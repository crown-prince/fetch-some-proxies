# -*- coding:utf-8 -*-
import requests, math
import gevent
from gevent.queue import Queue
from gevent import monkey;
from pyquery import PyQuery
import urllib.request
from bs4 import BeautifulSoup
import os

def write(data):
   f = open("proxies_data.txt", "a")
   f.write(data)
        
def fetch_urls(queue, num):
    s = requests.Session()
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
            
    }
    result = [] #结果列表
    
    while not queue.empty():
        url = queue.get()
        #print("【" + url + "】")
        
        req = urllib.request.Request(url, headers = headers)
        resp = urllib.request.urlopen(req) #data=urllib.request.urlopen(url).read()  
        pq = (resp.read()).decode("gb2312")
        #print(pq)

        soup = BeautifulSoup(pq, "html.parser")
        items = soup.find_all("tbody") #find_all 函数返回的是一个序列，可以对它进行循环，依次得到想到的东西
        #print(items)
        _soup = BeautifulSoup(str(items), "html.parser")
        for idx, tr in enumerate(_soup.find_all('tr')):
            tds = tr.find_all('td')
            ip =  tds[0].contents[0]
            port = tds[1].contents[0]
            _type = tds[3].contents[0]
            result.append({
                '{0}:{1}@{2}'.format(ip, port,_type)       
            })

   
    for i in result:
        print(i)
        write(str(i))
        
        
           
def get_proxies(num, types):
    domestic_gn_url = 'http://www.ip3366.net/free/?stype=1&page={0}' #国内高匿代理
    domestic_pt_url = 'http://www.ip3366.net/free/?stype=2&page={0}' #国内普通代理
    abroad_gn_url = 'http://www.ip3366.net/free/?stype=3&page={0}'  #国外高匿代理
    abroad_pt_url = 'http://www.ip3366.net/free/?stype=4&page={0}'  #国外普通代理
    url_queue = Queue()
    need_pages = int(math.ceil(num/15))
    if types == 1: # 国内高匿代理
        base_url = domestic_gn_url
    elif types == 2: # 国内普通代理
        base_url = domestic_pt_url
    elif types == 3: # 国外高匿代理
        base_url = abroad_gn_url
    elif types == 4: # 国外普通代理
        base_url = abroad_pt_url
    
    for i in range(need_pages):
        url = base_url.format(i+1)
        url_queue.put(url)
        
    #print(url_queue.get())
    #print(url_queue.get())
    
    gevent_list = []
    for i in range(2):
        gevent_list.append(
            gevent.spawn(fetch_urls, url_queue, num)
        )
    gevent.joinall(gevent_list)
    
    

def main():
    get_proxies(50, 1)
    
if __name__ == "__main__":
    main()
    
    
