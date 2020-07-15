from rest_framework import serializers
from apps.goods.models import Goods
from apps.trades.models import ShoppingCart, OrderInfo, OrderGoods
from apps.goods.serializers import GoodsSerializer
from utils.alipay import Alipay
from MyFoodshop.secret_key import ALI_APP_ID
from MyFoodshop.settings import ali_public_key_path, private_key_path


class ShoppingCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(
        label="数量",
        required=True,
        min_value=1,
        error_messages={
            "min_value": "商品数量不能小于1",
            "required": "请选择购买数量"
        }
    )
    goods = serializers.PrimaryKeyRelatedField(
        label="商品",
        queryset=Goods.objects.all(),
        required=True,
    )

    def create(self, validated_data):
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]  # 这里的goods是对象

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


class ShoppingCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class OrderInfoSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    # 以下的信息不能由用户提交，必须是后端修改的
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = Alipay(
            appid=ALI_APP_ID,
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_public_key_path,
            app_notify_url="http://39.108.55.149:8000/alipay/return",
            return_url="http://39.108.55.149:8000/alipay/return",
            method="alipay.trade.page.pay",
            debug=True,  # 使用沙箱环境
        )
        url = alipay.pay(
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            subject=obj.order_sn
        )
        return url

    def generate_order_sn(self):
        # 当前时间（秒）+userid+随机数
        import time
        from random import randint
        order_sn = "{time_str}{user_id}{random_num}".format(
            time_str=time.strftime("%Y%m%d%H%M%S"),
            user_id=self.context["request"].user.id,
            random_num=randint(10, 99)
        )
        return order_sn

    def validate(self, attrs):
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = Alipay(
            appid=ALI_APP_ID,
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_public_key_path,
            app_notify_url="http://39.108.55.149:8000/alipay/return",
            return_url="http://39.108.55.149:8000/alipay/return",
            method="alipay.trade.page.pay",
            debug=True,  # 使用沙箱环境
        )
        url = alipay.pay(
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,
            subject=obj.order_sn
        )
        return url

    class Meta:
        model = OrderInfo
        fields = ("goods", "signer_name", "singer_mobile", "order_sn", "pay_status", "address", "alipay_url")
