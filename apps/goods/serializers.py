#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from rest_framework import serializers
from .models import Goods, GoodsCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()
#
#     def create(self, validated_data):
#         return Goods.objects.create(**validated_data)


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Goods
        # fields = ('name', 'click_num', 'shop_price', 'goods_front_image', 'add_time')
        fields = "__all__"
