#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm
import re
import datetime
import redis
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from MyFoodshop.settings import REGEX_MOBILE, REDIS_PORT, REDIS_HOST
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

        # 如果使用redis
        # from MyFoodshop.secret_key import REDIS_HOST, REDIS_PORT
        # red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf8', decode_responses=True)
        # ttl = red.ttl(mobile)  # 设置了5分钟，如果剩余时间大于4分钟就说明间隔过短
        # if ttl > 4 * 60:
        #     raise serializers.ValidationError("距离上一次发送时间过短")  # 这里一般前端也会限制，这是为了防止黑客

        return mobile


class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=4, min_length=4,
                                 label='验证码',  # 注意与help text的区别
                                 write_only=True,  # 防止返回时候报错
                                 error_messages={
                                     # 设置验证错误时返回的信息内容
                                     "blank": "请验证",  # 空的时候显示这里的信息，注意跟下面的区别
                                     "required": "请输入验证码",  # 如果没有post这个字段就显示请输入验证码
                                     "max_length": "验证码过长",
                                     "min_length": "验证码过短",
                                 },
                                 help_text="验证码")
    username = serializers.CharField(required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已存在")])
    password = serializers.CharField(
        style={'input_type': 'password'},
        label='密码',
        write_only=True,
    )

    def create(self, validated_data):
        user = super(RegisterSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    def validate_code(self, code):
        verify_code_record = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        print(verify_code_record)
        if verify_code_record:
            last_record = verify_code_record[0]
            five_minutes_ago = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=5, seconds=0)
            if five_minutes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码已过期")
            if last_record.code != code:
                # print(type(last_record), type(code))
                # print(last_record, code)
                raise serializers.ValidationError("验证码错误")

            return code  # 不return也行，因为没有这个字段
        else:
            raise serializers.ValidationError("验证码不存在")

        # # 用redis
        # red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf8', decode_responses=True)
        # verify_code_record = red.get(self.initial_data["mobile"])  # 只会取到一个值，发送多条默认是最后一条覆盖的
        # if verify_code_record is None:
        #     raise serializers.ValidationError("验证码不存在")
        # elif verify_code_record != code:
        #     raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        attrs["mobile"] = attrs["username"]  # 添加字段
        del attrs["code"]  # 删除字段
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
