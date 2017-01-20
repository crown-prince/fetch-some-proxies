import urllib.request
from bs4 import BeautifulSoup
import os

def write(data):
    if os.path.isfile("proxies_data.txt"):
        print("Unable to write to file")
    else:
        f = open("proxies_data.txt", "w")
        f.write(data)
        
def main():
    #提取网页源码
    url = "http://ip.zdaye.com/dayProxy/ip/920.html"
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; rv:47.0) Gecko/20100101 Firefox/47.0",}
    req = urllib.request.Request(url, headers = headers)
    resp = urllib.request.urlopen(req) #data=urllib.request.urlopen(url).read()  
    respHtml = (resp.read()).decode("gb2312")
    #print(respHtml)

    soup = BeautifulSoup(respHtml, "html.parser")
    items = soup.find_all("div", "cont")
    #print(items)
    for item in items:
        link = item.find('br').get_text() 
        print(link + "\n")
        write(link)
if __name__ == "__main__":
    main()
