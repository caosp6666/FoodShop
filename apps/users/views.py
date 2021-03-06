from django.shortcuts import render

# Create your views here.
import redis
from random import choice
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from utils.YunPian import YunPian
from apps.users.serializers import SmsSerializer, RegisterSerializer, UserDetailSerializer
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


class UserViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        """
        根据action动态选择serializer
        :return:
        """
        if self.action == "create":
            return RegisterSerializer
        else:
            return UserDetailSerializer

    def get_permissions(self):
        """
        根据action动态选择permission，create不需要登陆，其他需要
        :return:
        """
        if self.action == "create":
            return []
        else:
            return [permissions.IsAuthenticated()]

    def get_object(self):
        return self.request.user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        now_user = self.perform_create(serializer)

        now_payload = jwt_payload_handler(now_user)
        now_token = jwt_encode_handler(now_payload)

        now_dict = serializer.data
        now_dict["token"] = now_token
        now_dict["name"] = now_user.name if now_user.name else now_user.username

        headers = self.get_success_headers(serializer.data)
        return Response(now_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """

        :param serializer:
        :return: 这里重写是为了返回一个user对象
        """
        return serializer.save()
