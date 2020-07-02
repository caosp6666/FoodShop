#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm


from django_filters import rest_framework as filters
from .models import Goods


class GoodsFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')  # contains代表包含，i代表不区分大小写

    class Meta:
        model = Goods
        fields = ['price_min', 'price_max', 'name', 'is_hot', 'is_new']
