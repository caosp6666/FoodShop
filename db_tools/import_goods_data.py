#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm


import sys
import os


pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd+"../")  # 将项目主文件夹添加到sys.path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyFoodshop.settings')

import django

django.setup()

from apps.goods.models import Goods, GoodsCategory, GoodsImage
from db_tools.data.product_data import row_data

for good_detail in row_data:
    goods = Goods()
    goods.name = good_detail["name"]
    goods.market_price = float(int(good_detail["market_price"].replace("￥", "").replace("元", "")))
    goods.shop_price = float(int(good_detail["sale_price"].replace("￥", "").replace("元", "")))
    goods.goods_brief = good_detail["desc"] if good_detail["desc"] is not None else ""
    goods.goods_desc = good_detail["goods_desc"] if good_detail["goods_desc"] is not None else ""
    goods.goods_front_image = good_detail["images"][0] if good_detail["images"] else ""

    category_name = good_detail["categorys"][-1]
    category = GoodsCategory.objects.filter(name=category_name)
    if category:
        goods.category = category[0]
    goods.save()

    for good_image in good_detail["images"]:
        good_image_instance = GoodsImage()
        good_image_instance.image = good_image
        good_image_instance.goods = goods
        good_image_instance.save()
