# encoding: utf-8
import datetime
import logging
import time

from django.db import models, transaction

from shouzhuan.const import *
from shouzhuan.utils import msec_time, del_dict_keys, \
    fix_length_random_int, get_datetime_by_stamp, bitflag_has, bitflag_set, bitflag_dump
from lib.im.rong import ApiClient

logger = logging.getLogger(__name__)


# Managers
class UserManager(models.Manager):
    def get_user_dict_from_session(self, request):
        return del_dict_keys(super(UserManager, self).get(pk=request.session['user_id']).to_dict(), 'password')

    def get_user_from_session(self, request):
        return super(UserManager, self).get(pk=request.session['user_id'])


class BlacklistManager(models.Manager):
    pass


class SmscaptchaManager(models.Manager):
    pass


# Models
class User(models.Model):
    id = models.IntegerField(primary_key=True, db_index=True)
    username = models.CharField(max_length=45, unique=True, db_index=True)
    password = models.CharField(max_length=32)
    phone = models.CharField(max_length=11, unique=True, db_index=True)
    buyer_level = models.SmallIntegerField(default=1, db_index=True)
    seller_level = models.SmallIntegerField(default=1, db_index=True)
    buyer_orders = models.IntegerField(default=0, db_index=True)
    seller_orders = models.IntegerField(default=0, db_index=True)
    idc_name = models.CharField(max_length=20, default='', blank=True)
    idc_photo = models.CharField(max_length=600, blank=True)
    qq = models.CharField(max_length=20, blank=True)
    photo = models.CharField(max_length=255, blank=True)
    principal = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    register_time = models.BigIntegerField(default=msec_time)
    imei = models.CharField(max_length=20, null=True, blank=True)

    # 融云token
    # ry_token=models.CharField(max_length=256,null=True,blank=True)

    # 今日任务收入
    today_commission = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    # 推广佣金，推广人数，邀请人奖励
    promote_award = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    promote_num = models.IntegerField(default=0)
    buyer_invitee_award = models.BooleanField(default=True)
    # 注册奖励，有邀请人将在完成第一单任务后奖励，无邀请人注册后即可奖励
    join_award = models.BooleanField(default=False)
    # 上次签到奖励时间
    last_award_time = models.BigIntegerField(null=True, blank=True)

    inviter = models.ForeignKey('self', related_name='invitee', null=True, blank=True)
    blacklist_buyer = models.ManyToManyField('self', related_name='in_blacklist', through='Blacklist',
                                             through_fields=('seller', 'buyer'), symmetrical=False)

    # 身份证审核状态
    verify_status = models.SmallIntegerField(default=Const['model.verify.need_check'], choices=verify_constraint)
    verify_time = models.BigIntegerField(null=True, blank=True)
    verify_admin = models.ForeignKey('management.Administrator', null=True, blank=True)

    flags = models.BigIntegerField(default=0, name='flags', db_index=True)
    notice = models.IntegerField(default=0)  # 各项通知的标志位
    is_close_sellerreturn = models.IntegerField(default=0)  # 是否关闭商家返款通道
    is_new = models.IntegerField(default=1)     # 是否新人 默认是
    order_money_limit = models.IntegerField(null=True)  # 限制接单金额
    liulan_order_num = models.IntegerField(default=0)   # 已完成浏览单数量
    haoping_order_num = models.IntegerField(default=0)  # 已完成好评单数量
    objects = UserManager()

    def to_data(self):
        data = del_dict_keys(self.to_dict(), 'password')
        data['today_promote'] = self.get_today_promote()
        return data

    def lahei(self, black_user_id, reason):
        buyer = User.objects.get(pk=black_user_id)
        if Blacklist.objects.filter(seller=self, buyer=buyer).count() > 0:
            return False
        else:
            Blacklist.objects.create(seller=self, buyer=buyer, reason=reason)
            return True

    # flags的第一位标志位为1表示已经冻结，否则为未冻结
    def is_freezed(self):
        return self.flag_has(1)

    def freeze(self, tofreeze_id):
        buyer = User.objects.get(pk=tofreeze_id)
        buyer.flag_set(1, True)
        buyer.save(update_fields=['flags'])

    def normalize_flags(self, user_id):
        buyer = User.objects.get(pk=user_id)
        buyer.flag_set(1, False)
        buyer.save(update_fields=['flags'])

    def has_blacklist_with(self, buyer_id):
        if len(self.blacklist_buyer.filter(pk=buyer_id)) > 0:
            return True
        else:
            return False

    def money_operatesafe(self, amount_type, amount, desc, category=0):
        amount = Decimal(amount)
        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=self.id)
            if amount_type == Const['model.record.pricipal']:
                locked_user.principal = locked_user.principal + amount
                if amount < 0 and locked_user.principal < 0:
                    return locked_user.principal

                Record.objects.create(id=Record.objects.avaliable_id(),
                                      user=locked_user,
                                      amount=amount,
                                      balance=locked_user.principal,
                                      type=Const['model.record.pricipal'],
                                      description=desc,
                                      category=category)
                locked_user.save(update_fields=['principal'])
                self.principal = locked_user.principal
                self.notice_set(Const['model.remind.principal'], True)
                return self.principal
            else:
                locked_user.commission = locked_user.commission + amount
                if amount < 0 and locked_user.commission < 0:
                    return locked_user.commission
                Record.objects.create(id=Record.objects.avaliable_id(),
                                      user=locked_user,
                                      amount=amount,
                                      balance=locked_user.commission,
                                      type=Const['model.record.commission'],
                                      description=desc,
                                      category=category)
                locked_user.save(update_fields=['commission'])
                self.commission = locked_user.commission
                self.notice_set(Const['model.remind.commission'], True)
                return self.commission

    def money_operate(self, account_type, amount, desc, category=0):
        amount = Decimal(amount)
        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=self.id)
            if account_type == Const['model.record.pricipal']:
                locked_user.principal = locked_user.principal + amount
                Record.objects.create(id=Record.objects.avaliable_id(),
                                      user=locked_user, amount=amount, balance=locked_user.principal,
                                      type=Const['model.record.pricipal'], description=desc,
                                      category=category)
                locked_user.save(update_fields=['principal'])
                self.principal = locked_user.principal
                self.notice_set(Const['model.remind.principal'], True)
            else:
                locked_user.commission = locked_user.commission + amount
                Record.objects.create(id=Record.objects.avaliable_id(),
                                      user=locked_user, amount=amount, balance=locked_user.commission,
                                      type=Const['model.record.commission'], description=desc,
                                      category=category)
                locked_user.save(update_fields=['commission'])
                self.commission = locked_user.commission
                self.notice_set(Const['model.remind.commission'], True)

    def ry_get_token(self):
        client = ApiClient()
        result = client.user_get_token(str(self.id), str(self.id),
                                       self.photo)
        if result[u'code'] == 200:
            # self.ry_token=result[u'token']
            # self.save()
            pass
        else:
            raise Exception('rongyun get user token error:%s'
                            % str(result))
        return result[u'token']

    def ry_info_refresh(self):
        client = ApiClient()
        result = client.user_refresh(str(self.id), str(self.id),
                                     self.photo)
        if result[u'code'] != 200:
            raise Exception('rongyun info refresh error:%s'
                            % str(result))

    def set_user_level(self, level_type):
        if level_type == 's':
            for i in range(len(Const['seller.level.limit'])):
                if self.seller_orders < Const['seller.level.limit'][i]:
                    if self.seller_level < (i + 1):
                        self.seller_level = (i + 1)
                    return
            self.seller_level = (len(Const['seller.level.limit']) + 1)
        elif level_type == 'b':
            for i in range(len(Const['buyer.level.limit'])):
                if self.buyer_orders < Const['buyer.level.limit'][i]:
                    if self.buyer_level < (i + 1):
                        self.buyer_level = (i + 1)
                    return
            self.buyer_level = (len(Const['buyer.level.limit']) + 1)
        else:
            raise Exception('xx')

    def get_today_promote(self):
        today = datetime.date.today()
        arg = int(time.mktime(datetime.datetime(today.year, today.month, today.day).timetuple()) * 1000)
        promote_records = self.record_set.filter(category=Const['model.record.category.promote'],
                                                 create_time__gt=arg)
        res = 0
        for r in promote_records:
            res = res + r.amount
        return float(res)

    def flag_has(self, index):
        return bitflag_has(self.flags, index)

    def notice_has(self, index):
        return bitflag_has(self.notice, index)

    def flag_set(self, index, value):
        self.flags = bitflag_set(self.flags, index, value)

    def notice_set(self, index, value):
        self.notice = bitflag_set(self.notice, index, value)
        self.save(update_fields=['notice'])

    def flag_dump(self):
        return bitflag_dump(self.flags)

    def __unicode__(self):
        return self.username

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if update_fields is None and not force_insert:
            update_fields = []
            for field in self._meta.fields:
                if not field.primary_key and (field.name != "principal" and field.name != "commission"):
                    update_fields.append(field.name)
                    if field.name != field.attname:
                        update_fields.append(field.attname)

        # logger.debug(update_fields)
        super(User, self).save(force_insert=force_insert, force_update=force_update,
                               using=using, update_fields=update_fields)

    class Meta:
        ordering = ['-register_time']


class Blacklist(models.Model):
    seller = models.ForeignKey(User, related_name='seller_blacklist')
    buyer = models.ForeignKey(User, related_name='buyer_blacklist')
    create_time = models.BigIntegerField(default=msec_time)
    reason = models.CharField(max_length=255)

    objects = BlacklistManager()

    def __unicode__(self):
        return str(self.seller_id) + ':' + str(self.buyer_id)


class Smscaptcha(models.Model):
    phone = models.CharField(max_length=11, primary_key=True)
    captcha = models.CharField(max_length=6)
    create_time = models.BigIntegerField()

    objects = SmscaptchaManager()

    def __unicode__(self):
        return self.phone + ':' + self.captcha


class Bankcard(models.Model):
    user = models.ForeignKey(User)
    bank_name = models.CharField(max_length=45)
    bank_city = models.CharField(max_length=45)
    bank_province = models.CharField(max_length=45, default=None)
    bank_district = models.CharField(max_length=45, default=None)
    owner_name = models.CharField(max_length=20)
    account_id = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=45, null=True)
    create_time = models.BigIntegerField(default=msec_time)

    verify_status = models.SmallIntegerField(default=Const['model.verify.need_check'], choices=verify_constraint)
    verify_time = models.BigIntegerField(null=True, blank=True)
    verify_admin = models.ForeignKey('management.Administrator', null=True, blank=True)

    def __unicode__(self):
        return u'<Bankcard: %d ,User: %s >' % (self.id, self.user.username)

    class Meta:
        ordering = ['-create_time']


class RecordManager(models.Manager):
    def avaliable_id(self):
        while True:
            oid = fix_length_random_int(9)
            if super(RecordManager, self).filter(pk=oid).count() == 0:
                return oid


class Record(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User)
    create_time = models.BigIntegerField(default=msec_time, db_index=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2, default=0, db_index=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2, default=0, db_index=True)
    type = models.SmallIntegerField(db_index=True)
    description = models.CharField(max_length=255)
    category = models.SmallIntegerField(default=0, db_index=True)

    objects = RecordManager()

    class Meta:
        ordering = ['-create_time']

    def is_income(self):
        if self.amount >= 0:
            return True
        else:
            return False

    def create_time_str(self):
        return get_datetime_by_stamp(self.create_time)

    def __unicode__(self):
        return 'id:%d ,user:%s ' % (self.id, self.user.username)


class TBAccount(models.Model):
    wangwang = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=11, db_index=True)
    city = models.CharField(max_length=20)
    place = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    pic_paths = models.CharField(max_length=600)
    status = models.SmallIntegerField(default=Const['model.verify.need_check'], choices=verify_constraint,
                                      db_index=True)
    verify_time = models.BigIntegerField(null=True, blank=True, db_index=True)
    create_time = models.BigIntegerField(default=msec_time, db_index=True)

    # 今日接单数
    today_receive_orders = models.SmallIntegerField(default=0, blank=True)

    verify_admin = models.ForeignKey('management.Administrator', null=True, blank=True)
    user = models.ForeignKey(User)

    register_time = models.IntegerField(null=True)
    gender = models.SmallIntegerField(null=True)
    age = models.IntegerField(null=True)
    is_credit_card_open = models.SmallIntegerField(default=0)
    wangwang_level = models.SmallIntegerField(null=True, choices=tb_level_constraint)
    is_huabei_open = models.SmallIntegerField(default=0)

    # 冻结
    is_frozen = models.SmallIntegerField(default=0)
    frozen_start_datetime = models.DateTimeField(null=True)
    frozen_days = models.IntegerField(null=True)

    class Meta:
        ordering = ['-create_time']

    def __unicode__(self):
        return u'<TBAccount: %d User: %s >' % (self.id, self.user.username)
