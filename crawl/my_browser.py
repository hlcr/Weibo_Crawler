from selenium import webdriver
import time  #调入time函数
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from PIL import Image
from crawl.handle_captcha.cr_http import *
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import random
import os
from crawl.MyError import *

# PROXY = "27.18.101.124:8998"
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--proxy-server=http://'+PROXY)

class MyBrowser:
    user = ""
    pwd = ""

    def __init__(self, browser, user, pwd):
        self.browser = browser
        self.user = user
        self.pwd = pwd
        self.client = Chaoren()
        self.client.data['username'] = 'XXXX'  # 修改为打码账号
        self.client.data['password'] = 'XXXXXX'  # 修改为打码密码

    # 通过class判断是否存在
    def check_exists_class(self, class_name):
        try:
            self.browser.find_element_by_class_name(class_name)
        except NoSuchElementException:
            return False
        return True

    def clear_code(self, code_pic):
        is_valid = False
        while not is_valid:
            pic_name = str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))+str(random.randint(0, 100))
            pic_name = r"D:\tempcode\{0}.png".format(pic_name)
            self.browser.save_screenshot(pic_name)
            loc = code_pic.location
            img = Image.open(pic_name)
            region = (loc['x'], loc['y'], loc['x'] + 95, loc['y'] + 34)
            # 裁切图片
            cropImg = img.crop(region)
            cropImg.save(pic_name)

            imgdata = open(pic_name, 'rb').read()
            if os.path.exists(pic_name):
                os.remove(pic_name)
            res = self.client.recv_byte(imgdata)
            if type(res) == type(False):
                is_valid = False
            else:
                # 保存验证码图片
                i = 0
                code_pic_name = r'D:\code\{0}.png'.format(res[u'result'])
                while os.path.exists(code_pic_name):
                    code_pic_name = r'D:\code\{0}.png'.format(res[u'result']+"("+str(i)+")")
                    i += 1
                cropImg.save(code_pic_name)
                res['pic_name'] = code_pic_name
                is_valid = True
                return res

    def get_cookie(self):
        self.browser.get("http://weibo.com/")
        WebDriverWait(self.browser, 60).until(EC.visibility_of_element_located((By.ID, "loginname")))
        self.browser.find_element_by_id("loginname").send_keys(self.user)
        self.browser.find_element_by_class_name("password").find_element_by_class_name("W_input").send_keys(self.pwd)
        time.sleep(1)
        self.browser.find_element_by_class_name("W_btn_a").click()
        time.sleep(1)
        # 判断是否有验证码
        try:
            attr = self.browser.find_element_by_css_selector('.info_list.verify.clearfix').get_attribute("style")
            if not attr == "display: none;":
                code_pic = self.browser.find_element_by_class_name("verify").find_element_by_tag_name("img")
                res = self.clear_code( code_pic)
                self.browser.find_element_by_css_selector(".info_list.verify.clearfix .W_input").send_keys(res[u'result'])
            time.sleep(1.5)
            self.browser.find_element_by_class_name("W_btn_a").click()
            time.sleep(5)
        except NoSuchElementException:
            pass

        # WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "W_face_radius")))
        # browser.execute_script('window.stop()')
        if self.check_exists_class("title"):
            if "帐号异常" in self.browser.find_element_by_class_name("title").text:
                raise MyError("账号异常")
        if r'freeze' in self.browser.current_url:
            raise MyError("账号被封")
        if r'home' not in self.browser.current_url:
            return None
        cookie = self.browser.get_cookies()
        r_dict = dict()
        print(self.user+" GETURL")

        while 's.weibo.com' not in self.browser.current_url:
            url = 'http://s.weibo.com/weibo/%25E7%25BE%258E%25E5%259B%25BD&scope=ori&suball=1&timescope=custom:2016-12-01-10:2016-12-27-15&Refer=g'
            self.browser.get(url)
            time.sleep(5)
            self.browser.execute_script('window.stop()')
        # WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "WB_feed_detail")))

        print(self.user+" Cookie")
        cookie1 = self.browser.get_cookies()
        cookie.extend(cookie1)
        time.sleep(1)
        for item in cookie:
            r_dict[item["name"]] = item["value"]
        return r_dict

    # 本地化保存cookie
    def save_cookie(self, cookie, file_path):
        with open(file_path+"\cookie", "w") as f:
            f.write(json.dumps(cookie))
            f.write('\n')

    def report_error_code(self, res):
        self.client.report_err(res[u'imgId'])

    # 模拟打码程序
    def handle_code(self):
        url = 'http://s.weibo.com/weibo/%25E7%25BE%258E%25E5%259B%25BD&scope=ori&suball=1&timescope=custom:2016-12-01-10:2016-12-27-15&Refer=g'
        if self.check_exists_class("hotsearch_rank_list"):
            try:
                a_links = self.browser.find_elements(By.CSS_SELECTOR, ".hotsearch_rank_list a")
                a_links[random.randint(0, len(a_links) - 1)].click()
            except WebDriverException:
                self.browser.get(url)
                print("不能点击")
                time.sleep(5)
            time.sleep(5)
        if self.check_exists_class("feed_content"):
            self.browser.get(url)
            time.sleep(5)
            print(self.user+" nocode")
            return True
        elif self.check_exists_class("W_inputStp"):
            txt = ""
            while self.check_exists_class("W_inputStp"):
                try:
                    self.browser.find_element_by_class_name("code_change").click()
                    time.sleep(2.5)
                    code_pic = self.browser.find_element_by_class_name("code_img").find_element_by_tag_name("img")
                    res = self.clear_code(code_pic)
                    self.browser.find_element_by_class_name("W_inputStp").send_keys(res[u'result'])
                    time.sleep(0.5)
                    self.browser.find_element_by_class_name('S_btn_b').click()
                    time.sleep(3)
                    if self.check_exists_class('M_notice_del'):
                        self.report_error_code(res)
                        txt = self.browser.find_element_by_class_name('M_notice_del').get_attribute('style')
                    else:
                        # print("okcode")
                        return True
                    # 删掉不合适的验证码
                    if os.path.exists(res["pic_name"]):
                        os.remove(res["pic_name"])
                except NoSuchElementException:
                    print(self.user+" nse")
                    time.sleep(2)
            return True
        else:
            return True


if __name__ == '__main__':
    # 选择chrome浏览器的webdriver
    # chrome = webdriver.Chrome(r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
    chrome = webdriver.PhantomJS(r"D:\Program Files (x86)\phantomjs-2.1.1-windows\bin\phantomjs.exe")
    chrome.set_window_size(1050,600)
    mb = MyBrowser(chrome, "17193176754", "a123456")
    while not mb.get_cookie():
        print("ERROR")
        time.sleep(0.5)
        pass
    mb.handle_code()

