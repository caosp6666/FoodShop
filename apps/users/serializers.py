#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm
import re
import datetime
from rest_framework import serializers
from django.contrib.auth import get_user_model
from MyFoodshop.settings import REGEX_MOBILE
from .models import VerifyCode

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """
    不用ModelSerializer是因为发送验证码的时候表单中没有code字段，而code是必填字段
    """
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        # 是否已经注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("该手机号已注册")

        # 手机号码是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("该手机号不合法")

        # 上次发送时间，频率限制
        one_minute_ago = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minute_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送时间过短")  # 这里一般前端也会限制，这是为了防止黑客

        return mobile
