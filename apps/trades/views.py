from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from utils.permissions import IsOwnerOrReadOnly
from apps.trades.models import ShoppingCart, OrderInfo, OrderGoods
from apps.trades.serializers import ShoppingCartSerializer, ShoppingCartDetailSerializer, OrderInfoSerializer, \
    OrderDetailSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车
    list:
        查看当前用户购物车
    create:
        添加购物车
    delete:
        删除购物车
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ShoppingCartSerializer
    lookup_field = "goods_id"

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ShoppingCartDetailSerializer
        else:
            return ShoppingCartSerializer


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """
    订单管理
    list:
        获取个人订单列表
    delete:
        删除订单
    create:
        创建订单
    retrieve:
        查看订单详情
    """
    # 因为不允许修改订单，因此没有用ModelViewSet
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderInfoSerializer

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save()

        shop_cart = ShoppingCart.objects.filter(user=self.request.user)
        for good in shop_cart:
            order_good = OrderGoods()
            order_good.goods = good.goods
            order_good.goods_num = good.nums
            order_good.order = order
            order_good.save()

            good.delete()

        return order

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        else:
            return OrderInfoSerializer
