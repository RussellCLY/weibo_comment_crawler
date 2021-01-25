#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/12/1 10:28
# @Author  : 胡已源
# @File    : demo.py
# @Software: PyCharm


import requests

next_url = "https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4577002533424521&from=singleWeiBo&__rnd=1594553068602"
cookies = "SUB=_2AkMo9xgvdcPxrARUmfkdyWjnZY1H-jybInHZAn7uJhMyOhh87nIOqSVutBF-XCnpb1_7Ak1SIsq3F5NxXMupn72Y; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhXMxSEC0D1eyOTQ7g9Y12G5JpVF02fSKMfeKeNShzf; login_sid_t=cbf9f3fe319e91ddbd60db8d70cfe4c0; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=3627638989130.4062.1605080858463; SINAGLOBAL=3627638989130.4062.1605080858463; ULV=1605080858473:1:1:1:3627638989130.4062.1605080858463:; wb_view_log=1440*9002; WBtopGlobal_register_version=2020111210"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/86.0.4240.75 Safari/537.36',
    'cookie': cookies,
}

response = requests.get(url=next_url, headers=headers, timeout=30, verify=False)
print(response.text)



