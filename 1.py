# -*- coding:utf-8 -*-
import requests, math
import gevent
from gevent.queue import Queue
from gevent import monkey;
from pyquery import PyQuery


def fetch_urls(queue, num):
    s = requests.Session()
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Referer': 'http://www.kuaidaili.com/'
    }
    result_arr = [] #结果列表
    while not queue.empty():
        url = queue.get()
        print("【" + url + "】")
        html = s.get(url, headers = headers).text
        pq = PyQuery(html)
        #print(pq)
        size = (pq.find('tbody tr').size())
        print(size)

        for index in range(15):
            print(index)
            item = pq.find('tbody tr').eq(index)
            
            ip = item.find('td').eq(0).text()
            port = item.find('td').eq(1).text()
            _type = item.find('td').eq(3).text()
            result_arr.append(
            {
                str(_type).lower():'{0}://{1}:{2}'.format(str(_type).lower(), ip, port)
            }
            )
            if len(result_arr) >= num:
                print(result_arr)
                break
            
def get_proxies(num, types):
    domestic_gn_url = 'http://www.kuaidaili.com/free/inha/{0}/' #国内高匿代理
    domestic_pt_url = 'http://www.kuaidaili.com/free/intr/{0}/' #国内普通代理
    abroad_gn_url = 'http://www.kuaidaili.com/free/outha/{0}/'  #国外高匿代理
    abroad_pt_url = 'http://www.kuaidaili.com/free/outtr/{0}/'  #国外普通代理
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
    
    
