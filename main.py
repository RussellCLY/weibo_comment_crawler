#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/21 10:54
# @Author  : 胡已源
# @File    : main.py
# @Software: PyCharm
import json
import os
import redis
from sina_weibo.script.sina_comment_one import SinaComment
from sina_weibo.script.sina_comment_two import CrawlThread
from sina_weibo.config.settings import host, password, port
from sina_weibo.script.data_upload import Upload

if __name__ == '__main__':

    crawl_thread_list = []

    redis_client = redis.Redis(host=host, port=port, password=password)

    dir_path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    with open(dir_path + 'sina_weibo/config/file/cookies.json', mode='r', encoding='utf-8') as f:
        cookies = json.loads(f.read())

    for web_cookies in cookies['web']:
        s = SinaComment(redis_client, web_cookies['cookie'])  # 一级评论采集
        s.setDaemon(True)
        crawl_thread_list.append(s)

    for app_cookies in cookies['app']:
        c = CrawlThread(redis_client, app_cookies)  # 二级评论采集
        c.setDaemon(True)
        crawl_thread_list.append(c)

    # for _ in range(1):
    #     u = Upload()
    #     u.setDaemon(True)
    #     crawl_thread_list.append(u)

    # 评论采集
    for crawl in crawl_thread_list:
        crawl.start()

    for t in crawl_thread_list:
        t.join()
