from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from apps.user_operations.serializers import UserFavSerializer
from apps.user_operations.models import UserFav
from utils.permissions import IsOwnerOrReadOnly


class UserFavViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = UserFavSerializer
    lookup_field = "goods_id"  # 指定param对应的字段，默认是pk（id）中找，这里改成根据商品的id找

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)
