#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import decodebytes, encodebytes
from urllib.parse import quote_plus, urlparse, parse_qs
from MyFoodshop.secret_key import ALI_APP_ID

import json


class Alipay(object):
    """
    支付宝支付类
    """

    def __init__(self, appid, app_private_key_path, alipay_public_key_path, return_url, app_notify_url, method,
                 debug=False):
        self.appid = appid
        self.app_private_key_path = app_private_key_path
        self.alipay_public_key_path = alipay_public_key_path
        self.app_notify_url = app_notify_url
        self.return_url = return_url
        self.method = method

        # 导入文件中的key
        with open(self.app_private_key_path) as f:
            self.app_private_key = RSA.importKey(f.read())  # 用于签名
        with open(self.alipay_public_key_path) as f:
            self.alipay_public_key = RSA.importKey(f.read())  # 用于验证

        if debug:
            # 测试环境
            self.__gateway = 'https://openapi.alipaydev.com/gateway.do'
        else:
            self.__gateway = 'https://openapi.alipay.com/gateway.do'

    @staticmethod
    def generate_biz_content(out_trade_no, total_amount, subject, **kwargs):
        """
        generate_biz_content
        :param subject: string
        :param out_trade_no: string
        :param total_amount: float
        :return:
        """
        biz_content = {
            'out_trade_no': out_trade_no,
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'total_amount': total_amount,
            'subject': subject,
        }
        biz_content.update(kwargs)  # 添加其他字段，默认是空的
        return biz_content

    def generate_public_params(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    @staticmethod
    def generate_ordered_data(data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        signer = PKCS1_v1_5.new(self.app_private_key)
        hash_string = SHA256.new(unsigned_string.encode("utf-8"))  # 生成一个sha256hash object
        signature = signer.sign(hash_string)
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def sign_data(self, data):
        ordered_data = self.generate_ordered_data(data)  # 将data dict转为一个有序的tuple list
        unsigned_string = "&".join("{0}={1}".format(key, value) for key, value in ordered_data)  # 拼接成用于签名的字符串
        sign = self.sign(unsigned_string)
        quoted_string = "&".join(
            "{0}={1}".format(key, quote_plus(value)) for key, value in ordered_data)  # 生成url的时候要对参数进行处理
        all_params = quoted_string + "&sign=" + quote_plus(sign)
        return all_params

    def pay(self, out_trade_no, total_amount, subject, **kwargs):
        biz_content = self.generate_biz_content(out_trade_no, total_amount, subject, **kwargs)
        public_params = self.generate_public_params(self.method, biz_content, self.return_url)
        all_params = self.sign_data(public_params)

        final_url = self.__gateway + '?' + all_params
        return final_url

    def check_sign(self, unsigned_string, ali_sign):
        # 开始计算签名，使用阿里给我们的公钥，对阿里返回的签名是否正确
        signer = PKCS1_v1_5.new(self.alipay_public_key)
        hash_string = SHA256.new(unsigned_string.encode('utf-8'))
        if signer.verify(hash_string, decodebytes(ali_sign.encode("utf8"))):
            return True
        return False

    def verify(self, query_test, ali_sign):
        # 排序，拼接
        ordered_data = self.generate_ordered_data(query_test)
        unsigned_string = "&".join("{0}={1}".format(key, value) for key, value in ordered_data)  # 排序后的字符串
        return self.check_sign(unsigned_string, ali_sign)


if __name__ == '__main__':
    alipay = Alipay(
        appid=ALI_APP_ID,
        app_private_key_path="../trades/keys/private_2048",
        alipay_public_key_path="../trades/keys/ali_key",
        app_notify_url="http://39.108.55.149:8000/alipay/return",
        return_url="http://39.108.55.149:8000/alipay/return",
        method="alipay.trade.page.pay",
        debug=True,  # 使用沙箱环境
    )

    test_url = alipay.pay(
        out_trade_no='202345611',
        total_amount=124,
        subject="测试订单"
    )

    print(test_url)


    # 思路是获取参数（将sign pop处出来），用支付宝公钥签名，然后跟支付宝的签名比对，一致即可
    # return_get_url = 'http://39.108.55.149:8000/?charset=utf-8&out_trade_no=2024567934511&method=alipay.trade.page.pay.return&total_amount=111.30&sign=Rn7UuWDzwbnvGmZXTz7b%2F0%2BscWbb8jhNP9N%2FIsB94TqY49CpxJqERRmNjoD9QIUjtJ62EXuYQ92%2FjVBspGKpyBDrPMKyJKXS5K1z%2BPcFnB56hm6zBOy3txDie0xonSFYgasXd4atS6yZCJnsxR9yeIstMb3OCl140Q%2BKp2d%2BY8nC3ExPEGTLzplg16DfOSOzoluV47OePh2FgR2dXJ1r60EBSgFlpLQ92C41u6idFCXUUEqrJeGemtJEBkuvJqdFyq0FLXkBhv%2FJq44NgdgvYGX4GDReZlgyprzL4%2BljEzRhbV9LcXfeAa5RoHK9IgRqf0TyaVhAwPT5TuQKTsUp3A%3D%3D&trade_no=2020071522001441490501326508&auth_app_id=2016102300744775&version=1.0&app_id=2016102300744775&sign_type=RSA2&seller_id=2088102180761534&timestamp=2020-07-15+17%3A14%3A07'
    # o = urlparse(return_get_url)  # 解析url
    # query = parse_qs(o.query)  # 解析参数
    # ali_sign = query.pop('sign')[0]  # 获得ali的sign
    # query_test = {}  # 其余的参数，保存为一个dict
    # for k, v in query.items():
    #     query_test[k] = v[0]  # 因为解析完的是数组
    # print(alipay.verify(query_test, ali_sign))
