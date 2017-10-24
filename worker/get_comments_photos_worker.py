# coding:utf8
import threading
import time
from browser_control import browser_controler
from sqlhelper import redishelper

class get_comments_photos_worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name=r'访问评论详情')
        self.worker = browser_controler.browser_controler()

    def run(self):

        self.worker.download_comment_photo()