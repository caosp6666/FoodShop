#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

import requests
import json
from MyFoodshop.secret_key import yunpian_api_key


class YunPian(object):
    def __init__(self, apikey, mobile):
        self.API_KEY = apikey
        self.url = 'https://sms.yunpian.com/v2/sms/single_send.json'
        self.mobile = mobile

    def send(self, code):
        data = {
            "apikey": self.API_KEY,
            "mobile": self.mobile,
            # "text": '【曹松鹏个人学习使用】您的验证码是{}。如非本人操作，请忽略本短信'.format(code)
            "text": "【深圳市天蓝色软件服务有限公司】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        res = requests.post(self.url, data)  # 这里res返回是json数据
        res_dict = json.loads(res.text)
        return res_dict


if __name__ == '__main__':
    # 以下是测试
    yunpian = YunPian(yunpian_api_key, '17804304121')
    res_json = yunpian.send('1234')
    code = res_json['code']
    msg = res_json['msg']
    if code == 0:
        print('发送成功')
    else:
        print('发送失败：{}'.format(msg))
