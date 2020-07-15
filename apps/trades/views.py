from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from utils.permissions import IsOwnerOrReadOnly
from apps.goods.models import Goods
from apps.trades.models import ShoppingCart, OrderInfo, OrderGoods
from apps.trades.serializers import ShoppingCartSerializer, ShoppingCartDetailSerializer, OrderInfoSerializer, \
    OrderDetailSerializer
from utils.alipay import Alipay
from MyFoodshop.settings import ali_public_key_path, private_key_path
from MyFoodshop.secret_key import ALI_APP_ID


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


class OrderViewSet(viewsets.ModelViewSet):
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
        for buy in shop_cart:
            order_good = OrderGoods()
            order_good.goods = buy.goods
            order_good.goods_num = buy.nums
            buy.goods.goods_num -= buy.nums
            buy.goods.save()
            order_good.order = order
            order_good.save()

            buy.delete()

        return order

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        else:
            return OrderInfoSerializer


class AlipayView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        process_dict = {}  # 得到一个字符串参数对应字典
        for key, value in request.POST.items():
            process_dict[key] = value
        sign = process_dict.pop("sign")

        alipay = Alipay(
            appid=ALI_APP_ID,
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_public_key_path,
            app_notify_url="http://39.108.55.149:8000/alipay/return",
            return_url="http://39.108.55.149:8000/alipay/return",
            method="alipay.trade.page.pay",
            debug=True,  # 使用沙箱环境
        )

        result = alipay.verify(process_dict, sign)
        print(result)
