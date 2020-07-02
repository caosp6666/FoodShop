from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics


from .models import Goods
from .serializers import GoodsSerializer


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
    queryset = Goods.objects.all()[:10]
    serializer_class = GoodsSerializer
