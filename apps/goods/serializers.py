#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm

from rest_framework import serializers
from .models import Goods, GoodsCategory, GoodsImage, Banner, HotSearchWords, GoodsCategoryBrand, IndexAd


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

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

class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ('image',)


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        # fields = ('name', 'click_num', 'shop_price', 'goods_front_image', 'add_time')
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


class HotSearchWordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotSearchWords
        fields = ("keywords",)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


class IndexGoodsCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)  # 一级类别对应品牌
    goods = serializers.SerializerMethodField()  # 一级类别对应商品
    sub_cat = CategorySerializer2(many=True)  # 二级类别

    def get_goods(self, obj):
        from django.db.models import Q
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__father_category_id=obj.id) | Q(
            category__father_category__father_category_id=obj.id))
        goods = GoodsSerializer(all_goods, many=True)
        return goods.data

    class Meta:
        model = GoodsCategory
        fields = "__all__"
