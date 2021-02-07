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

def downloadVideo(animeName,episode):

   result_name = []
   result_links = []

   url = 'https://gogoanime.sh/'+animeName+'-'+'episode-'+str(episode)
   hdr = {'User-Agent': 'Mozilla/5.0'}
   req = Request(url,headers=hdr)
   page = urlopen(req)
   soup = BeautifulSoup(page,'lxml')

   downloadLinkContainer = soup.findAll('div',{'class':'favorites_book'})
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

   fileName = animeName + " "  + str(episode) + ".mp4"
   with progessBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
      urllib.request.urlretrieve(result_links[0],fileName,reporthook=t.update_to) 

#@NOTE: animeName should contain - instead of space

#animeName -> name of anime you wanna download
#start -> starting episode
#stop  -> ending episode
def startDownload(animeName,start,stop):
   all_threads = []
   _queue = queue.Queue()
   if start == stop:
      downloadVideo(animeName,start)
   else:
      for i in range(start,stop+1):
         t = Thread(target=downloadVideo,args=(animeName,i))
         t.start()
         all_threads.append(t)

startDownload('gintama',252,252)