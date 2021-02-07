import sys,re,webbrowser,json,requests,os
import urllib
import queue

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import parse_qs
from threading import Thread
from tqdm import tqdm

class progessBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

#download videos
def downloadVideo(animeName,episode,quality,queue):

   result_name = []
   result_links = []

   url = 'https://gogoanime.sh/'+animeName+'-'+'episode-'+str(episode)
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = urlopen(req)
   soup = BeautifulSoup(page,'lxml')

   downloadLinkContainer = soup.findAll('div',{'class':'favorites_book'})

   if len(downloadLinkContainer) == 0:
      return False

   ulContainer = downloadLinkContainer[0].findAll('ul')
   liContainer = ulContainer[0].findAll('li',{'class':'dowloads'})
   aContainer = liContainer[0].find('a')
   downloadPageLink = aContainer['href']
   
   req = Request(downloadPageLink,headers=hdr)
   page = urlopen(req)
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
   if quality == 'l':

      #if 360p download
      if '\n(360P-mp4)' in result_name:
         idx = result_name.index('\n(360P-mp4)')
         fileName += " [360P].mp4"
         fullFileName = os.path.join(animeName,fileName)

      #if not download other res
      else:

         #first priority to 480P
         if '\n(480P-mp4)' in result_name:
            idx = result_name.index('\n(480P-mp4)')
            fileName += " [480P].mp4"
            fullFileName = os.path.join(animeName,fileName)

         #second priority
         elif '\n(720P-mp4)' in result_name:
            idx = result_name.index('\n(720P-mp4)')
            fileName += " [720P].mp4"
            fullFileName = os.path.join(animeName,fileName)
            
         else:
            print('no quality avail')

   #MEDIUM 480P
   elif quality == 'm':
 
      #if 480p then download
      if '\n(480P-mp4)' in result_name:
         idx = result_name.index('\n(480P-mp4)')
         fileName += " [480P].mp4"
         fullFileName = os.path.join(animeName,fileName)

      #if not download other res
      else:

         #first priority to 720p
         if '\n(720P-mp4)' in result_name:
            idx = result_name.index('\n(720P-mp4)')
            fileName += " [720P].mp4"
            fullFileName = os.path.join(animeName,fileName)

         #second priority
         elif '\n(360P-mp4)' in result_name:
            idx = result_name.index('\n(360P-mp4)')
            fileName += " [360P].mp4"
            fullFileName = os.path.join(animeName,fileName)
            
         else:
            print('no quality avail')

   #HIGH 720P
   else:

      #if 720P then download
      if '\n(720P-mp4)' in result_name:
         idx = result_name.index('\n(720P-mp4)')
         fileName += " [720P].mp4"
         fullFileName = os.path.join(animeName,fileName)

      #if not download other res
      else:

         #first priority to 480P
         if '\n(480P-mp4)' in result_name:
            idx = result_name.index('\n(480P-mp4)')
            fileName += " [480P].mp4"
            fullFileName = os.path.join(animeName,fileName)

         #second priority
         elif '\n(360P-mp4)' in result_name:
            idx = result_name.index('\n(360P-mp4)')
            fileName += " [360P].mp4"
            fullFileName = os.path.join(animeName,fileName)
            
         else:
            print('no quality avail')

   #put this in queue to track thread related stuff
   if queue is not None:
      queue.put(result_links[idx])
   
   #download
   with progessBar(unit="B",unit_scale=True,miniters=1,desc=url.split('/')[-1]) as t:
            urllib.request.urlretrieve(result_links[idx],fullFileName,reporthook=t.update_to)   

   return True

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

   print("\n Could not find anime .. so giving suggestions ..")
   print("")
   count = 1
   for li in liContainer:
      pContainer = li.findAll('p')
      rawSEOname = pContainer[0].find('a')['href']
      title = pContainer[0].find('a')['title']

      rawSEOname = rawSEOname.replace('/category/','')

      print(str(count) + " : " + title + "   [ " + rawSEOname + " ]")
      count += 1

#@NOTE: animeName should contain - instead of space

#animeName -> name of anime you wanna download
#start -> starting episode
#stop  -> ending episode
def multiDownload(animeName,start,stop,quality):
   all_threads = []
   _queue = queue.Queue()
   for i in range(start,stop+1):
      t = Thread(target=downloadVideo,args=(animeName,i,quality,_queue))
      t.start()
      all_threads.append(t)

   #means there was an error in the function
   #that the queue is empty
   if _queue.empty():
      t.join()
      return False
   return True

#COMMANDS

#1. python filteredanime [anime] [startEpisode] [stopEpisode] [quality] //BULK
#2. python filteredanime [anime] [episode] [quality] //SINGLE EPISODE

#quality modes 

  # l => low => 360p
  # m => medium => 480p
  # h => high => 720p

#Example : python filteredanime gintama 245 250 h => will download anime gintama from episode 245 to 250 in HIGH [720P] 

#Save the downloaded files in their respective folders
def makeFolderIfNotCreate(animeName):
   if os.path.exists(animeName) == False:
      os.mkdir(animeName)

if __name__ == '__main__':
   argLength = len(sys.argv)-1
   if argLength == 4:
      if ((sys.argv[4] != 'l') and (sys.argv[4] != 'm') and (sys.argv[4] != 'h')) or (sys.argv[2].isdigit() == False) or (sys.argv[3].isdigit() == False) or (int(sys.argv[2]) > int(sys.argv[3])) or (int(sys.argv[2]) == int(sys.argv[3])):
         print('invalid arguments: check params')
      else:
         makeFolderIfNotCreate(sys.argv[1])
         if multiDownload(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]) == False:
            os.rmdir(sys.argv[1]) #remove directory
            searchAnimeSuggestions(sys.argv[1]) #search for suggestions
   elif argLength == 3:
      if ((sys.argv[3] != 'l') and (sys.argv[3] != 'm') and (sys.argv[3] != 'h')) or (sys.argv[2].isdigit() == False):
         print('invalid arguments: check params')
      else:
         makeFolderIfNotCreate(sys.argv[1])
         if downloadVideo(sys.argv[1],sys.argv[2],sys.argv[3],None) == False:
            os.rmdir(sys.argv[1]) #remove directory
            searchAnimeSuggestions(sys.argv[1])
   else:
      print('invalid arguments: check params')