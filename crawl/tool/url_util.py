import requests
import time
from .proxy_util import *
import traceback



# get 请求
def get(url, req_head, proxy):
    is_ok = False
    while not is_ok:
        try:
            r = requests.get(url, headers=req_head, proxies=proxy, timeout=5)
            is_ok = process_result(r, proxy)
        except requests.exceptions.RequestException:
            time.sleep(0.5)
            is_ok = False
            proxy.clear()
            proxy["http"] = get_proxy()["http"]
    return r


def post(url, data_dict, req_head, proxy):
    is_ok = False
    while not is_ok:
        try:
            r = requests.post(url, data=data_dict, headers=req_head, timeout=10)
            # r = requests.post(url, data=data_dict, headers=req_head, proxies=proxy, timeout=10)
            is_ok = process_result(r, proxy)
        except requests.exceptions.RequestException:
            traceback.print_exc()
            time.sleep(0.5)
            is_ok = False
            proxy.clear()
            proxy["http"] = get_proxy()["http"]
    return r


def process_result(c_respone, proxy):
    html = c_respone.text
    if 'Maximum number of open connections reached.' in html:
        pass
    elif c_respone.status_code != 200:
        pass
    else:
        return True
    proxy.clear()
    proxy["http"] = get_proxy()["http"]
    return False

