#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/11/23 14:43
# @Author  : 胡已源
# @File    : sql.py
# @Software: PyCharm
import csv
import os

import pymysql

import pymysql.cursors

# Connect to the database
from sina_weibo.utils.date_tools import get_current_time

sep = os.sep
dir_path = os.path.abspath(os.path.dirname(__file__)) + sep
path = dir_path[:dir_path.rfind(sep) - 4] + "config{}file{}data.csv".format(sep, sep)

# with open(path, 'r') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         print(row)
#         # user_name = row[0]
#         # user_id = row[1]
#         # user_url = row[2]


connection = pymysql.connect(host='192.168.10.175',
                             user='wg_dba',
                             password='wgdb%2017',
                             db='sina_mblog',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                user_name = row[0]
                user_id = row[1]
                user_url = row[2]

                sql = "INSERT INTO `mblog_comment` (`user_name`, `user_id`,`user_url`,`frequency`,`crawl_time`) VALUES (%s,%s,%s,%s,%s)"
                cursor.execute(sql, (user_name, user_id, user_url, 1000, get_current_time()))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()
finally:
    connection.close()
