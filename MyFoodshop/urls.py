"""MyFoodshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path, include
from django.views.static import serve
import xadmin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token


# from goods.view_django import GoodsListView
from goods.views import GoodsListView, GoodsListViewSet, CategoryViewSet
from users.views import SmsCodeViewset
from .settings import MEDIA_ROOT

router = DefaultRouter()
router.register(r'goods', GoodsListViewSet, basename="goods")
router.register(r'categorys', CategoryViewSet, basename='categorys')
router.register(r'code', SmsCodeViewset, basename='code')

urlpatterns = [
    path('xadmin/', xadmin.site.urls),  # xadmin后台
    path('', include(router.urls)),  # router url的配置

    # path('goods/', GoodsListView.as_view(), name="goods-list"),
    # path('goods/', goods_list, name="goods-list"),

    path('login/', obtain_jwt_token),  # 登陆
    re_path(r'^api-auth/', include('rest_framework.urls')),  # DRF登陆的配置
    re_path(r'docs/', include_docs_urls(title="MyFoodShop")),  # 文档
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # media文件获取

    # path('api-token-auth/', views.obtain_auth_token),  # drf自带的token验证模式，测试用
    # path('jwt_auth/', obtain_jwt_token),  # JWT验证模式，测试用
]
