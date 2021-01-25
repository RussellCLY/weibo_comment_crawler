import json
import os
from io import BytesIO
from pyzbar import pyzbar
from PIL import Image, ImageEnhance
import requests
import re
from urllib.parse import quote

from sina_weibo.utils.date_tools import get_13_time_stamp

"""
mac需要安装 brew install zbar
windows:pip install pyzbar
"""

#
# def get_ewm(img_adds, show=True):
#     """ 读取二维码的内容： img_adds：二维码地址（可以是网址也可是本地地址 """
#     if os.path.isfile(img_adds):
#         # 从本地加载二维码图片
#         img = Image.open(img_adds)
#         if show:
#             img.show()
#     else:
#         # 从网络下载并加载二维码图片
#         rq_img = requests.get(img_adds).content
#         img = Image.open(BytesIO(rq_img))
#
#     # img.show()  # 显示图片，测试用
#
#     txt_list = pyzbar.decode(img)
#
#     for txt in txt_list:
#         barcode_data = txt.data.decode("utf-8")
#         # print(barcodeData)
#     return barcode_data
#
#
# session = requests.session()
#
# url = "https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_{}1".format(get_13_time_stamp())
#
# headers = {
#     'Connection': 'keep-alive',
#     'Pragma': 'no-cache',
#     'Cache-Control': 'no-cache',
#     'Upgrade-Insecure-Requests': '1',
#     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'Sec-Fetch-Site': 'none',
#     'Sec-Fetch-Mode': 'navigate',
#     'Sec-Fetch-User': '?1',
#     'Sec-Fetch-Dest': 'document',
#     'Accept-Language': 'zh-CN,zh;q=0.9'
# }
#
# response = session.get(url, headers=headers)
#
# try:
#     rq_json = json.loads(re.search("{[^}]*}}", response.text).group())
#
#     rq_url = 'https://v2.{}'.format(rq_json['data']['image'].replace('//', ''))
#
#     res = session.get(rq_url, headers=headers)
#
#     with open('code.png', mode='wb') as f:
#         f.write(res.content)
#
#     pass_qr_url = get_ewm('./code.png')
#     session.get(pass_qr_url, headers=headers)
#
#     url = "https://passport.weibo.cn/signin/login?entry=mweibo&r={}".format(quote(pass_qr_url))
#     r = session.get(url, headers=headers,timeout =15)
#     print(r.text)
#
#
#
# except Exception as e:
#     print(e)
# print(response.text)

# if __name__ == '__main__':
#     # 解析本地二维码
#     # get_ewm('./code.png')
#     print()

# 解析网络二维码
# get_ewm('https://gqrcode.alicdn.com/img?type=cs&shop_id=445653319&seller_id=3035998964&w=140&h=140&el=q&v=1')


import requests

url = "https://api.weibo.cn/2/account/getcookie?c=weibolite" \
      "&s=cd3fc555" \
      "&from=37A6095010" \
      "&gsid=_2A25yrJjHDeRxGeBI6lET8S_OyzuIHXVv-6sPrDV6PUJbkdAKLXilkWpNRrEROn-uNe_iGAWaFtDhhUr43e5J2G_T"

payload = {}
headers = {}

response = requests.get(url, headers=headers, data=payload)

print(response.text)
