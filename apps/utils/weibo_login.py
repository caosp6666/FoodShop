#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from MyFoodshop.secret_key import WEIBO_APP_KEY, WEIBO_APP_SECRET
import requests


def get_auth_url():
    weibo_auth_url = 'https://api.weibo.com/oauth2/authorize'
    redirect_url = 'http://127.0.0.1:8000/weibo'
    client_id = WEIBO_APP_KEY
    auth_url = weibo_auth_url + '?client_id=' + client_id + '&redirect_uri=' + redirect_url

    return auth_url


def get_access_token(code):
    access_token_url = 'https://api.weibo.com/oauth2/access_token'
    post_data = {
        "client_id": WEIBO_APP_KEY,
        "client_secret": WEIBO_APP_SECRET,
        "grant_type": 'authorization_code',
        "code": code,
        "redirect_uri": 'http://127.0.0.1:8000/complete/weibo',
    }
    re_dict = requests.post(access_token_url, data=post_data)
    return re_dict


def get_user_info(access_token, uid):
    user_show_url = 'https://api.weibo.com/2/users/show.json?access_token=' + access_token + '&uid=' + uid
    return user_show_url


if __name__ == '__main__':
    print(get_auth_url())
    # message = get_access_token('3145947986bcc787d383ceed3cb60d12')
    # print(message.text)
    #
    # print(get_user_info('2.006grI6GmwMzZE6d6c0d915c07p5dP', "5868318377"))

    # 1.拼接auth_url给用户
    # 2.用户访问，登陆，授权
    # 3.获取授权后的回调url中code参数
    # 4.将code等参数post到token_url，返回的message.text可以获取access_token和uid
    # 5.使用access_token和uid访问user/show的API，获取用户信息
    # 6.查询数据库中是否有这个用户，如果没有就创建一个，如果有就用这个用户登陆
