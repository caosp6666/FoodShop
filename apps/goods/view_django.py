#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : AlbertC
# @Software: PyCharm


from django.views.generic.base import View
from .models import Goods


class GoodsListView(View):
    def get(self, request):
        """
        通过django的view实现商品列表页
        :param request:
        :return:
        """
        json_list = []
        goods = Goods.objects.all()[:10]

        # 方法一：使用手动添加
        # for good in goods:
        #     json_dict = {}
        #     json_dict["name"] = good.name
        #     json_dict["category"] = good.category.name
        #     json_dict["market_price"] = good.market_price
        #     # json_dict["add_time"] = good.add_time  # 这个字段无法通过json.dumps序列化
        #     json_list.append(json_dict)
        # from django.http import HttpResponse
        # import json
        # return HttpResponse(json.dumps(json_list), content_type="application/json")

        # 方法二：使用model_to_dict，同样会有字段不能序列化的问题
        # from django.forms.models import model_to_dict
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)
        # from django.http import HttpResponse
        # import json
        # return HttpResponse(json.dumps(json_list), content_type="application/json")

        # 方法三：使用django的serializers进行序列化
        import json
        from django.core import serializers
        json_data = serializers.serialize("json", goods)
        json_data = json.loads(json_data)
        from django.http import JsonResponse
        return JsonResponse(json_data, safe=False)



