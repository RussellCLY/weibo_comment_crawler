#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/20 11:09
# @Author  : 胡已源
# @File    : core.py
# @Software: PyCharm

import datetime
import json
import random
import sys
import threading
import time

import requests
import urllib3

sys.path.append("./")
from sina_weibo.utils.com_tools import hash_md5, pretty_json
from sina_weibo.utils.date_tools import format_Tue_time
from sina_weibo.config.log import logger
from sina_weibo.config.pipelines_queue import data_queue
from sina_weibo.config.settings import redis_comment_key

urllib3.disable_warnings()


class CrawlThread(threading.Thread):
    """
     采集线程
    """

    def __init__(self, client_, cookies):
        super().__init__()
        self.client = client_
        self.root_mid = 0,  # 根评论id
        self.blog_url = ''
        self.count = 0
        self.url = 'https://api.weibo.cn/2/comments/build_comments'
        self.headers = {
            'Host': 'api.weibo.cn',
            'User-Agent': 'Pixel_9_weibo_10.10.0_android',
            'Accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.cookies = cookies
        self.ip = self.get_ip() or '127.0.0.0'

    @staticmethod
    def get_ip():
        return requests.get("http://ip.42.pl/raw").text

    def gen_query_params(self, meta):
        """
         生成请求参数
        """
        querystring = {
            'is_mix': '1',
            'is_show_bulletin': '2',
            'c': 'weibolite',
            's': self.cookies['s'],
            'id': self.root_mid,
            'from': self.cookies['from'],
            'gsid': self.cookies['gsid'],
            # 'oriuicode': '10000010_10000003_10000198_10000002',
            'fetch_level': '1'
        }
        if not meta['is_root']:
            querystring['max_id'] = meta['next_cursor']
        return querystring, meta

    @logger.catch
    def cut_sina_comment_data(self, data):
        """
        解析数据
        @param data:
        """
        comments = data['comments']

        if not data['status']:
            print("错误！")
        mid = data['status']['mid']

        for comment in comments:
            user_id = comment['user']['idstr']
            try:

                data = dict()
                data['S'] = 'ziacai'
                data['user_id'] = user_id
                data['userid'] = user_id
                data['content'] = comment['text']
                data['source_url'] = self.blog_url
                data['url'] = self.blog_url
                data['user_name'] = comment['user']['name']
                data['author'] = data['user_name']
                data['article_type'] = 2
                data['article_id'] = mid
                data['mblog_id'] = mid
                data['mid'] = mid
                data['language'] = 1
                data['host'] = 'weibo.com'
                data['pubtime'] = format_Tue_time(comment['created_at'])
                data['crawler_no'] = self.ip
                data['crawler_type'] = 1
                data['media_type'] = 1
                data['up_count'] = comment['like_counts']
                data['upcount'] = data['up_count']
                data['cmt_count'] = 0
                data['commtcount'] = 0
                data['rtt_count'] = 0
                data['share_num'] = 0
                data['interaction_count'] = 0
                data['interaction_num'] = data['interaction_count']

                data['region'] = 0
                data['insert_time'] = str(datetime.datetime.now()).split('.')[0]

                data['comments_id'] = comment['mid']
                uuid = hash_md5(data['comments_id'])
                data['root_id'] = self.root_mid
                data['uuid'] = uuid
                data['md5'] = uuid

            except Exception as e:
                logger.error("解析数据错误!", e)
            else:
                self.count += 1
                logger.debug(pretty_json(data))
                data_queue.put(data)

    def run(self):
        """
        运行
        @return:
        """
        while True:
            pointer = 0
            try:
                str_comment_data = self.client.lpop(redis_comment_key)
                if not str_comment_data:
                    continue
                root_comment_data = json.loads(str_comment_data)
            except Exception as e:
                logger.exception("获取二级评论异常！", e)
                continue

            root_comment = self.root_mid = root_comment_data['comments_id']
            self.blog_url = root_comment_data['url']
            self.root_mid = root_comment
            next_params, queue_item = self.gen_query_params({
                'pages': 1,
                'is_root': True,
                'root_mid': root_comment,
                'next_cursor': root_comment,
            })
            while next_params:
                try:
                    response = requests.get(self.url, headers=self.headers, params=next_params, timeout=30,
                                            verify=False)
                    if not response.text:
                        logger.warning("采集评率过快,触发风控,采集线程休眠2分钟!")
                        time.sleep(120)  # 休息2分钟
                        break
                    data_list = response.json()

                    pointer += 1
                    if data_list.get('comments'):
                        pointer = 0

                    if pointer > 3:
                        logger.info("连续采集3次未获取数据,跳出循环!")
                        break

                except Exception as e:
                    logger.exception('采集错误,当前错误链接{},请求参数:{},异常信息:{}', self.url, next_params, e)
                    # 如果中间某一页出错,需要重新开始一页采集
                    param, queue_item = self.gen_query_params({
                        'pages': 1,
                        'is_root': True,
                        'root_mid': self.root_mid,
                        'next_cursor': self.root_mid,
                    })
                    next_params = param
                else:
                    logger.info(
                        f"当前第[{queue_item['pages']}]页,"
                        f"采集的mid:[{queue_item['next_cursor']}],"
                        f"当前评论总条数:{data_list.get('total_number')},"
                        f"抓取到的评论数:[{self.count}]"
                    )
                    # 解析数据
                    self.cut_sina_comment_data(data_list)
                    next_cursor = data_list.get('next_cursor')

                    if not next_cursor and next_cursor == 0:  # 0表示到了最后一页
                        logger.debug('mid:[{}],采集完成!!!!', queue_item['next_cursor'])
                        self.root_mid = 0
                        self.count = 0
                        break

                    if next_cursor:
                        param, queue_item = self.gen_query_params({
                            'pages': queue_item['pages'] + 1,
                            'is_root': False,
                            'root_mid': self.root_mid,
                            'next_cursor': next_cursor,
                        })
                        next_params = param
                finally:
                    time.sleep(random.randint(3, 5))


if __name__ == '__main__':
    # crawl_thread = CrawlThread('Thread-1')
    # crawl_thread.run()
    pass
