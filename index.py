#!/usr/bin/python
# coding:utf-8
import requests
import ujson
import config
import time
import datetime
import sys
import os
import codecs
import random
from chinese_calendar import is_workday

headers = {
    'Cache-Control': "no-cache",
}
if sys.stdout.encoding is None:
    enc = os.environ['LANG'].split('.')[1]
    sys.stdout = codecs.getwriter(enc)(sys.stdout)


def get_mysess():
    """
    获取mysess
    """
    url = config.api_url + "get/hy_login_for_app"
    querystring = {
        "account": config.accout,
        "pwd": config.pwd,
        "role": "c",
        "style": "c_app"
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    return ujson.loads(response.text).get("body", {}).get("mysess")


def get_last_checking():
    """
    获取最后一条打卡记录
    """
    url = config.api_url + "get/vg_user_get_att_log"
    querystring = {
        "mysess": mysess,
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)
    checking_list = ujson.loads(response.text).get("body", {}).get("list", [])
    return checking_list[0].get("r_stamp")


def is_today(timestamp):
    """
    判断是否是今天
    """
    cur_time = time.time() * 1000
    cur_zero_time = cur_time - (cur_time % 86400000)
    f_zero_time = cur_zero_time + 86400000
    return (timestamp > cur_zero_time) and (timestamp < f_zero_time)


def is_checkin():
    """
    判断是否已经打卡
    """
    workday = is_workday(
        (datetime.datetime.fromtimestamp(time.time())))
    if not workday:
        print(u'不需要打卡')
        return
    last_checking = get_last_checking()
    last_checking_hour = time.localtime(last_checking / 1000).tm_hour
    now_hour = datetime.datetime.now().hour
    today = is_today(last_checking)
    if not today:
        print(u'上班没打卡，需要打卡')
        chekin()
        return
    if now_hour > 20 and last_checking_hour < 18:
        print(u'下班没打卡，需要打卡')
        chekin()
    else:
        print(u"打过卡了")


def chekin():
    """
    打卡
    """
    url = config.api_url + "post/vg_user_att_umpire"
    headers = {
        "user-agent": "wehomec 2.0.27 (iPhone; iOS 11.2.1; Scale 3.00)"}
    payload = {
        "mysess": mysess,
        "bssid": config.bssid,
        "bi_u_v_n": "2.0.27",
        "user_ip": "172.16.11.2",
        "bi_u_o_t": "2",
        "bi_u_o_v": "11.2.6",
        "lon": "121.420368",
        "lat": "31.215915",
    }
    time.sleep(random.randint(1200,3000))
    response = requests.post(url, headers=headers, data=payload)
    status = ujson.loads(response.text).get("status")
    if status == 200:
        print(u'打卡成功')
    else:
        print(u'打卡失败')


mysess = get_mysess()

if __name__ == '__main__':
    is_checkin()
