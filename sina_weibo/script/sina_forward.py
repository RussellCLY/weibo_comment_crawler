import datetime
import json
import re
import sys
import threading
import time
from queue import Queue

import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger

sys.path.append("./")
from sina_weibo.utils import emoji_tools
from sina_weibo.utils.com_tools import hash_md5, get_public_ip, pretty_json, bid2mid
from sina_weibo.utils.date_tools import parse_date_time
from sina_weibo.utils.upload_tools import uploading_data
from sina_weibo.task.es_task import Task

urllib3.disable_warnings()

task_queue = Queue()

data_queue = Queue()


class SinaForward:

    def __init__(self):
        super().__init__()
        self.base_url = 'https://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id={}&__rnd=1605182897017'
        self.headers = {
            'authority': 'weibo.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'SUB=_2AkMo8BOEdcPxrARUmfkdyWjnZY1H-jybJXpyAn7uJhMyOhh87goCqSVutBF-XLf42aUjkmeJSQ3_mD1Bu7h2xaNp; '
                      'SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WhXMxSEC0D1eyOTQ7g9Y12G5JpVF02fSKMfeKeNShzf;'
                      ' _s_tentry=passport.weibo.com; Apache=8784975572746.782.1605147828657; SINAGLOBAL=8784975572746.782.1605147828657; '
                      'ULV=1605147828708:1:1:1:8784975572746.782.1605147828657:; wb_view_log=1440*9002; WBtopGlobal_register_version=2020111211'
        }
        self.ip = get_public_ip()

    def get_html_cont(self, html):
        """
        获取评论html
        @param html:原始页面
        @return:
        """
        cont = ''
        try:
            data = json.loads(html).get('data', '')
        except Exception as e:
            print("页面解析错误:", e, html)
        else:
            if data:
                cont = data.get('html', '')
            return cont

    def get_forward_list(self, html, blog_id, blog_url_):
        """
        获取评论列表
        @param blog_id: 博文id
        @param blog_url_:博文url
        @param html: 文本
        :return:
        """
        cont = self.get_html_cont(html)
        soup = BeautifulSoup(cont, 'html5lib')
        forwards = soup.find_all(attrs={'class': 'list_con'})
        forwards_list = list()
        for forward in forwards:
            wb_forward = dict()
            try:
                topic_list = set()
                cont = []
                for content in forward.find(attrs={'class': 'WB_text'}).find(attrs={'node-type': 'text'}).contents:
                    if not content:
                        continue
                    if content.name == 'a':
                        tp = content.get('class')
                        if tp:
                            if tp[0] and tp[0] == 'a_topic':
                                topic_list.add(content.text.replace("#", ""))
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
                                print('解析表情失败，具体信息是{}'.format(e))
                                img_title = ''
                        cont.append(img_title)
                    else:
                        cont.append(content)

                wb_forward['S'] = "zicai"
                wb_forward['content'] = ''.join(cont).strip()
                wb_forward['user_id'] = forward.find(attrs={'class': 'WB_text'}).find('a').get('usercard')[3:]
                wb_forward['userid'] = wb_forward['user_id']

                forward_info = forward.find(attrs={'class': 'WB_from S_txt2'})
                source_url = forward_info.a.get('href').replace("https", "http")
                bid = source_url[source_url.rfind("/") + 1:]
                mid = bid2mid(bid)

                wb_forward['source_url'] = source_url
                wb_forward['url'] = source_url
                wb_forward['user_name'] = forward.find(attrs={'class': 'WB_text'}).find('a').text
                wb_forward['author'] = wb_forward['user_name']
                wb_forward['article_type'] = 1
                wb_forward['mblog_type'] = 1
                wb_forward['article_id'] = mid
                wb_forward['mblog_id'] = mid
                wb_forward['mid'] = mid
                wb_forward['language'] = 1
                wb_forward['host'] = 'weibo.com'

                wb_forward['ref_url'] = blog_url_
                wb_forward['ref_id'] = blog_id
                wb_forward['retweet_id'] = blog_id
                # 日期格式化
                wb_forward['pubtime'] = parse_date_time(forward_info.text)
                wb_forward['crawler_no'] = self.ip
                wb_forward['crawler_type'] = 2
                wb_forward['media_type'] = 2
                # 点赞量 评论量 转发量 评论无转发量
                up_count = 0
                try:
                    element = forward.select("*[node-type$='like_status'] > em")
                    if element:
                        p = re.search(r"\d+", element[1].get_text())
                        if p:
                            up_count = int(p.group())
                except Exception as e:
                    print("up_count 参数,类型转换错误：", e)
                wb_forward['up_count'] = up_count
                wb_forward['upcount'] = wb_forward['up_count']
                wb_forward['cmt_count'] = 0
                wb_forward['comment_num'] = wb_forward['cmt_count']
                wb_forward['commtcount'] = wb_forward['cmt_count']

                rtt_count = 0
                try:
                    ele = forward.find(attrs={'action-type': 'feed_list_forward'})
                    if ele:
                        p = re.search(r"\d+", ele.get_text())
                        if p:
                            rtt_count = int(p.group())
                except Exception as e:
                    print("up_count 参数,类型转换错误：", e)

                wb_forward['rtt_count'] = rtt_count
                wb_forward['share_num'] = wb_forward['rtt_count']
                wb_forward['interaction_count'] = wb_forward['up_count'] + wb_forward['cmt_count'] + wb_forward[
                    'rtt_count']
                wb_forward['interaction_num'] = wb_forward['interaction_count']
                wb_forward['region'] = 0
                wb_forward['insert_time'] = str(datetime.datetime.now()).split('.')[0]
                if topic_list:
                    wb_forward['mblog_topic'] = str(list(topic_list))
                uuid = hash_md5(source_url)
                wb_forward['uuid'] = uuid
                wb_forward['md5'] = uuid
            except Exception as e:
                print(e)
            else:
                forwards_list.append(wb_forward)

        return forwards_list, ''

    def get_comment(self, blog_url):
        """
         启动
        """
        # 1.需要把要采集的博文查询出来
        # 2.对博文的一级评论进行采集
        # 3.把二级评论给另外的采集器

        bid = blog_url[blog_url.rfind("/") + 1:].replace('\n', '')
        if not bid and len(bid) < 9:
            print("不合法的bid:", bid)
            return

        try:
            mid = bid2mid(bid)
        except:
            return
        next_url = self.base_url.format(mid)
        while next_url:
            try:
                response = requests.get(url=next_url, headers=self.headers, timeout=60, verify=False)
            except Exception as e:
                logger.error(e)
            else:
                comment_list, url = self.get_forward_list(response.text, mid, blog_url.replace("\n", ""))
                next_url = url
                if comment_list:
                    logger.debug(pretty_json(comment_list))
                for comment in comment_list:
                    data_queue.put(comment)
            finally:
                time.sleep(3)

    def run(self):
        while True:
            print('#'*20)
            if task_queue.qsize():
                blog_url = task_queue.get()
                if blog_url:
                    logger.info("当前抓取的微博文章url:{}", blog_url)
                    self.get_comment(blog_url)
            else:
                time.sleep(2)


def push_task():
    while True:
        task = Task()
        for _ in task.generate_task_list():
            print("获取的任务url:" + _)
            task_queue.put(_)
        time.sleep(80000)  # 每八分钟获取一次任务


def upload():
    while True:
        if data_queue.qsize():
            data = data_queue.get()
            uploading_data(data)
        else:
            time.sleep(5)


if __name__ == '__main__':
    t = threading.Thread(target=push_task)
    u = threading.Thread(target=upload)
    s = SinaForward()
    t.start()
    u.start()
    s.run()
