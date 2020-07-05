from django.shortcuts import render

# Create your views here.
import redis
from random import choice
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from utils.YunPian import YunPian
from .serializers import SmsSerializer, RegisterSerializer
from MyFoodshop.secret_key import yunpian_api_key, REDIS_PORT, REDIS_HOST
from apps.users.models import VerifyCode

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """
    send sms code
    """

    # 先验证
    serializer_class = SmsSerializer

    def generate_code(self):
        seeds = "1234567890"
        random_string = []
        for i in range(4):
            random_string.append(choice(seeds))
        return ''.join(random_string)

    # 重写create方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # 这里设置为True以后，如果有异常，后面不会执行，且返回http400给前端

        mobile = serializer.validated_data["mobile"]
        yun_pian = YunPian(yunpian_api_key, mobile)
        code = self.generate_code()

        sms_status = yun_pian.send(code)  # 返回一个dict

        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"],
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # # 将code保存到redis
            # red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, charset='utf8', decode_responses=True)
            # red.set(str(mobile), str(code))
            # red.expire(str(mobile), 5 * 60)  # 五分钟过期

            # 将code保存到mysql
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()

            return Response({
                "mobile": mobile,
            }, status=status.HTTP_201_CREATED)


class UserViewSet(CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
