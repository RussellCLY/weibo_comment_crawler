#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/26 16:09
# @Author  : 胡已源
# @File    : data_upload.py
# @Software: PyCharm
import json
import threading
import time
from sina_weibo.utils.upload_tools import uploading_data
from sina_weibo.config.pipelines_queue import data_queue


class Upload(threading.Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        print('数据推送线程')
        while True:
            if data_queue.qsize():
                data = data_queue.get()
                uploading_data(data)
            else:
                time.sleep(1)


if __name__ == '__main__':
    pass
    # import requests
    #
    # url = "http://192.168.56.1:32701/data/upload"
    #
    # payload = "[\n    {\n        \"keyword\": \"电子书\",\n        \"channel_name\": \"新闻\",\n        \"video_path\": \"http://23456\",\n        \"steam_time\": \"2020-10-14 17:02:45\",\n        \"video_time\": \"2020-10-14 16:25:39\",\n        \"post_time\": \"2020-10-14 16:25:39\",\n        \"video_note\": \"写笔记\",\n        \"status\": 1,\n        \"message_user\": \"写文本\",\n        \"update_time\": \"2020-10-14 16:25:39\",\n        \"insert_time\": \"2020-10-14 16:25:39\"\n    },\n    {\n        \"keyword\": \"电子书\",\n        \"channel_name\": \"新闻\",\n        \"video_path\": \"http://23456\",\n        \"steam_time\": \"2020-10-14 17:02:45\",\n        \"video_time\": \"2020-10-14 16:25:39\",\n        \"post_time\": \"2020-10-14 16:25:39\",\n        \"video_note\": \"写笔记\",\n        \"status\": 1,\n        \"message_user\": \"写文本\",\n        \"update_time\": \"2020-10-14 16:25:39\",\n        \"insert_time\": \"2020-10-14 16:25:39\"\n    }\n]"
    # headers = {
    #     'Accept': "*/*",
    #     'Connection': "keep-alive",
    #     'Content-Type': "application/json",
    #     'Host': "192.168.0.56:32701",
    #     'User-Agent': "PostmanRuntime/7.13.0",
    #     'accept-encoding': "gzip, deflate",
    #     'content-length': "1300"
    # }
    #
    # response = requests.request("POST", url, data=payload, headers=headers)
    #
    # print(response.text)