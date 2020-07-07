#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from apps.user_operations.models import UserFav
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
