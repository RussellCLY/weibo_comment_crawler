#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/21 10:19
# @Author  : 胡已源
# @File    : upload_tools.py
# @Software: PyCharm
import json

import requests

s = requests.Session()


def uploading_data(values: dict):
    """
    上传数据 typing
    @type values: object
    """
    pass
    print("#######################################")
    # # url = 'http://192.168.10.173:8082/kafka/allDataSend'
    # url = 'http://124.204.66.253:30035/kafka/allDataSend'
    # # headers = {'Content-Type': 'application/json', 'cache-control': 'no-cache', 'Connection': 'close'}
    # payload = {
    #     "topic": 'mblog_info',
    #     "msg": json.dumps(values)
    # }
    # try:
    #     res = s.post(url, data=payload, timeout=30)
    #     if res.status_code == 200:
    #         print("success:", res.text)
    # except Exception as e:
    #     print('上传失败', e)
#
#
# def greeting(name: str):
#     return 'Hello ' + name


if __name__ == '__main__':
    pass
    # uploading_data({"key":""})
