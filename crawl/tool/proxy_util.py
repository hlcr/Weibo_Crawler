import requests
import threading
import time
import random


# 文件互斥锁
mutex = threading.Lock()
download_proxy_path = "./config/download_proxy_list.txt"
proxy_path = "./config/proxy_list.txt"


# 下载代理
def download_proxy():
    result_list = []
    url = "http://dev.kuaidaili.com/api/getproxy/?orderid=938136466707541&num=200&area=%E4%B8%AD%E5%9B%BD&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_ha=1&sp1=1&sep=3"
    is_ok = False
    # 获取代理服务
    while not is_ok:
        try:
            r = requests.get(url)
            is_ok = True
            result = r.text
            result_list = result.split(r" ")
        except requests.exceptions.RequestException:
            time.sleep(0.5)
            is_ok = False

    with open(download_proxy_path, "r") as f:
        proxy_num = len(f.readlines())

    if proxy_num > 2000:
        with open(download_proxy_path, "w") as f:
            f.write("")

    with open(download_proxy_path, "a") as f:
        for ip_port in result_list:
            f.write(ip_port+"\n")

    # 等待获取互斥锁
    mutex.acquire()
    # 清空原有配置文件
    with open(proxy_path,"w") as f:
        f.write("")
    mutex.release()

    with open(download_proxy_path, "r") as f:
        ip_address_set = set(f.readlines())


    # 验证每个ip可用性
    for ip in ip_address_set:
        ip = ip.strip()
        t = threading.Thread(target=is_valid, args=(ip,))
        t.setDaemon(True)
        t.start()


# 随机获取一个代理地址
def get_proxy():
    proxies = dict()
    proxy_list = []
    while not proxy_list:
        mutex.acquire()
        with open(proxy_path, "r") as f:
            proxy_list = f.readlines()
        mutex.release()

    index = random.randint(0, len(proxy_list)-1)
    ip_port = proxy_list[index].strip()
    # 移除已经用了的ip
    proxy_list.remove(proxy_list[index])
    mutex.acquire()
    with open(proxy_path,"w") as f:
        for item in proxy_list:
            f.write(item)
    proxies['http'] = "http://" + ip_port
    mutex.release()
    return proxies

def WhatIsmyIp(proxies):
    url = "http://ip.chinaz.com/getip.aspx"
    req_head = {'Host': 'ip.chinaz.com', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
     'Accept-Encoding': 'gzip, deflate, sdch', 'Upgrade-Insecure-Requests': '1',
     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
     'Connection': 'keep-alive', 'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2'}
    try:
        r = requests.get(url, headers=req_head, proxies=proxies, timeout=5).text
    except requests.Timeout:
        return None
    except:
        return None
    try:
        r_ip = r.split("'")[1]
    except:
        # print(r)
        return None
    return r_ip

def is_ok(proxies):
    url = "http://s.weibo.com"
    req_head = {'Host': 's.weibo.com', 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
     'Accept-Encoding': "gzip, deflate", 'Upgrade-Insecure-Requests': '1',
     'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
     'Connection': 'keep-alive', 'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2',"DNT":"1"}
    try:
        r = requests.get(url, headers=req_head, proxies=proxies, timeout=5).text
        if "微博搜索" in r:
            return True
    except requests.Timeout:
        return False
    except:
        return False
    return False


# 判断是否可用于微博请求
def is_valid(ip_port):
    proxies = {
        "http": "http://" + ip_port
    }
    t_ip = WhatIsmyIp(proxies)
    # 验证是否匿名
    if t_ip == ip_port.split(":")[0]:
        # 验证是否能够访问微博
        if not is_ok(proxies):
            return False
        mutex.acquire()
        with open(proxy_path,"a") as f:
            f.write(ip_port+"\n")
        mutex.release()
        return True
    else:
        return False


# def process_download_proxy(file_path=None):
#     # with open(file_path, "r") as f:
#     with open("record.txt", "r") as f:
#         ip_list = f.readlines()
#     for ip in ip_list:
#         ip = ip.strip()
#         t = threading.Thread(target=is_valid, args=(ip,))
#         t.setDaemon(True)
#         t.start()


# print(is_valid("115.203.124.80:8998"))

# download_proxy()
#
# while not threading.activeCount() == 1:
#     time.sleep(2)
#     print(threading.activeCount())

# print(get_proxy())



