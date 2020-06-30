from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    """
    user info
    继承自Django的AbstractUser
    """
    GENDER_TYPE = (
        ("male", "男"),
        ("female", "女")
    )

    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=GENDER_TYPE, verbose_name="性别", default="female")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="电话")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username  # username和name是不同的


class VerifyCode(models.Model):
    """
    把短信验证码存到数据库中用于验证
    """
    code = models.CharField(max_length=6, verbose_name="验证码")
    mobile = models.CharField(max_length=11, verbose_name='电话')

    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code
