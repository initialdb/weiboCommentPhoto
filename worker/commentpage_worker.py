# coding:utf8
import threading
from browser_control import browser_controler
class commentpage_worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name=r'搜索用户微博评论')
        self.worker = browser_controler.browser_controler()

    def run(self):
        # 某些微博大V主页，实测这几个用户足够爬取过万个表情包……
        user_homepage_list=[
            r'http://weibo.com/jianglaoye',
            r'http://weibo.com/tfwangjunkai',
            r'http://weibo.com/u/1669879400',
            r'http://weibo.com/tfyiyangqianxi',
            r'http://weibo.com/liyifeng2007',
            r'http://weibo.com/yangmiblog',
            r'http://weibo.com/williamchanwaiting',
            r'http://weibo.com/lixiaolu',
            r'http://weibo.com/u/1815418641',
            r'http://weibo.com/tfwangyuan',
            r'http://weibo.com/mmc8832',
            r'http://weibo.com/gemtang'
        ]
        for url in user_homepage_list:
            self.worker.get_user_info(url)
        self.worker.driver.close()