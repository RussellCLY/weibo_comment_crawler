#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/21 17:19
# @Author  : 胡已源
# @File    : demo.py
# @Software: PyCharm

import datetime
import json
import re
import sys
import threading
import time

import requests
import urllib3
from bs4 import BeautifulSoup

sys.path.append("./")
from sina_weibo.config.pipelines_queue import data_queue
from sina_weibo.utils import emoji_tools
from sina_weibo.utils.com_tools import hash_md5, pretty_json, bid2mid
from sina_weibo.utils.date_tools import get_13_time_stamp, parse_date_time
from sina_weibo.config.settings import redis_blog_key, redis_comment_key
from sina_weibo.config.log import logger

urllib3.disable_warnings()


class SinaComment(threading.Thread):
    """
     微博评论第一层
    """

    def __init__(self, client_, cookies):
        """

        @param client_:redis连接
        @param cookies: cookie
        """
        super().__init__()
        self.base_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&from=singleWeiBo&__rnd=1594553068602'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36',
            'cookie': cookies,
        }
        self.ip = self.get_ip() or '127.0.0.0'
        self.client = client_

    @staticmethod
    def get_html_cont(html):
        """
        获取评论html
        @param html:原始页面
        @return:
        """
        cont = ''
        try:
            data = json.loads(html).get('data', '')
        except Exception as e:
            par = re.search('(?<=")http[^"]+(?=")', html)
            if par:
                url = par.group()
                logger.info("页面跳转url:{}", url)
                return url
            else:
                print("页面解析错误:", e, html)
        else:
            if data:
                cont = data.get('html', '')
            return cont

    @staticmethod
    def get_ip():
        """获取本机ip"""
        return requests.get("http://ip.42.pl/raw").text

    def get_comment_list(self, html, m_blog_id, blog_url_):
        """
        获取评论列表
        @param blog_url_:
        @param html:
        @param m_blog_id:
        @param soup:
        :return:
        """
        print(m_blog_id)
        cont = self.get_html_cont(html)

        if not cont:
            return list(), ''

        if cont.startswith("http"):
            if 'www.w3.org' in cont or 'weibo.com/sorry' in cont:
                next_url_ = ''
            else:
                next_url_ = cont

            return list(), next_url_

        # soup = BeautifulSoup(cont, 'html5lib')
        soup = BeautifulSoup(cont, 'lxml')   # lpy
        comment_list = list()
        comments = soup.find(attrs={'node-type': 'comment_list'}).find_all(attrs={'node-type': 'root_comment'})

        for comment in comments:
            wb_comment = dict()
            try:
                cont = []
                first_author = True
                first_colon = True
                for content in comment.find(attrs={'class': 'WB_text'}).contents:
                    if not content:
                        continue
                    if content.name == 'a':
                        if first_author:
                            first_author = False
                            continue
                        else:
                            if content.text:
                                cont.append(content.text)

                    elif content.name == 'img':
                        img_title = content.get('title', '')
                        if img_title == '':
                            img_title = content.get('alt', '')
                        if img_title == '':
                            img_src = content.get('src', '')
                            img_src = img_src.split('/')[-1].split('.', 1)[0]
                            try:
                                img_title = emoji_tools.softband_to_utf8(img_src)
                            except Exception as e:
                                logger.exception('解析表情失败，具体信息是{},{}'.format(e, comment))
                                img_title = ''
                        cont.append(img_title)

                    else:
                        if first_colon:
                            if content.find('：') == 0:
                                cont.append(content.replace('：', '', 1))
                                first_colon = False
                        else:
                            cont.append(content)

                wb_comment['S'] = "zicai"
                wb_comment['content'] = ''.join(cont).strip()
                wb_comment['user_id'] = comment.find(attrs={'class': 'WB_text'}).find('a').get('usercard')[3:]
                wb_comment['userid'] = wb_comment['user_id']
                wb_comment['source_url'] = blog_url_
                wb_comment['url'] = blog_url_
                wb_comment['user_name'] = comment.find(attrs={'class': 'WB_text'}).find('a').text
                wb_comment['author'] = wb_comment['user_name']
                wb_comment['article_type'] = 2
                wb_comment['mblog_type'] = 2
                wb_comment['article_id'] = m_blog_id
                wb_comment['mblog_id'] = m_blog_id
                wb_comment['mid'] = m_blog_id
                wb_comment['language'] = 1
                wb_comment['host'] = 'weibo.com'
                # 日期格式化
                create_time = comment.find(attrs={'class': 'WB_from S_txt2'}).text
                wb_comment['pubtime'] = parse_date_time(create_time)
                wb_comment['crawler_no'] = self.ip
                wb_comment['crawler_type'] = 1
                wb_comment['media_type'] = 1
                # 点赞量 评论量 转发量 评论无转发量
                up_count = 0
                try:
                    p = re.search(r"\d+", comment.select("*[node-type$='like_status'] > em")[1].get_text())
                    if p:
                        up_count = int(p.group())
                except Exception as e:
                    print("up_count 参数,类型转换错误：", e)
                wb_comment['up_count'] = up_count
                wb_comment['upcount'] = wb_comment['up_count']
                more = comment.find(attrs={'class', 'list_li_v2'})
                cmt_count = 0
                try:
                    if more:
                        cmt_count = int(re.search(r"\d+", more.select("a[action-type$='login']")[0].get_text()).group())
                except Exception as e:
                    print("cmt_count参数,类型转换错误：", e)

                wb_comment['cmt_count'] = cmt_count
                wb_comment['commtcount'] = wb_comment['cmt_count']
                wb_comment['comment_num'] = wb_comment['cmt_count']
                wb_comment['rtt_count'] = 0
                wb_comment['share_num'] = 0
                # 计算
                interaction_count = 0
                c = wb_comment['up_count']
                if isinstance(c, int):
                    interaction_count += c
                c2 = wb_comment['cmt_count']
                if isinstance(c2, int):
                    interaction_count += c2

                wb_comment['interaction_count'] = interaction_count
                wb_comment['interaction_num'] = wb_comment['interaction_count']
                wb_comment['region'] = 0
                wb_comment['insert_time'] = str(datetime.datetime.now()).split('.')[0]
                wb_comment['comments_id'] = comment['comment_id']
                wb_comment['root_id'] = wb_comment['comments_id']
                uuid = hash_md5(wb_comment['comments_id'])
                wb_comment['uuid'] = uuid
                wb_comment['md5'] = uuid

                if more:
                    # 发送id给二级评论抓取脚本
                    data = {
                        'comments_id': wb_comment['comments_id'],
                        'url': wb_comment['url']
                    }
                    self.client.lpush(redis_comment_key, json.dumps(data))
                    logger.info(f"添加二级评论id:[{data}]成功!")

            except Exception as e:
                logger.exception('解析评论失败，具体信息是{}'.format(e))
            else:
                comment_list.append(wb_comment)

        # 获取下一页评论
        comment_loading = soup.find(attrs={'node-type': 'comment_loading'}) or \
                          soup.find(attrs={'class': 'WB_cardmore S_txt1 S_line1 clearfix'})
        next_url = ''
        if comment_loading:
            attr = comment_loading['action-data']
            next_url = "https://weibo.com/aj/v6/comment/big?ajwvr=6&{}&from=singleWeiBo&__rnd={}"\
                .format(attr, get_13_time_stamp())
            logger.info("下一页的请求url:{}", next_url)
        return comment_list, next_url

    def get_comment(self, blog_url):
        """
         启动
        """
        # 1.需要把要采集的博文查询出来
        # 2.对博文的一级评论进行采集
        # 3.把二级评论给另外的采集器

        # bid = blog_url[blog_url.rfind("/") + 1:].replace('\n', '')
        mid = blog_url[blog_url.rfind("/") + 1:].replace('\n', '') # lpy
        # if not bid and len(bid) < 9:
        #     logger.info("不合法的bid:", bid)
        #     return

        # mid = bid2mid(bid)   # 博文id转换成评论id
        next_url = self.base_url.format(mid)

        while next_url:
            try:
                response = requests.get(url=next_url, headers=self.headers, timeout=60, verify=False)
            except Exception as e:
                logger.exception(e)
                break
            else:
                comment_list, url = self.get_comment_list(response.text, mid, blog_url.replace("\n", ""))
                next_url = url
                if comment_list:

                    logger.info("当前抓取的评论id:[{}],抓取的评论数量:[{}]".format(mid, len(comment_list)))
                    logger.debug(pretty_json(comment_list))
                # 数据缓存至队列
                for comment in comment_list:
                    data_queue.put(comment)
            finally:
                time.sleep(3)

    def run(self):
        while True:
            line = self.client.lpop(redis_blog_key)
            if not line:
                time.sleep(3)
                continue
            if isinstance(line, bytes):
                line = str(line, encoding="utf-8")        # 需要采集的评论链接
            logger.info("当前抓取的微博文章url:{}", line)
            self.get_comment(line)    # 开始采集
            time.sleep(3)


if __name__ == '__main__':
    pass

    # print(json.loads(c.rpop("MBLOG_COMMENT:COMMENT_LIST")))
    # s = SinaComment(c)
    # s.start()
