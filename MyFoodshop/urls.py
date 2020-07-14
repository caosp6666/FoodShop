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
from django.views.generic import TemplateView
import xadmin
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

# from goods.view_django import GoodsListView
from goods.views import GoodsListView, GoodsListViewSet, CategoryViewSet, BannerViewSet, HotSearchWordsViewSet, \
    IndexGoodsCategoryViewSet
from users.views import SmsCodeViewSet, UserViewSet
from user_operations.views import UserFavViewSet, MessageViewSet, AddressViewSet
from apps.trades.views import ShoppingCartViewSet, OrderViewSet
from .settings import MEDIA_ROOT

router = DefaultRouter()
router.register(r'goods', GoodsListViewSet, basename="goods")
router.register(r'categorys', CategoryViewSet, basename='categorys')
router.register(r'code', SmsCodeViewSet, basename='code')
router.register(r'user', UserViewSet, basename='user')
# 收藏
router.register(r'userfavs', UserFavViewSet, basename='userfavs')
# 留言
router.register(r'messages', MessageViewSet, basename='messages')
# 收货地址
router.register(r'address', AddressViewSet, basename='address')
# 购物车
router.register(r'shoppingcarts', ShoppingCartViewSet, basename='shoppingcarts')
# 订单
router.register(r'orders', OrderViewSet, basename='orders')

# 首页轮播图
router.register(r'banner', BannerViewSet, basename='banner')
# 热搜词
router.register(r'hotsearchs', HotSearchWordsViewSet, basename='hotsearchs')
# 首页分类展示列表
router.register(r'indexgoods', IndexGoodsCategoryViewSet, basename='indexgoods')

urlpatterns = [
    path('xadmin/', xadmin.site.urls),  # xadmin后台
    path('', include(router.urls)),  # router url的配置

    # path('goods/', GoodsListView.as_view(), name="goods-list"),
    # path('goods/', goods_list, name="goods-list"),

    path('login/', obtain_jwt_token),  # 登陆
    re_path(r'^api-auth/', include('rest_framework.urls')),  # DRF登陆的配置
    path('docs/', include_docs_urls(title="MyFoodShop")),  # 文档
    re_path(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),  # media文件获取

    # path('api-token-auth/', views.obtain_auth_token),                         # drf自带的token验证模式，测试用
    # path('jwt_auth/', obtain_jwt_token),                                      # JWT验证模式，测试用

    re_path('', include('social_django.urls', namespace='social')),  # 第三方登录
    re_path(r'^index/', TemplateView.as_view(template_name="index.html"), name="index"),
]


# sentry test
def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns += [
    path('sentry-debug/', trigger_error),
]
