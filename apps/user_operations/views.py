from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from apps.user_operations.serializers import UserFavSerializer, UserFavListSerializer, MessageSerializer, \
    AddressSerializer
from apps.user_operations.models import UserFav, UserLeavingMessage, UserAddress
from utils.permissions import IsOwnerOrReadOnly


class UserFavViewSet(viewsets.ModelViewSet):
    """
    list:
        获取用户收藏列表
    retrieve:
        判断某个商品是否已经收藏
    create:
        收藏商品
    """
    queryset = UserFav.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 验证是否登录
    lookup_field = "goods_id"  # 指定param对应的字段，默认是pk（id）中找，这里改成根据商品的id找

    def get_serializer_class(self):
        if self.action == "list":
            return UserFavListSerializer
        else:
            return UserFavSerializer

    # def perform_create(self, serializer):
    #     instance = serializer.save()  # 得到serializer
    #     goods = instance.goods
    #     goods.fav_num += 1  # 对收藏数加1
    #     goods.save()
    #
    # def perform_destroy(self, instance):
    #     goods = instance.goods
    #     goods.fav_num -= 1
    #     goods.save()
    #     instance.delete()

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)


class MessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取留言
    create:
        添加留言
    delete:
        删除留言
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = MessageSerializer

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收获地址
    create:
        添加收获地址
    update:
        更新收获地址
    delete:
        删除收货地址
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AddressSerializer

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
