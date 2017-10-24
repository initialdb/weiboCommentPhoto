# coding:utf8

import re
import os
import urllib.request

from bs4 import BeautifulSoup
from selenium import webdriver
from sqlhelper import redishelper
import time


class browser_controler():
    def __init__(self, create_browser=True, connections=5):
        # 请将chromedriver复制到你的chrome安装目录
        # chromedriver = r'C:\Users\用户名\AppData\Local\Google\Chrome\Application\chromedriver.exe'
        # profile_dir = r"C:\Users\用户名\AppData\Local\Google\Chrome\User Data"  # 对应你的chrome的用户数据存放路径
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument(
        #     'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        # chrome_options.add_argument(r"user-data-dir=C:\Users\Windows\AppData\Local\Google\Chrome\User Data\Default")
        # 此配置使chrome浏览器在访问网页时不在加载图片，加快浏览速度
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        if create_browser:
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.redishelper = redishelper.redishelper(connections)
        # self.driver.get('http://weibo.com/p/1005051816605567/photos')
        pass

    # 匹配用户相册图片
    def match_user_imgs(self, photopage):
        soup = self.load_page_to_bottom(photopage)
        userid = self.redishelper.get_user_id(photopage)
        if userid is None:
            return
        img_srcs = soup.find_all('img', class_='photo_pict')
        imgs = set()
        for img_src in img_srcs:
            src = img_src.attrs['src']
            rsrc = re.search(r'\w+\.gif', src)
            if rsrc is not None:
                imgs.add(rsrc.group())
        self.redishelper.insert_new_imgs(imgs, userid)

    # 下载用户信息
    def download_userinfo(self):
        while True:
            homepage = self.redishelper.get_downloading_homepage()
            if homepage is not None and len(homepage) > 17:
                self.get_user_info(homepage)
            else:
                time.sleep(3)

    # 不断滚动到底端获得网页源代码
    def load_page_to_bottom_source(self, url):
        self.scroll_to_bottom(url)
        return self.driver.page_source

    # 滚动到底部
    def scroll_to_bottom(self, url):
        print(r'开始加载网页%s' % url)
        self.driver.get(url)
        time.sleep(1)
        height = 0
        while True:
            size = self.driver.find_element_by_tag_name('body').size
            if height != size['height']:
                height = size['height']
                js = "document.documentElement.scrollTop=" + str(height)
                self.driver.execute_script(js)
                time.sleep(1)
            else:
                break

    # 展开页面所有评论
    def expand_comments(self, url):
        print(r'开始加载网页%s' % url)
        self.driver.get(url)
        time.sleep(1)
        height = 0
        while True:
            size = self.driver.find_element_by_tag_name('body').size
            if height != size['height']:
                height = size['height']
                js = "document.documentElement.scrollTop=" + str(height)
                self.driver.execute_script(js)
                time.sleep(1)
            else:
                break
        js = r'var lines=document.getElementsByClassName("line S_line1");for (i=0;i<lines.length;i++){l=lines[i];if (l.getAttribute("node-type")=="comment_btn_text"){console.log(i);l.click();}}'
        self.driver.execute_script(js)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    # 不断滚动到底端获得beautifulsoup对象
    def load_page_to_bottom(self, url):
        self.scroll_to_bottom(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    # 根据homepage取得用户信息
    def get_user_info(self, homepage):
        soup = self.expand_comments(homepage)
        usernames = soup.find('h1', class_='username')
        if usernames is None:
            return
        username = usernames.get_text()
        photo_page_urls = soup.find_all('a', href=re.compile(r'^/p/\d+/photos.*'))
        if photo_page_urls is None or len(photo_page_urls) == 0:
            return
        photo_page_url = re.match(r'^/p/\d+/photos', photo_page_urls[0]['href']).group()
        self.match_user_homepage(soup)
        # 取得“更多评论”链接
        comment_photos = re.findall(r'//weibo\.com/\d+/\w+', self.driver.page_source)
        for comment_url in comment_photos:
            self.redishelper.insert_new_comment_url(r'http:' + comment_url)
        print('添加了%s个评论地址' % len(comment_photos))
        self.redishelper.insert_downloaded_homepage(homepage)
        if self.redishelper.insert_new_user(username, homepage, r'http://weibo.com' + photo_page_url):
            print('成功下载了%s的主页信息\n' % username)
        else:
            print('下载%s的主页信息出错' % username)

    # 从用户主页中匹配其他用户主页信息
    def match_user_homepage(self, soup):
        links = set()
        # 类似/u/1927564525?from=feed&loc=nickname
        links_u = soup.find_all('a', href=re.compile(r'^/u/\d+[\??.*]'))
        # 类似//weibo.com/yangmiblog
        links_weibo_nickname = soup.find_all('a', href=re.compile(r'^//weibo.com/\w+$'))
        # 类似/tv?sfd=sdfs&dfgsd=sfe
        links_weibo_nickname_args = soup.find_all('a', href=re.compile(r'^/\w+\?{1}.+'))
        # 类似/n/昵称
        # links_weibo_n_name = soup.find_all('a', href=re.compile(r'^/n/.+$'))
        print(r'取到%s个用户链接' % str(
            len(links_u) + len(links_weibo_nickname) + len(links_weibo_nickname_args)))
        for link in links_u:
            links.add(r'http://weibo.com' + str(re.match(r'^/u/\d+', link['href']).group()))
        for link in links_weibo_nickname:
            links.add(r'http:' + link['href'])
        for link in links_weibo_nickname_args:
            links.add(r'http://weibo.com' + re.match(r'^/\w+', link['href']).group())
        # for link in links_weibo_n_name:
        #     links.add(r'http://weibo.com' + link['href'])
        self.redishelper.insert_new_homepages(links)

    def start(self, start_url):
        self.driver.get(start_url)
        time.sleep(5)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.match_user_homepage(soup)
        self.download_userinfo()

    # 访问评论，爬取照片
    def download_comment_photo(self):
        while True:
            comment_url = self.redishelper.get_downloading_comment()
            if comment_url is not None:
                self.match_comment_photo(comment_url)
            else:
                print(r'当前没有评论待爬取，等待2秒')
                time.sleep(3)

    # 匹配评论中的图片
    def match_comment_photo(self, comment_url):
        self.driver.get(comment_url)
        time.sleep(3)
        print('正在访问评论：', comment_url)
        height = 0
        while True:
            size = self.driver.find_element_by_tag_name('body').size
            if height != size['height']:
                height = size['height']
                js = "document.documentElement.scrollTop=" + str(height)
                self.driver.execute_script(js)
                time.sleep(1)
            else:
                break
        height = 0
        t = 0
        while True:
            size = self.driver.find_element_by_tag_name('body').size
            if height != size['height'] and t < 10:
                height = size['height']
                js = "document.documentElement.scrollTop=" + str(height)
                self.driver.execute_script(js)
                try:
                    js = r'document.getElementsByClassName("WB_cardmore")[0].click();'
                    self.driver.execute_script(js)
                except:
                    break
                t += 1
                time.sleep(2)
            else:
                break
        # js = 'var height=0;\nwhile(true){\nif(height!=document.body.scrollHeight){\nheight=document.body.scrollHeight;\ndocument.documentElement.scrollTop=height;\ndocument.getElementsByClassName("WB_cardmore")[0].click();\n}else{\nreturn;\n}\n}'
        # self.driver.execute_script(js)
        # soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        comment_photos = re.findall(r'imagecard="pid=\w+', self.driver.page_source)
        photos = set()
        for comment_photo in comment_photos:
            print(comment_photo)
            photos.add(comment_photo[15:] + ".jpg")
        self.redishelper.insert_new_imgs_to_download(photos)
