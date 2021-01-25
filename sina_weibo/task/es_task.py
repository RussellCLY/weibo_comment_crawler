#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/10/22 17:21
# @Author  : 胡已源
# @File    : es_demo.py
# @Software: PyCharm
import datetime
import csv
import os

import jsonpath
import redis
import requests
import sys

sys.path.append("./")
from sina_weibo.utils.date_tools import get_before_30_date
from sina_weibo.config.settings import host, password, redis_blog_key


class Task:
    """
     任务获取类
    """

    def __init__(self):
        self.redis_client = redis.Redis(host=host, password=password)
        self.session = requests.Session()
        # 配置参数
        self.time = get_before_30_date(1)
        self.url = "http://192.168.10.103:9200/_sql"
        self.payload = "select * from mblog_info where user_id = {} and pubtime >= '{} 00:00:00'" \
                       " order by interaction_count desc limit 0,50"
        self.headers = {
            'Proxy-Connection': "keep-alive",
            'Accept': "application/json, text/plain, */*",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
            'Content-Type': "application/json;charset=UTF-8",
            'Accept-Language': "zh-CN,zh;q=0.9"
        }

        # self.proxies = {"http": '192.168.6.1:1984', "https": '192.168.6.1:1984'}

    @staticmethod
    def get_uid_list():
        """
        获取需要抓取重点微博uid
        @return: list()
        """
        uid_list = list()
        sep = os.sep
        dir_path = os.path.abspath(os.path.dirname(__file__)) + sep
        path = dir_path[:dir_path.rfind(sep) - 4] + "config{}file{}data.csv".format(sep, sep)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                uid_list.append(row[1])
        return uid_list

    def find_es_data(self, uid_, payload_=''):
        """
        从es中获取数据
        @param payload_: 请求参数
        @param uid_: uid
        @return: 需要抓取博文url
        """
        if not payload_:
            payload_ = self.payload.format(uid_, self.time)
        response = self.session.post(self.url, data=payload_, headers=self.headers, timeout=60)
        print(response)
        source_url_list = jsonpath.jsonpath(response.json(), '$.hits.hits[*]._source[source_url]')
        if source_url_list:
            for url_ in source_url_list:
                yield url_

    def generate_task_list(self):
        for uid in self.get_uid_list():
            for url_ in self.find_es_data(uid):
                yield url_

    def get_task_list(self):
        """
        获取需要抓取任务list
        @return:
        """
        tasks = []
        for uid in self.get_uid_list():
            for url_ in self.find_es_data(uid):
                tasks.append(url_)
        return tasks

    def save_task_to_redis(self):
        """
        任务推送至redis
        @return:
        """
        for item in self.get_task_list2():
            print("添加博文至--->redis:", item)
            self.push_redis(item)
            # self.redis_client.lpush(redis_blog_key, item)

    def push_redis(self, data):
        """
        推送任务
        @param data:数据
        @return:
        """
        self.redis_client.lpush(redis_blog_key, data)

    def get_task_list2(self):
        return [
            # "https://m.weibo.cn/status/4568561508945042",
            # "https://m.weibo.cn/5461016454/4555254534772468",
            # "https://m.weibo.cn/5461016454/4539729522994612",
            # "https://m.weibo.cn/2418471844/JskS9nD3k"
            "https://m.weibo.cn/2418471844/4596908674782097"
        ]

if __name__ == '__main__':
    pass
    task = Task()

    task.save_task_to_redis()
    # import redis
    #
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # redis_client = redis.Redis(host='localhost', port=6379)
    #
    # redis_client.set('name', 'lipingyuan')
    #
    # print(redis_client.get('name'))
    # task.
    # uid_list = [
    #     7483054836, 6397754323, 6551339780, 7073308386, 6528178851, 6969972165,
    #     6970924033, 6189120710, 3592075834, 7468777622, 7336594039, 1699432410,
    #     2803301701, 5651101017, 1728148193, 7508733210, 5493018291, 6224784458
    # ]
    #
    # for y in uid_list:
    #     pay = "select * from mblog_info where user_id = {} and pubtime >= '2020-11-16 00:00:00' order by interaction_count desc ".format(y)
    #
    #     for i in task.find_es_data(y, pay):
    #         task.push_redis(i)
    #         print(i)

