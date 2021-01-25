# @Time    : 2020/10/10 15:44
# @Author  : 胡已源
# @File    : proxy_test.py
# @Software: PyCharm
import datetime
import hashlib
import json
import time
import copy
import jsonpath
import redis
import requests
import urllib3

urllib3.disable_warnings()


class SinaAPP:
    """
    新浪微博互动粉丝榜
    """

    def __init__(self):
        self.target_url = "https://api.weibo.cn/2/cardlist"
        self.headers = {
            'Host': "api.weibo.cn",
            'User-Agent': "Pixel_9_weibo_10.10.0_android",
            'Accept': "*/*"
        }
        self.datalist = []
        self.query_dict = {
            "c": "android",
            "s": "ef0b978d",
            "uid": "",
            "from": "10AA095010",
            "gsid": "_2A25yi6p4DeRxGeBN4lcR-CrPzTyIHXVvALqwrDV6PUJbkdANLXf3kWpNRAfyczllWxQqGye1eLEcvrTPtFpXlxTQ",
            "count": "20",
            "containerid": "231051_-_fans_intimacy_-_6574978729",
            # "since_id": "3907753719_80.06345_40"
        }

    def __urlFlag(self, md):
        m = hashlib.md5()
        m.update(md.encode("utf-8"))
        return m.hexdigest()

    def get_sian_data(self, one_data):
        """
        提取数据
        """
        sian_data = {}
        try:

            sian_data['user_id'] = one_data['user']['id']
            sian_data['user_url'] = 'http://weibo.com/{}'.format(sian_data['user_id'])
            sian_data['md5'] = self.__urlFlag(sian_data['user_url'])
            sian_data['uuid'] = sian_data['md5']
            sian_data['user_name'] = one_data['user']['name']
            sian_data['S'] = 'zicai'
            sian_data['head_img_url'] = one_data['user']['profile_image_url']
            sian_data['insert_time'] = str(datetime.datetime.now()).split(".")[0]
            sian_data['fans_count'] = one_data['user']['followers_count']
            sian_data['follow_count'] = one_data['user']['friends_count']
            sian_data['is_verified'] = one_data['user']['verified']
            # old
            sian_data['userid'] = sian_data['user_id']
            sian_data['name'] = sian_data['user_name']
            sian_data['headimgurl'] = sian_data['head_img_url']
            sian_data['url'] = sian_data['user_url']
            sian_data['name'] = one_data['user']['name']
            sian_data['fanscount'] = sian_data['fans_count']
            sian_data['followcount'] = sian_data['follow_count']
            sian_data['verified'] = sian_data['is_verified']  # old

            # sian_data['verified_type'] = one_data['user']['verified_type']
        except Exception as e:
            print("get_channel_url：获取错误%s" % e)
        return sian_data

    def get_json_html(self, query_dict):
        """
        获取json数据
        """
        count = 3
        while True:
            try:
                rsp = requests.get(url=self.target_url, params=query_dict, timeout=10, verify=False)
                if rsp.status_code == 200:
                    return rsp.json()
            except Exception as e:
                print("get_channel_url：获取错误%s" % e)
            time.sleep(1)
            count -= 1
            if count < 1:
                break

    def list_parse(self, uid, since_id=''):

        self.query_dict['uid'] = uid
        self.query_dict['since_id'] = since_id
        list_data = self.get_json_html(copy.copy(self.query_dict))
        card_list = jsonpath.jsonpath(list_data, '$.cards[*].card_group[?(@.user)]')
        since_id = jsonpath.jsonpath(list_data, '$.cardlistInfo.since_id')

        if card_list:
            for card in card_list:
                data = self.get_sian_data(card)
                print(data)
                self.datalist.append(data)
            if since_id:
                self.list_parse(uid, since_id[0])
        else:
            self.save()

    def save(self):
        with open('fans.json', mode='w', encoding='utf-8')as f:
            f.write(json.dumps(self.datalist, ensure_ascii=False))

    # 能看到前500个互动粉丝
    def start(self, uid_list):
        for uid in uid_list:
            pass


if __name__ == '__main__':
    app = SinaAPP()
    # app.start(['7511853590'])
    app.list_parse('7511853590')