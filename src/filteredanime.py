import sys,re,webbrowser,json,requests,os
import urllib
import queue

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import parse_qs
from threading import Thread
from tqdm import tqdm
from colorama import init , Fore , Style , Back

class progessBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

#download video from 4Anime 1080p
#@NOTE//BUG: Can't download more then 2 at once
def downloadFrom4Anime(animeName,episode):
   url = 'https://4anime.to/anime/'+animeName
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = None
   try:
      page = urlopen(req)
   except:
      return False
   soup = BeautifulSoup(page,'lxml')

   divContainer = soup.findAll('div',{'class':'server row'})
   innerDivContainer = divContainer[0].findAll('div')
   ulContainer = innerDivContainer[0].findAll('ul')
   liContainer = ulContainer[0].findAll('li')
   
   episodePageLink = liContainer[episode-1].findAll('a')[0]['href']

   #OPENING A NEW LINK

   url = episodePageLink
   req = Request(url,headers=hdr)
   page = None
   try:
      page = urlopen(req)
   except:
      return False
   soup = BeautifulSoup(page,'lxml')

   divContainer = soup.findAll('div',{'class':'mirror-footer cl'})
   scriptContainer = divContainer[0].find_all('script')
   scriptText = scriptContainer[0].string

   scriptText = scriptText.replace(' ','')
   start = scriptText.find('href=') + 3
   end = scriptText.find('">',start)
   extracted = scriptText[start+4:end-1]
   
   return extracted
 
#download videos from gogoanime 360,480,720p
def downloadFromGogoAnime(animeName,episode,quality,queue):

   if quality == 'uh':
      
      url = downloadFrom4Anime(animeName,int(episode))
      if queue is not None:
         queue.put(url)
      
      fileName = animeName + " "  + str(episode) + " [1080p].mp4"
      fullFileName = os.path.join(animeName,fileName)
      
      #download
      with progessBar(unit="B",unit_scale=True,miniters=1,desc=url.split('/')[-1]) as t:
         urllib.request.urlretrieve(url,fullFileName,reporthook=t.update_to)   

      return True

   result_name = []
   result_links = []
   
   url = 'https://gogoanime.sh/'+animeName+'-'+'episode-'+str(episode)
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = None
   try:
      page = urlopen(req)
   except:
      return False
   soup = BeautifulSoup(page,'lxml')

   downloadLinkContainer = soup.findAll('div',{'class':'favorites_book'})

   if len(downloadLinkContainer) == 0:
      return False

   ulContainer = downloadLinkContainer[0].findAll('ul')
   liContainer = ulContainer[0].findAll('li',{'class':'dowloads'})
   aContainer = liContainer[0].find('a')
   downloadPageLink = aContainer['href']
   
   req = Request(downloadPageLink,headers=hdr)
   page = None
   try:
      page = urlopen(req)
   except:
      return False
   soup = BeautifulSoup(page,'lxml')

   container = soup.findAll('div',{'class':'mirror_link'})
   downloadLinkContainer = container[0].findAll('div',{'class':'dowload'})
   
   for dlink in downloadLinkContainer:
      link = dlink.findAll('a')
      name = link[0].text
      name = name.replace('Download','')
      name = name.replace(" ",'')
      downloadLink = link[0]['href']
      result_name.append(name)
      result_links.append(downloadLink)

   fileName = animeName + " "  + str(episode)  
   fullFileName = ' '
   idx = -1   

   #Sorting out the Quality Control if one quality is not found
   #Download the quality as to priority
   #LOW 360P
   if quality == 'l':
      idx,fullFileName = checkIfResolution(animeName,'\n(360P-mp4)',result_name,idx,fileName,fullFileName)
      #First priority => 480P
      if idx == None:
         idx,fullFileName = checkIfResolution(animeName,'\n(480P-mp4)',result_name,idx,fileName,fullFileName)
         #Second priority => 720P
         if idx == None:
            idx,fullFileName = checkIfResolution(animeName,'\n(720P-mp4)',result_name,idx,fileName,fullFileName)
            if idx == None:
               print('no quality available')  
               return False
   #MEDIUM 480P
   elif quality == 'm':
      idx,fullFileName = checkIfResolution(animeName,'\n(480P-mp4)',result_name,idx,fileName,fullFileName)
      #First priority => 720P
      if idx == None:
         idx,fullFileName = checkIfResolution(animeName,'\n(720P-mp4)',result_name,idx,fileName,fullFileName)
         #Second priority => 360P
         if idx == None:
            idx,fullFileName = checkIfResolution(animeName,'\n(360P-mp4)',result_name,idx,fileName,fullFileName)
            if idx == None:
               print('no quality available')  
               return False
   #HIGH 720P
   elif quality == 'h':
      idx,fullFileName = checkIfResolution(animeName,'\n(720P-mp4)',result_name,idx,fileName,fullFileName)
      #First priority => 480P
      if idx == None:
         idx,fullFileName = checkIfResolution(animeName,'\n(480P-mp4)',result_name,idx,fileName,fullFileName)
         #Second priority => 360P
         if idx == None:
            idx,fullFileName = checkIfResolution(animeName,'\n(360P-mp4)',result_name,idx,fileName,fullFileName)
            if idx == None:
               print('no quality available')  
               return False
   
   #put this in queue to track thread related stuff
   if queue is not None:
      queue.put(result_links[idx])
   
   #download
   with progessBar(unit="B",unit_scale=True,miniters=1,desc=url.split('/')[-1]) as t:
      urllib.request.urlretrieve(result_links[idx],fullFileName,reporthook=t.update_to)   

   return True

def checkIfResolution(animeName,qualityString,resultName,idx,fileName,fullFileName):
   result = []
   if qualityString in resultName:
      idx = resultName.index(qualityString)
      if qualityString == '\n(720P-mp4)':
         fileName += " [720P].mp4"
      elif qualityString == '\n(480P-mp4)':
         fileName += " [480P].mp4"
      else:
         fileName += " [360P].mp4"
      fullFileName = os.path.join(animeName,fileName)
      return idx,fullFileName
   return None,None

#Give suggestions based on animename
def searchAnimeSuggestions(animeName):
   animeName = animeName.replace('-','%20')
   url = 'https://gogoanime.sh//search.html?keyword=' + animeName
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = urlopen(req)
   soup = BeautifulSoup(page,'lxml')

   listContainer = soup.findAll('div',{'class':'last_episodes'})
   ulContainer = listContainer[0].findAll('ul')
   liContainer = ulContainer[0].findAll('li')

   if len(liContainer) == 0:
      print(Fore.RED + "(ERROR) "+ Style.RESET_ALL + "Could not even find suggestions :(")
      return False

   print(Back.MAGENTA + "\n Could not find anime .. so giving suggestions .." + Style.RESET_ALL)
   print("")
   count = 1
   for li in liContainer:
      pContainer = li.findAll('p')
      rawSEOname = pContainer[0].find('a')['href']
      title = pContainer[0].find('a')['title']
      rawSEOname = rawSEOname.replace('/category/','')
      print(str(count) + " : " + title + "   [ " + Fore.MAGENTA + rawSEOname + Style.RESET_ALL+" ]")
      count += 1
   return True

#Get Anime Info
def getAnimeInfo(animeName):
   url = 'https://gogoanime.sh//category/' + animeName
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = None
   try:
      page = urlopen(req)
   except:
      return False
   soup = BeautifulSoup(page,'lxml')

   divContainer = soup.findAll('div',{'class':'anime_video_body'})

   if len(divContainer) == 0:
      return False

   #Retrieving episode count
   ulContainer = divContainer[0].findAll('ul')   
   totalEpisodeCount = 0
   aContainer = []
   for li in ulContainer:
      aContainer = li.findAll('a') #[0]['ep_end']   
   totalEpisodeCount = aContainer[len(aContainer)-1]['ep_end']
   
   #Retriving Other anime info such as type,genre,releasedate,status
   divContainer = soup.findAll('div',{'class':'anime_info_body_bg'})
   pContainer = divContainer[0].findAll('p',{'class','type'}) 

   animeType = pContainer[0].findAll('a')[0]['title'] #type
   releasedate = pContainer[3].text #release date
   status = pContainer[4].findAll('a')[0].text #status

   #genres
   genres = []
   gList = pContainer[2].findAll('a')
   for g in gList:
      genres.append(g['title'])
   
   #printing
   print(Fore.YELLOW + "Anime: "+Style.RESET_ALL + animeName + Fore.YELLOW +"\nTotal Episodes: " + Style.RESET_ALL + totalEpisodeCount+Fore.YELLOW+"\nType: "+Style.RESET_ALL+ animeType + Fore.YELLOW+" \n" + releasedate + "\nStatus: "+Style.RESET_ALL + status)   

   return True

#@NOTE: animeName should contain - instead of space

#animeName -> name of anime you wanna download
#start -> starting episode
#stop  -> ending episode
def multiDownload(animeName,start,stop,quality):
   all_threads = []
   _queue = queue.Queue()
   for i in range(start,stop+1):
      t = Thread(target=downloadFromGogoAnime,args=(animeName,i,quality,_queue))
      t.start()
      all_threads.append(t)

   #means there was an error in the function
   #that the queue is empty
   if _queue.empty():
      t.join()
      return False
   return True

#Save the downloaded files in their respective folders
def makeFolderIfNotCreate(animeName):
   if os.path.exists(animeName) == False:
      os.mkdir(animeName)

if __name__ == '__main__':
   argLength = len(sys.argv)-1
   if argLength == 4:
      if ((sys.argv[4] != 'l') and (sys.argv[4] != 'm') and (sys.argv[4] != 'h') and (sys.argv[4] != 'uh')) or (sys.argv[2].isdigit() == False) or (sys.argv[3].isdigit() == False) or (int(sys.argv[2]) > int(sys.argv[3])) or (int(sys.argv[2]) == int(sys.argv[3])):
         print(Fore.RED + 'invalid arguments: '+ Style.RESET_ALL  +' Check your Parameters')
      else:
         makeFolderIfNotCreate(sys.argv[1]) #make directory
         if multiDownload(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]) == False:
            os.rmdir(sys.argv[1]) #remove directory
            searchAnimeSuggestions(sys.argv[1]) #search for suggestions
   elif argLength == 3:
      if ((sys.argv[3] != 'l') and (sys.argv[3] != 'm') and (sys.argv[3] != 'h') and (sys.argv[3] != 'uh')) or (sys.argv[2].isdigit() == False):
         print(Fore.RED + 'invalid arguments: '+ Style.RESET_ALL  +' Check your Parameters')
      else:
         makeFolderIfNotCreate(sys.argv[1])
         if downloadFromGogoAnime(sys.argv[1],sys.argv[2],sys.argv[3],None) == False:
            os.rmdir(sys.argv[1]) #remove directory
            searchAnimeSuggestions(sys.argv[1])
   elif argLength == 2:
      if(sys.argv[2] != 'info'):
         print(Fore.RED + 'invalid arguments: '+ Style.RESET_ALL  +' Check your Parameters')
      else:
         if getAnimeInfo(sys.argv[1]) == False:
            searchAnimeSuggestions(sys.argv[1])
   else:
      print(Fore.RED + 'invalid arguments: '+ Style.RESET_ALL  +' Check your Parameters')