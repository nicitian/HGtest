# coding=utf-8
from django.db import models


class DailyReport(models.Model):
    type = models.SmallIntegerField()
    date = models.DateField()
    value = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-date']


class TkGoods(models.Model):
    dtk_id = models.IntegerField(null=True)  # 大淘客ID
    goods_id = models.CharField(max_length=255, null=True)  # 大淘客商品ID
    c_id = models.IntegerField(null=True)  # 分类ID 1：服装 2：母婴 3：化妆品 4：居家 5：鞋包配饰 6：美食 7：文体车品 8：家电
    title = models.CharField(max_length=255, null=True)  # 标题
    d_title = models.CharField(max_length=255, null=True)  # 短标题
    pic = models.CharField(max_length=255, null=True)  # 商品图片
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    is_tmall = models.SmallIntegerField(default=0)  # 是否天猫
    dsr = models.CharField(max_length=10, null=True)  # 商品描述分
    sales_num = models.IntegerField(default=0)  # 销量
    seller_id = models.CharField(null=True, max_length=255)  # 卖家ID
    quan_price = models.DecimalField(max_digits=11, decimal_places=2, default=0)  # 优惠券金额
    quan_time = models.DateTimeField(null=True)  # 优惠券结束时间
    quan_surplus = models.IntegerField(default=0)  # 优惠券剩余数量
    quan_receive = models.IntegerField(default=0)  # 已领券数量
    quan_condition = models.CharField(max_length=255, null=True)  # 优惠券使用条件
    quan_link = models.TextField()  #
    quan_d_link = models.CharField(max_length=255, null=True)  # 短链*
    link = models.CharField(max_length=255)  # 淘宝客链接
    quan_goods_link = models.TextField(null=False)  # 领券并下单链接
    status = models.SmallIntegerField(default=1)  # 1 正常 0 冻结
    fr = models.SmallIntegerField(default=1)  # 来源  1 手动添加 2 大淘客
    tkl = models.CharField(max_length=255,default=' ')
    create_time = models.DateTimeField(auto_now_add=True, null=True)


class TkGoodsTmp(models.Model):
    dtk_id = models.IntegerField(null=True)     # 大淘客ID
    goods_id = models.CharField(max_length=255, null=True)      # 大淘客商品ID
    c_id = models.IntegerField()    # 分类ID 1：服装 2：母婴 3：化妆品 4：居家 5：鞋包配饰 6：美食 7：文体车品 8：家电
    title = models.CharField(max_length=255, null=True)  # 标题
    d_title = models.CharField(max_length=255, null=True)   # 短标题
    pic = models.CharField(max_length=255, null=True)  # 商品图片
    price = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    is_tmall = models.SmallIntegerField(default=0)      # 是否天猫
    dsr = models.CharField(max_length=10, null=True)  # 商品描述分
    sales_num = models.IntegerField(default=0)  # 销量
    seller_id = models.CharField(null=True,max_length=255)  # 卖家ID
    quan_price = models.DecimalField(max_digits=11, decimal_places=2, default=0)    # 优惠券金额
    quan_time = models.DateTimeField(null=True)  # 优惠券结束时间
    quan_surplus = models.IntegerField(default=0)  # 优惠券剩余数量
    quan_receive = models.IntegerField(default=0)   # 已领券数量
    quan_condition = models.CharField(max_length=255, null=True)    # 优惠券使用条件
    quan_link = models.TextField()    #
    quan_d_link = models.CharField(max_length=255, null=True)   # 短链*
    link = models.CharField(max_length=255)     # 淘宝客链接
    quan_goods_link = models.TextField(null=True)  # 领券并下单链接
    # quan_goods_link = models.TextField(null=False)  # 领券并下单链接
    status = models.SmallIntegerField(default=1)    # 1 正常 0 冻结
    fr = models.SmallIntegerField(default=1)    # 来源  1 手动添加 2 大淘客
    tkl = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, null=True)

# 淘客广告
class TkAd(models.Model):
    cid = models.IntegerField()  # 分类 0:全部 1：服装 2：母婴 3：化妆品 4：居家 5：鞋包配饰 6：美食 7：文体车品 8：家电
    pic = models.CharField(max_length=255, null=True)  # 商品图片
    link = models.CharField(max_length=255, null=True)  # 链接
