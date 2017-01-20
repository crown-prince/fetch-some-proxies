#!/usr/bin/env python

import sys

if sys.version_info.major > 2:
    exit("[!] please run this program with Python v2.x")

import json
import os
import Queue
import random
import re
import string
import subprocess #subprocess包主要功能是执行外部的命令和程序
import tempfile
import threading
import time
import urllib2

VERSION = "2.1"
BANNER = """
+-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-+
|f||e||t||c||h||-||s||o||m||e||-||p||r||o||x||i||e||s| <- v%s
+-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-++-+""".strip("\r\n") % VERSION

TIMEOUT = 10
IFCONFIG_URL = "http://ipecho.net/plain" #发现本机IP
USER_AGENT = "curl/7.{curl_minor}.{curl_revision} (x86_64-pc-linux-gnu) libcurl/7.{curl_minor}.{curl_revision} OpenSSL/0.9.8{openssl_revision} zlib/1.2.{zlib_revision}".format(curl_minor=random.randint(8, 22), curl_revision=random.randint(1, 9), openssl_revision=random.choice(string.lowercase), zlib_revision=random.randint(2, 6))

FALLBACK_METHOD = False

PROXY_LIST_URL = "https://hidester.com/proxydata/php/data.php?mykey=csv&gproxy=2" #代理列表
ROTATION_CHARS = ('/', '-', '\\', '|')

THREADS = 10

ANONIMITY_LEVELS = {"elite": "high", "anonymous": "medium", "transparent": "low"}

if not subprocess.mswindows:
    BANNER = re.sub(r"\|(\w)\|", lambda _: "|\033[01;41m%s\033[00;49m|" % _.group(1), BANNER)

counter = [0]
threads = []

def retrieve(url, data=None, headers={"User-agent": USER_AGENT}):
    try:
        req = urllib2.Request("".join(url[i].replace(' ', "%20") if i > url.find('?') else url[i] for i in xrange(len(url))), data, headers)
        retval = urllib2.urlopen(req, timeout=TIMEOUT).read()
    except Exception as ex:
        try:
            retval = ex.read() if hasattr(ex, "read") else getattr(ex, "msg", str())
        except:
            retval = None

    return retval or ""

def worker(queue, handle=None):
    try:
        while True:
            proxy = queue.get_nowait()
            result = ""
            counter[0] += 1
            sys.stdout.write("\r%s\r" % ROTATION_CHARS[counter[0] % len(ROTATION_CHARS)])
            sys.stdout.flush()
            start = time.time()
            candidate = "%s://%s:%s" % (proxy["type"], proxy["IP"], proxy["PORT"])
            if not all((proxy["IP"], proxy["PORT"])) or re.search(r"[^:/\w.]", candidate):
                continue
            if not FALLBACK_METHOD:
                process = subprocess.Popen("curl -m %d -A '%s' --proxy %s %s" % (TIMEOUT, USER_AGENT, candidate, IFCONFIG_URL), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result, _ = process.communicate()
            elif proxy["type"] in ("http", "https"):
                opener = urllib2.build_opener(urllib2.ProxyHandler({"http": candidate, "https": candidate}))
                urllib2.install_opener(opener)
                result = retrieve(IFCONFIG_URL)
            if (result or "").strip() == proxy["IP"].encode("utf8"):
                latency = time.time() - start
                if latency < TIMEOUT:
                    if handle:
                        handle.write("%s%s" % (candidate, os.linesep))
                        handle.flush()
                    sys.stdout.write("\r%s%s # latency: %.2f sec; country: %s; anonimity: %s (%s)\n" % (candidate, " " * (32 - len(candidate)), latency, ' '.join(_.capitalize() for _ in (proxy["country"].lower() or '-').split(' ')), proxy["anonymity"].lower() or '-', ANONIMITY_LEVELS.get(proxy["anonymity"].lower(), '-')))
                    sys.stdout.flush()
    except Queue.Empty:
        pass

def main():
    global FALLBACK_METHOD #疑问

    sys.stdout.write("%s\n\n" % BANNER)
    sys.stdout.write("[i] initial testing...\n")

    """
    给运行的命令提供输入或者读取命令的输出，判断该命令的运行状态，管理多个命令的并行等等。
    这时subprocess中的Popen命令就能有效的完成我们需要的操作
    """
    process = subprocess.Popen("curl -m %d -A '%s' %s" % (TIMEOUT, USER_AGENT, IFCONFIG_URL), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    """
    如果参数shell设为true，程序将通过shell来执行
    stdin stdout和stderr，分别表示子程序的标准输入、标准输出和标准错误。可选的值有PIPE或者一个有效的文件描述符（其实是个正整数）
    或者一个文件对象，还有None。如果是PIPE，则表示需要创建一个新的管道，如果是None，不会做任何重定向工作，子进程的文件描述符会继承父进程的。另外，stderr的值还可以是STDOUT
    ，表示子进程的标准错误也输出到标准输出

    """
    stdout, _ = process.communicate()
    FALLBACK_METHOD = re.search(r"\d+\.\d+\.\d+\.\d+", stdout or "") is None

    sys.stdout.write("[i] retrieving list of proxies...\n")
    try:
        proxies = json.loads(retrieve(PROXY_LIST_URL))
    except:
        exit("[!] something went wrong during the proxy list retrieval/parsing. Please check your network settings and try again")
    random.shuffle(proxies) #shuffle() 方法将序列的所有元素随机排序

    _, filepath = tempfile.mkstemp(prefix="proxies", suffix=".txt") # “_”，“filepath"分别是变量名

    """
    应用程序经常要保存一些临时的信息，这些信息不是特别重要，没有必要写在配置文件里，但又不能没有，这时候就可以把这些信息写到临时文件里。
    其实很多程序在运行的时候，都会产生一大堆临时文件，有些用于保存日志，有些用于保存一些临时数据，还有一些保存一些无关紧要的设置
    """

    """
    tempfile.mkstemp([suffix=”[, prefix=’tmp'[, dir=None[, text=False]]]]), 仅用于创建临时文件,参数suffix和prefix分别表示临时文件名称的后缀和前缀
    """
    os.close(_)
    handle = open(filepath, "w+b") #w+: 可读可写，若文件不存在，创建；b表示二进制 #疑问

    sys.stdout.write("[i] storing results to '%s'...\n" % filepath)
    #以上代码获取了代理列表
    #以下代码
    queue = Queue.Queue()
    for proxy in proxies:
        queue.put(proxy)

    sys.stdout.write("[i] testing %d proxies (%d threads)...\n\n" % (len(proxies), THREADS))
    for _ in xrange(THREADS):
        thread = threading.Thread(target=worker, args=[queue, handle])
        thread.daemon = True

        try:
            thread.start()
        except ThreadError as ex:
            sys.stderr.write("[x] error occurred while starting new thread ('%s')" % ex.message)
            break

        threads.append(thread)

    try:
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.isAlive():
                    alive = True
                    time.sleep(0.1)
    except KeyboardInterrupt: #用户中断的异常
        sys.stderr.write("\r   \n[!] Ctrl-C pressed\n")
    else:
        sys.stdout.write("\n[i] done\n")
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        handle.flush()
        handle.close()

if __name__ == "__main__":
    main()
