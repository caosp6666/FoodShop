from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from django_filters.rest_framework import DjangoFilterBackend

from apps.goods.models import Goods, GoodsCategory, Banner, HotSearchWords
from apps.goods.serializers import GoodsSerializer, CategorySerializer, BannerSerializer, HotSearchWordsSerializer, \
    IndexGoodsCategorySerializer
from apps.goods.filters import GoodsFilter


class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'page'  # 决定next页面的url参数
    max_page_size = 100


class GoodsListAPIView(APIView):
    """
    list all goods
    """

    def get(self, request, format=None):
        goods = Goods.objects.all()[:10]
        goods_serializer = GoodsSerializer(goods, many=True)  # 因为是goods是list，多条数据要增加many=True
        return Response(goods_serializer.data)

    # def post(self, request, format=None):
    #     serializer = GoodsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GoodsListView(mixins.ListModelMixin, generics.GenericAPIView):
#     queryset = Goods.objects.all()[:10]
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#     # 如果不重写这个get，会返回：get方法不允许
#     # 以上操作就相当于ListAPIView


class GoodsListView(generics.ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination


# 手动实现过滤操作
# class GoodsListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     # queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination
#
#     def get_queryset(self):
#         queryset = Goods.objects.all()  # 这里只是拼接了sql，并不会查询数据库所有数据
#         price_min = self.request.query_params.get("price_min", 0)
#         if price_min:
#             queryset = queryset.filter(shop_price__gt=int(price_min))
#         return queryset


class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    # filter_fields = ('name', 'market_price', )
    filter_class = GoodsFilter
    search_fields = ['name', 'goods_brief', 'goods_desc']
    ordering_fields = ['sold_num', 'shop_price']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品分类数据
    """
    # queryset = GoodsCategory.objects.all()
    queryset = GoodsCategory.objects.filter(category_type=1)  # 获取第一大类
    serializer_class = CategorySerializer


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    获取轮播图列表
    """
    queryset = Banner.objects.all().order_by("index")
    serializer_class = BannerSerializer


class HotSearchWordsViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    获取热搜词
    """
    queryset = HotSearchWords.objects.all().order_by("-search_nums")[:4]
    serializer_class = HotSearchWordsSerializer


class IndexGoodsCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    主页的分类展示列表
    """
    queryset = GoodsCategory.objects.filter(is_tab=True)
    serializer_class = IndexGoodsCategorySerializer
