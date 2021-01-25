import re
import datetime
import time


def ctime_to_number_time(ctime_):
    """
    将中文时间转成数字时间
    :param ctime_: 需要转换的中文时间
    :return: 转换后的数字时间
    """
    ctime_ = ctime_.replace("二十一", "21")
    ctime_ = ctime_.replace("二十二", "22")
    ctime_ = ctime_.replace("二十三", "23")
    ctime_ = ctime_.replace("二十四", "24")
    ctime_ = ctime_.replace("二十五", "25")
    ctime_ = ctime_.replace("二十六", "26")
    ctime_ = ctime_.replace("二十七", "27")
    ctime_ = ctime_.replace("二十八", "28")
    ctime_ = ctime_.replace("二十九", "29")

    ctime_ = ctime_.replace("三十一", "31")
    ctime_ = ctime_.replace("三十", "30")
    ctime_ = ctime_.replace("十一", "11")
    ctime_ = ctime_.replace("十二", "12")
    ctime_ = ctime_.replace("十三", "13")
    ctime_ = ctime_.replace("十四", "14")
    ctime_ = ctime_.replace("十五", "15")
    ctime_ = ctime_.replace("十六", "16")
    ctime_ = ctime_.replace("十七", "17")
    ctime_ = ctime_.replace("十八", "18")
    ctime_ = ctime_.replace("十九", "19")
    ctime_ = ctime_.replace("二十", "20")

    ctime_ = ctime_.replace("一", "1")
    ctime_ = ctime_.replace("二", "2")
    ctime_ = ctime_.replace("三", "3")
    ctime_ = ctime_.replace("Ｏ", "0")
    ctime_ = ctime_.replace("〇", "0")
    ctime_ = ctime_.replace("o", "0")
    ctime_ = ctime_.replace("O", "0")
    ctime_ = ctime_.replace("零", "0")
    ctime_ = ctime_.replace("四", "4")
    ctime_ = ctime_.replace("五", "5")
    ctime_ = ctime_.replace("六", "6")
    ctime_ = ctime_.replace("七", "7")
    ctime_ = ctime_.replace("八", "8")
    ctime_ = ctime_.replace("九", "9")
    ctime_ = ctime_.replace("十", "10")

    ctime_ = ctime_.replace("年", "-")
    ctime_ = ctime_.replace("月", "-")
    ctime_ = ctime_.replace("日", " ")
    ctime_ = ctime_.replace("/", "-")
    ctime_ = ctime_.replace(".", "-")
    ctime_ = ctime_.replace(" ", "-")
    if re.compile("(\d{4}-\d{1,2}-\d{1,2})").search(ctime_.strip()):
        number_time = re.compile("(\d{4}-\d{1,2}-\d{1,2})").search(ctime_).group()
        return number_time


# 获取一段时间的列表
def get_range_date(start_date: str, end_date: str, step=1):
    """
    start_date，end_date都应该满足yyyy-mm-dd的格式
    :param start_date: 开始时间
    :param end_date: 结束时间
    :param step: 递增天数
    :return: 返回生成后的时间列表
    """
    start_child = start_date.split("-")
    start_time = datetime.date(
        int(start_child[0]),
        int(start_child[1]),
        int(start_child[2])
    )

    end_child = end_date.split("-")
    end_time = datetime.date(
        int(end_child[0]),
        int(end_child[1]),
        int(end_child[2])
    )
    day_range = list()
    day = start_time
    for i in range((end_time - start_time).days // step + 2):
        if day > end_time:
            day_range.append(str(end_time))
        else:
            day_range.append(str(day))
        day = day + datetime.timedelta(days=step)

    return day_range


# 获取指定间隔的时间元祖
def get_between_date(start_date: str, end_date: str, step=1):
    date_list = get_range_date(start_date, end_date, step)
    date_tuple_list = []
    for index, date in enumerate(date_list):
        if end_date == date:
            continue
        date_tuple_list.append((date, date_list[index + 1]))
    return date_tuple_list


def getYesterday():
    """获取去年的今天"""
    today = datetime.date.today()
    one_day = datetime.timedelta(days=365)
    yesterday = today - one_day
    return yesterday


def get_before_30_date(n):
    """获取前n天的日期"""
    day = datetime.datetime.now() - datetime.timedelta(days=n)
    before_n_day = datetime.datetime(day.year, day.month, day.day).strftime('%Y-%m-%d')
    return before_n_day


def get_7_time(recently_n_week):
    dayOfWeek = datetime.datetime.now().isoweekday()
    now_time = datetime.datetime.now()
    start_time = now_time - datetime.timedelta(days=int(dayOfWeek - 1))
    end_time = now_time + datetime.timedelta(days=int(7 - dayOfWeek))
    # 计算出前几周
    time_list = [{"start_time": start_time.strftime("%Y-%m-%d"), "end_time": end_time.strftime("%Y-%m-%d")}]
    for i in range(1, recently_n_week):
        time_list.append({
            "start_time": (start_time - datetime.timedelta(days=int(i * 7))).strftime("%Y-%m-%d"),
            "end_time": (end_time - datetime.timedelta(days=int(i * 7))).strftime("%Y-%m-%d")
        })
    return time_list


def get_date_list(days):
    """返回前days天日期列表"""
    date_list = list()
    for i in range(0, days):
        day = datetime.datetime.now() - datetime.timedelta(days=i)
        date_to = datetime.datetime(day.year, day.month, day.day).date()
        date_list.append(date_to)
    return date_list


def parse_date_time(create_time):
    """
    解析时间
    @param create_time: 网页上原始时间
    @return: 返回标识时间格式
    """

    if '秒前' in create_time:
        now = datetime.datetime.now()
        reduce_minute = create_time.strip().split('秒前')[0]
        delta = datetime.timedelta(seconds=int(reduce_minute))
        real_time = now - delta
        date_time = str(real_time.strftime('%Y-%m-%d %H:%M:%S'))
    elif '分钟前' in create_time:
        now = datetime.datetime.now()
        reduce_minute = create_time.strip().split('分钟')[0]
        delta = datetime.timedelta(minutes=int(reduce_minute))
        real_time = now - delta
        date_time = str(real_time.strftime('%Y-%m-%d %H:%M'))
    elif '今天' in create_time:
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        real_time = now + create_time.strip().split('今天')[-1]
        date_time = str(real_time)
    elif '楼' in create_time:
        date_time = str(re.sub('第\d*楼', '', create_time))
    else:
        date_time = create_time
    if not date_time.startswith('202'):
        date_time = str(datetime.datetime.now().year) + "年" + date_time
        # 中文时间戳转换成标准格式 "%Y-%m-%d %H:%M"
    create_time_copy = date_time
    if '月' in create_time_copy and '日' in create_time_copy:
        month = create_time_copy.split("年")[-1].split("月")[0]
        day = create_time_copy.split("年")[-1].split("月")[-1].split("日")[0]
        # 补齐0
        if month and int(month) < 10:
            date_time = date_time.replace(str(month) + "月",
                                          "0" + str(month) + "月")
        if day and int(day) < 10:
            date_time = date_time.replace(str(day) + "日", "0" + str(day) + "日")
        date_time = date_time.replace("月", "-")
        date_time = date_time.replace("日", "")
        if '年' in date_time:
            date_time = date_time.replace("年", "-")

    if len(date_time) < 17:
        date_time += ":00"
    return date_time


def format_Tue_time(time_str):
    """
     转换时间 "Tue Sep 22 10:36:58 +0800 2020"
    """
    date = time_str.replace('+0800', '')
    new_date = time.strptime(date, '%a %b %d %H:%M:%S %Y')
    # 转换为正常时间
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.mktime(new_date))))


def get_13_time_stamp() -> int:
    """
    @return:
    """
    return int(round(time.time() * 1000))


def get_current_time():
    return str(datetime.datetime.now()).split('.')[0]


if __name__ == '__main__':
    # print(parse_date_time("今天 09:35"))
    print(get_before_30_date(1) + " 00:00:00")
