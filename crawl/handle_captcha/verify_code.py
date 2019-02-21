import requests
import binascii
import time
import json
from crawl.MyError import *
from crawl.tool.url_util import *


# 初始化一个打码的类别
class Chaoren():
    def __init__(self):
        self.s = requests.Session()
        self.s.encoding = 'utf-8'
        self.data = {
            'username': '',
            'password': '',
            'softid': '3696',  # 修改为自己的软件id
            'imgid': '',
            'imgdata': ''
        }

    # 获取剩余点数
    def get_left_point(self):
        try:
            r = self.s.post('http://api2.sz789.net:88/GetUserInfo.ashx', self.data)
            return r.json()
        except requests.ConnectionError:
            return self.get_left_point()
        except:
            return False

    # 识别图片字节流
    def recv_byte(self, imgdata):
        self.data['imgdata'] = binascii.b2a_hex(imgdata).upper()
        try:
            r = self.s.post('http://api2.sz789.net:88/RecvByte.ashx', self.data)
            res = r.json()
            if res[u'info'] == -1:
                return False
            return r.json()
        except requests.ConnectionError:
            return self.recv_byte(imgdata)
        except:
            return False

    # 报告错误
    def report_err(self, imgid):
        self.data['imgid'] = imgid
        if self.data['imgdata']:
            del self.data['imgdata']
        try:
            r = self.s.post('http://api2.sz789.net:88/ReportError.ashx', self.data)
            return r.json()
        except requests.ConnectionError:
            return self.report_err(imgid)
        except:
            return False


# 自动打码
def verify_code(cookie_dict, refer_url, pin_url, proxy):
    Pic_Cookie = "login_sid_t={0}; _s_tentry={1}; Apache={2}; SINAGLOBAL={3}; ULV={4}; SWB={5}; SCF={6}; SUB={7}; SUBP={8}; SUHB={9}; ALF={10}; SSOLoginState={11}; un={12}; wvr={13}; WBStorage={14}".format(
        cookie_dict["login_sid_t"], cookie_dict["_s_tentry"], cookie_dict["Apache"], cookie_dict["SINAGLOBAL"],
        cookie_dict["ULV"], cookie_dict["SWB"], cookie_dict["SCF"], cookie_dict["SUB"], cookie_dict["SUBP"],
        cookie_dict["SUHB"], cookie_dict["ALF"], cookie_dict["SSOLoginState"], cookie_dict["un"], cookie_dict["wvr"],
        cookie_dict["WBStorage"])

    # if 'ULOGIN_IMG' in cookie_dict:
    #     Pic_Cookie = Pic_Cookie+'; ULOGIN_IMG='+cookie_dict['ULOGIN_IMG']
    # 获取验证码图片
    req_head = {'Accept-Encoding': 'gzip, deflate, sdch',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Referer': refer_url,
                'Accept': 'image/webp,image/*,*/*;q=0.8', 'Cache-Control': 'max-age=0',
                'Cookie': Pic_Cookie,
                'Accept-Language': 'zh-CN,zh;q=0.8', 'Connection': 'keep-alive', 'Host': 's.weibo.com'}

    # url = "http://s.weibo.com/ajax/pincode/pin?type=sass" + str(int(time.time() * 10000))
    # url = "http://s.weibo.com/ajax/pincode/pin?type=sass&ts=" + str(int(time.time()))
    # 请求图片
    r = get(pin_url, req_head, proxy)
    cookie = r.headers['Set-Cookie']

    if 'ULOGIN_IMG' not in cookie:
        with open('qiguai.html',"w") as f:
            f.write(r.text)
        raise MyError(cookie)
    cookie = cookie.replace(" domain=weibo.com; path=/, ", "").replace("; path=/", "")
    items = cookie.split(";")
    # 添加对应的请求头
    for item in items:
        if "=" in item:
            key, value = item.split("=")
            cookie_dict[key] = value

    # 初始化打码程序
    client = Chaoren()
    client.data['username'] = 'XXX'  # 修改为打码账号
    client.data['password'] = 'XXXX'  # 修改为打码密码
    res = client.recv_byte(r.content)  # 获取验证码识别结果
    if type(res) == type(False):
        raise MyError("验证码出错")
    # 保存识别结果
    with open("./code/" + res[u'result'] + ".png", "wb") as f:
        f.write(r.content)

    time.sleep(1.5)

    # 提交识别结果
    # Cookie = "SWB={0}; WBStorage={1}; _s_tentry={2}; Apache={3}; SINAGLOBAL={4}; ULV={5}; ULOGIN_IMG={6}".format(
    #     cookie_dict['SWB'], cookie_dict['WBStorage'], cookie_dict['_s_tentry'], cookie_dict['Apache'],
    #     cookie_dict['SINAGLOBAL'], cookie_dict['ULV'], cookie_dict['ULOGIN_IMG'])
    Cookie = "login_sid_t={0}; _s_tentry={1}; Apache={2}; SINAGLOBAL={3}; ULV={4}; SWB={5}; SCF={6}; SUB={7}; SUBP={8}; SUHB={9}; ALF={10}; SSOLoginState={11}; un={12}; wvr={13}; WBStorage={14}; ULOGIN_IMG={15}".format(
        cookie_dict['login_sid_t'], cookie_dict['_s_tentry'], cookie_dict['Apache'], cookie_dict['SINAGLOBAL'],
        cookie_dict['ULV'], cookie_dict['SWB'],
        cookie_dict['SCF'], cookie_dict['SUB'], cookie_dict['SUBP'], cookie_dict['SUHB'], cookie_dict['ALF'],
        cookie_dict['SSOLoginState'],
        cookie_dict['un'], cookie_dict['wvr'], cookie_dict['WBStorage'], cookie_dict['ULOGIN_IMG'])
    rnd = str(int(time.time() * 1000))

    url = "http://s.weibo.com/ajax/pincode/verified?__rnd=" + rnd
    req_head = {'Host': 's.weibo.com',
                'Connection': 'keep-alive',
                'Content-Length': '39',
                'Origin': 'http://s.weibo.com',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*',
                'Cookie': Cookie,
                'Accept-Encoding': 'gzip, deflate',
                'Referer': refer_url,
                'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2'}
    data_dict = {'_t': "0'", 'type': 'sass', 'secode': res[u'result'], 'pageid': 'weibo'}
    # 提交打码post
    r = post(url, data_dict, req_head, proxy)

    # 判断结果是否准确
    k = json.loads(r.text)
    if int(k.get("code")) == 100000:
        print("success_code")
        return True
    else:
        client.report_err(res[u'imgId'])
        print("error_code")
        return False

# if __name__ == '__main__':
#     cookie_dict = {'WBStorage': '2c466cc84b6dda21|undefined',
#                    'ULV': '1481277807542:1:1:1:9804109628703.14.1481277807535:', '_s_tentry': '-',
#                    'SINAGLOBAL': '9804109628703.14.1481277807535', 'Apache': '9804109628703.14.1481277807535'}
#     verify_code(cookie_dict)
