from crawl.tool import util as my_util
from crawl.handle_captcha import verify_code
from crawl.db_handler import executeSQL
from lxml import etree
from crawl.tool.url_util import *
from crawl.my_browser import *
from crawl.tool.proxy_util import *
from crawl.db_handler.handle_db import *


# 获取已经登录的cookie列表
def get_cookie_list():
    cookie_list = []
    with open("cookie", "r") as f:
        cookie_list = f.readlines()
    return cookie_list


# 把cookie转换为dict
def convert_cookie(cookie_list):
    result_list = []
    for cookie in cookie_list:
        cookie_dict = dict()
        cookie = json.loads(cookie)
        for item in cookie:
            cookie_dict[item["name"]] = item["value"]
        result_list.append(cookie_dict)
    return result_list





# 根据提供的html识别出最大页数
def get_max_page(html):
    max_page = 1
    p_list = re.findall(r"第(\d+)页", html)
    p_list = [int(p) for p in p_list]
    if p_list:
        max_page = max(p_list)
    return max_page


# 返回 0：成功
# 返回 1：无结果
# 返回 2：验证码
# 返回 3：VPN超过最大连接
# 返回 4: 强制跳转
# 返回 10：未知错误
def process_html(html,page,url):
    # 判断是否没有关键词信息
    n_index = html.find('noresult')
    # 强制加载页面，有验证码
    replace_index = html.find('location.replace')
    code_index = html.find(r'sassfilter.js')
    max_conn_index = html.find(r'Maximum number of open connections reached.')
    # 没有结果
    if n_index > 100:
        # print('no_result')
        return 1
    # 有验证码
    if code_index > 100:
        return 2
    if max_conn_index >= 0:
        return 3
    if replace_index > 100:
        return 4
    s_index = html.find(r'<div class="search_feed"')
    e_index = html.find(r'<!-- \/未登录提示 -->')
    if s_index > 100 and e_index > 100 and s_index < e_index:
        html = html[s_index:e_index + 34]
        html = html.replace(r'\/', r'/')
        # 转为xml
        xml = my_util.html2xml(html)
        root = xml.getroot()
        url_element = etree.Element("url")
        url_element.text = bytes(url, encoding='utf-8')
        root.insert(0, url_element)

        # html = r'<meta charset="utf-8">'+html
        xml_text = etree.tostring(root, pretty_print=True)
        executeSQL.process_xml(xml_text)
        # 写入文件
        # with open('./测试xml/result_xml'+str(page)+'.xml', 'wb') as f:
        #     f.write(xml)

            # html = html.replace(r'\"',r'"')
            # html = html.replace(r'\n',r'<br/>')
            # html = html.replace(r'\t',r'')
        return 0
    else:
        return 10


# 提交验证码
def submit_code(cookie_dict, cur_url, html, proxy, pin_url=None):
    # 处理为空
    if not pin_url:
        pp_url = get_code_url(html)
        if not pp_url:
            pp_url = str(int(time.time()))
        pin_url = 'http://s.weibo.com/ajax/pincode/pin?type=' + pp_url

    print("code_appear")
    is_ok = False
    # 验证码
    while not is_ok:
        try:
            code_result = verify_code.verify_code(cookie_dict, cur_url, pin_url, proxy)
            if not code_result:
                proxy = get_proxy()
            is_ok = True
        except MyError as me:
            print("不能获得合适cookie" + str(me))
            time.sleep(0.5)
            proxy["http"] = get_proxy()["http"]
            is_ok = False

def generate_cookie(cookie_dict):
    cookie = ""
    if 'login_sid_t' in cookie_dict:
        cookie = cookie + cookie_dict['login_sid_t'] + '; '

    if '_s_tentry' in cookie_dict:
        cookie = cookie + cookie_dict['_s_tentry'] + '; '

    if 'Apache' in cookie_dict:
        cookie = cookie + cookie_dict['Apache'] + '; '

    if 'SINAGLOBAL' in cookie_dict:
        cookie = cookie + cookie_dict['SINAGLOBAL'] + '; '

    if 'ULV' in cookie_dict:
        cookie = cookie + cookie_dict['ULV'] + '; '

    if 'SWB' in cookie_dict:
        cookie = cookie + cookie_dict['SWB'] + '; '

    if 'SCF' in cookie_dict:
        cookie = cookie + cookie_dict['SCF'] + '; '

    if 'SUB' in cookie_dict:
        cookie = cookie + cookie_dict['SUB'] + '; '

    if 'SUBP' in cookie_dict:
        cookie = cookie + cookie_dict['SUBP'] + '; '

    if 'SUHB' in cookie_dict:
        cookie = cookie + cookie_dict['SUHB'] + '; '

    if 'ALF' in cookie_dict:
        cookie = cookie + cookie_dict['ALF'] + '; '

    if 'SSOLoginState' in cookie_dict:
        cookie = cookie + cookie_dict['SSOLoginState'] + '; '

    if 'un' in cookie_dict:
        cookie = cookie + cookie_dict['un'] + '; '

    if 'wvr' in cookie_dict:
        cookie = cookie + cookie_dict['wvr'] + '; '

    if 'WBStorage' in cookie_dict:
        cookie = cookie + cookie_dict['WBStorage'] + '; '

    return cookie


        # 获取html页面里面验证码的地址
def get_code_url(html):
    m = re.search(r"type\=(\S*)\" node-type", html)
    if m:
        return m.group(1)
    return None

# 获取重定向的页面
def get_replace_address(html):
    m = re.search(r"location\.replace\(\"(.+)\"\);", html)
    if not m:
        return None
    else:
        n_pin_url = m.group(1)
        print("跳转url" + n_pin_url)
        return n_pin_url


# 爬取主程序
def crawl(cookie_dict, url, proxy, browser, config_dict, sub_index):
    page = 1
    num_page = 1
    repeat_num = 0

    while page <= num_page:
        time.sleep(0.1)
        r_page = '&Refer=STopic_box'
        if page - 1 > 0:
            r_page = '&page='+str(page - 1)

        Cookie = 'login_sid_t={0}; _s_tentry={1}; Apache={2}; SINAGLOBAL={3}; ULV={4}; SWB={5}; SCF={6}; SUB={7}; SUBP={8}; SUHB={9}; ALF={10}; SSOLoginState={11}; un={12}; wvr={13}; WBStorage={14}'.format(
            cookie_dict['login_sid_t'], cookie_dict['_s_tentry'], cookie_dict['Apache'], cookie_dict['SINAGLOBAL'],
            cookie_dict['ULV'], cookie_dict['SWB'], cookie_dict['SCF'], cookie_dict['SUB'], cookie_dict['SUBP'],
            cookie_dict['SUHB'], cookie_dict['ALF'], cookie_dict['SSOLoginState'], cookie_dict['un'], cookie_dict['wvr'],
            cookie_dict['WBStorage'])
        req_header = {'Connection': 'keep-alive', 'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-CN;q=0.2',
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                      'Upgrade-Insecure-Requests': '1', 'Host': 's.weibo.com',
                      'Referer': url+str(r_page),
                      'Accept-Encoding': 'gzip, deflate, sdch', 'Cookie': Cookie}

        # 当前请求的url
        cur_url = url+'&page='+str(page)

        # 请求页面
        r = get(cur_url, req_header, proxy)
        if not r.status_code == 200:
            time.sleep(2)
            continue

        r.encoding = "unicode-escape"
        html = r.text
        # 更新最大页
        if num_page == 1:
            num_page = get_max_page(html)

        # 判断是否有效页
        r_code = process_html(html, page, cur_url)
        if r_code == 10:
            r.encoding = "utf-8"
            html = r.text
            with open('./特殊页面/e_page'+str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))+'.html', 'w', encoding="utf-8") as f:
                f.write(html)
            return False
        # 没有结果的页面
        elif r_code == 1:
            repeat_num += 1
            if repeat_num == 3:
                repeat_num = 0
                page += 1
        # 处理跳转
        elif r_code == 4:
            with open('./特殊页面/跳转页面' + str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + '.html',
                      'w',
                      encoding='utf-8')as f:
                f.write(html)
            n_pin_url = get_replace_address(html)
            # 请求验证页面
            rr = requests.get(n_pin_url, headers=req_header, proxies=proxy, timeout=5)
            if rr.text == "":
                is_ok = False
        # 验证码
        elif r_code == 2:
            # with open('./特殊页面/code' + str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))) + '.html',
            #           'w',
            #           encoding='utf-8')as f:
            #     f.write(html)
            # submit_code(cookie_dict, cur_url, html, proxy)
            # 检查是否已经有打码程序在运行
            if config_dict["m"].acquire(False):
                try:
                    browser.handle_code()
                except:
                    traceback.print_exc()
                finally:
                    config_dict["m"].release()
            else:
                time.sleep(10)
            # while not code_result:
            #     time.sleep(1)
            #     code_result = verify_code.verify_code(cookie_dict,cur_url, pin_url)
        else:
            repeat_num = 0
            #  翻页
            page += 1

    # 完成单个采集项目更新数据库
    finish_url(url, page-1, num_page)
    # 收集完成，标记号设置为0
    config_dict["l"][sub_index] = 0


# download_proxy()
# c_list = get_cookie_list()
# cookie = convert_cookie(c_list)[0]

def record_url(b_url_list):
    with open("./config/url_list.txt", "a") as f:
        for url in b_url_list:
            f.write(url + "\n")


def crawl_weibo(user, pwd, url_list):
    # 选择chrome浏览器的webdriver
    chrome = webdriver.Chrome(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe")
    # chrome = webdriver.PhantomJS(r"D:\Program Files (x86)\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    chrome.set_window_size(1050,600)
    try:
        # 使用浏览器进行登陆
        mb = MyBrowser(chrome, user, pwd)
        cookie = None
        test_num = 0
        while (not cookie):
            test_num += 1
            cookie = mb.get_cookie()
            time.sleep(2)
            print("未知错误")
            if test_num >= 10:
                raise MyError("登陆异常过多")
        print(cookie)

        # 进行url的请求
        proxy = get_proxy()

        # 多线程参数设置
        url_mutex = threading.Lock()
        config_dict = dict()
        config_dict["m"] = url_mutex
        config_dict["l"] = [0, 0, 0]

        is_finish = False
        while not is_finish:
            # 扫描会否已经启动五个线程
            for pi, ii in enumerate(config_dict["l"]):
                if ii == 0:
                    # 标识符设置为1
                    config_dict["l"][pi] = 1
                    url = url_list.pop()
                    print(url.strip() + "\t" + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
                    t = threading.Thread(target=crawl, args=(cookie, url.strip(), proxy, mb, config_dict, pi))
                    t.start()
                    # 所有url采集完毕
                    if not url_list:
                        t_num = 0
                        count_thread_num = 0
                        time.sleep(260)
                        # 等待所有进程采集完毕
                        while t_num != len(config_dict["l"]):
                            t_num = 0
                            # 统计有多少个线程正在采集
                            for n in config_dict["l"]:
                                if n == 0:
                                    t_num += 1
                            time.sleep(10)
                            # 计算运行次数
                            count_thread_num += 1
                            if count_thread_num == 10:
                                is_finish = True
                        is_finish = True
            time.sleep(2)
    except MyError as e:
        print(user+"---"+ str(e))
        del_user(user)
        chrome.quit()
        # 放回去
        record_url(url_list)
        return False
    except:
        with open("./record/Error.txt","a") as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+"\n")
            traceback.print_exc(file=f)
            f.write('\n')
        finish_user(user)
        # 放回去
        record_url(url_list)
        chrome.quit()
        return False
    # 完成时候记录下时间
    with open("./record/record.txt", "a") as f:
        f.write(user+"\n")
        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+"\n")
    finish_user(user)
    chrome.quit()
    return True


def update_proixy():
    while True:
        t = threading.Thread(target=download_proxy)
        t.setDaemon(True)
        t.start()
        time.sleep(100)


print("=======Get Proxy=======")
with open("./config/download_proxy_list.txt", "w") as f:
        f.write("")
t_url = threading.Thread(target=update_proixy)
t_url.setDaemon(True)
t_url.start()
time.sleep(2)
print("======Finish Proxy======")

print("=======Get Url=======")
t_url_list = get_url_list(30000)
with open("./config/url_list.txt", "w") as f:
    for url in t_url_list:
        f.write(url+"\n")
print("=======Finish Url=======")


count_num = 0
FLAG = True
# 主函数
while FLAG:
    user_list = get_user_list(15)
    for user, pwd in user_list:
        url_list = []
        with open("./config/url_list.txt", "r") as f:
            f_list = f.readlines()
        i = 0
        max_line = len(f_list)

        # 添加url
        while i < 500 and i < (max_line - 1):
            url = f_list[0]
            f_list.remove(url)
            url_list.append(url.strip())
            i += 1

        # 重新覆盖
        with open("./config/url_list.txt", "w") as f:
            for l_url in f_list:
                f.write(l_url)

        # 判断是否要新增
        if max_line < 10:
            count_num += 1
            print("url文件重新读取 " + str(count_num))
            if count_num > 10:
                FLAG = False
                break
            t_url_list = get_url_list(30000)
            with open("./config/url_list.txt", "w") as f:
                for url in t_url_list:
                    f.write(url + "\n")

        if url_list:
            print(user)
            print(str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            c = threading.Thread(target=crawl_weibo, args=(user, pwd, url_list))
            c.start()
            time.sleep(30)
        else:
            print("url全部加载完毕")
    time.sleep(300)



print(str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))))
time.sleep(1000000)