#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/21 9:31
# @Author  : 胡已源
# @File    : utils.py
# @Software: PyCharm
import hashlib
import json

import requests


def hash_md5(md):
    """
     md5
    """
    m = hashlib.md5()
    m.update(md.encode("utf-8"))
    return m.hexdigest()


def pretty_json(obj):
    """
     格式化输出
    """

    try:
        return json.dumps(obj, indent=4, ensure_ascii=False, separators=(',', ':'))
    except (Exception,):
        print("错误的json格式")


def check_filed(fields, data_list):
    """
    检查指定字段是否缺失
    :param fields: 指定检查字段的列表
    :param data_list: 检查的数据(字典或者列表均可)
    """
    if isinstance(data_list, dict):
        data_list = [data_list]
    for field in fields:
        for data_dict in data_list:
            if not data_dict.get(field):
                print(data_dict)
                raise Exception(field + "字段缺失")


def get_public_ip():
    return requests.get("http://ip.42.pl/raw").text


def bid2mid(bid):
    """
        convert string bid to string mid
    """
    str_num = ''
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    base = len(alphabet)
    bid_len = len(bid)
    head = bid_len % 4
    digit = int((bid_len - head) / 4)
    d_list = [bid[0:head]]
    for d in range(1, digit + 1):
        d_list.append(bid[head:head + d * 4])
        head += 4
    mid = ''
    for d in d_list:
        num = 0
        idx = 0
        str_len = len(d)
        for char in d:
            power = (str_len - (idx + 1))
            num += alphabet.index(char) * (base ** power)
            idx += 1
            str_num = str(num)
            while len(d) == 4 and len(str_num) < 7:
                str_num = '0' + str_num
        mid += str_num
    return mid


if __name__ == '__main__':
    mid = bid2mid("JskS9nD3k")
    print(mid)

    # 4597205962857601
    # 4567534215631666
