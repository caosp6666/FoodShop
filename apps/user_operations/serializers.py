#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.user_operations.models import UserFav, UserLeavingMessage, UserAddress
from apps.goods.serializers import GoodsSerializer


class UserFavSerializer(serializers.ModelSerializer):
    """
    用于提交收藏的类
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFav
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message="已经收藏",
            )
        ]
        fields = ('user', 'goods', 'id')


class UserFavListSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ("goods", "id")


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ("user", "message_type", "subject", "message", "file", "add_time", "id")


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserAddress
        fields = ("id", "user", "province", "city", "district", "address", "signer_name", "signer_mobile", "add_time")