# encoding: utf-8
from django.db import models

from shouzhuan.const import Const, verify_constraint, withdraw_constraint
from shouzhuan.utils import msec_time, get_date_by_stamp
from users.models import User, Bankcard


class Administrator(models.Model):
    adminname = models.CharField(max_length=45,unique=True)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=10)
    phone = models.CharField(max_length=11)
    
    normal_permission=models.BooleanField(default=True)#任务、商店审核
    notice_permission=models.BooleanField(default=True)#公告发布
    finance_permission=models.BooleanField(default=False)#充值、提现
    statistic_permission=models.BooleanField(default=True)#统计
    
    def __unicode__(self):
        return '<Administrator : %d >' %(self.id)
    
class Recharge(models.Model):
    amount=models.DecimalField(max_digits=11, decimal_places=2,default=0)
    bank_name=models.CharField(max_length=45)
    account_name=models.CharField(max_length=255)
    verify_status=models.SmallIntegerField(default=Const['model.verify.need_check'],choices=verify_constraint)
    verify_time=models.BigIntegerField(null=True,blank=True)
    create_time=models.BigIntegerField(default=msec_time)
    

    user=models.ForeignKey(User,null=True)
    verify_admin=models.ForeignKey(Administrator,null=True,blank=True)
    class Meta:
        ordering = ['-create_time']
        
    def __unicode__(self):
        return '<Recharge : %d ,User : %s >' %(self.id,self.user.username)
        
class Withdraw(models.Model):
    amount=models.DecimalField(max_digits=11, decimal_places=2,default=0)
    reward = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    verify_status=models.SmallIntegerField(default=Const['model.verify.need_check'],choices=verify_constraint)
    verify_time=models.BigIntegerField(null=True,blank=True)
    create_time=models.BigIntegerField(default=msec_time)
    type=models.SmallIntegerField(choices=withdraw_constraint)
    admin_submit=models.DecimalField(max_digits=11, decimal_places=2,default=0)
    
    bankcard=models.ForeignKey(Bankcard,null=True)
    verify_admin=models.ForeignKey(Administrator,null=True,blank=True)
    class Meta:
        ordering = ['-create_time']

    def __unicode__(self):
        return '<Withdraw : %d ,Bankcard : %d >' %(self.id,self.bankcard_id)
    
class Notice(models.Model):
    type=models.SmallIntegerField()
    title=models.CharField(max_length=60)
    content=models.TextField(null=True,blank=True)
    create_time=models.BigIntegerField(default=msec_time)
    update_time=models.BigIntegerField(default=msec_time)
    important=models.BooleanField(default=False)
    url=models.URLField(null=True,blank=True)
    pic_path=models.URLField(null=True,blank=True)
    publish_admin=models.ForeignKey(Administrator)
    
    class Meta:
        ordering = ['-update_time']
    
    def create_date(self):
        return get_date_by_stamp(self.create_time)
    
    def is_new(self):
        nowms=msec_time()
        if (nowms-self.create_time) < Const['notice.new.timedelta']:
            return True
        else:
            return False
