

# ll = [1, 2, 3, 4, 56, 6]
#
# l2 = [x if x !=3 else breakpoint() for x in ll]
#
# print(l2)



def get_mid_list(uid):

    import requests
    from loguru import logger
    from jsonpath import jsonpath

    headers = {
        'Host':'api.weibo.cn',
        'user-agent':'Pixel_9_weibo_11.1.1_android',
        'x-log-uid':'1018216549367',
        'x-sessionid':'c43c43e4-1c99-46fa-9167-870f2f589745',
        'x-validator':'GydeV9hos/uMet05iwsZRlEqIiXSbepL96ePePfeDCw='
    }
    user_url = f"https://api.weibo.cn//2/profile/statuses?c=android&s=9e42271d&from=10B1195010&gsid=_2AkMXUuhTf8NhqwJRmfAXzW3naIR0zA_EieKhDhmIJRM3HRl-wT92qmITtRV6A17R0ctwmm_mGavgbLvfILR6ruMOV809&containerid=107603{uid}_-_WEIBO_SECOND_PROFILE_WEIBO"
    try:
        response = requests.get(url=user_url, headers=headers, timeout=20)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            mid_list = jsonpath(response.json(), '$.cards[*]..mid')
            return mid_list
        else:
            logger.error(f'请求失败,异常【{response.status_code}】')
    except Exception as e:
        logger.error(f'请求失败,异常【{str(e)}】')


if __name__ == '__main__':
    pass
    uid_list = [
        "2812335943",
        "1640571365"
    ]
    for uid in uid_list:
        print(get_mid_list(uid))
    # uid = "2812335943"
    # uid = "1640571365"