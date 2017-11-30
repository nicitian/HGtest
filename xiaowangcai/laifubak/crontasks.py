# encoding: utf-8
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
import time

from django.contrib.sessions.models import Session
from django.db import transaction
from django.db.models import Sum

from laifu.const import Const
from laifu.utils import msec_time
from management.models import Recharge, Withdraw
from others.models import DailyReport
from tasks.models import StoreRecentBuyer, Order
from tasks.views import _order_returndeliver, _rebate_judge, _order_affirm,order_auto_returndeliver
from users.models import User, TBAccount, Record


logger = logging.getLogger(__name__)

def daily_maintenance():
    field_clean()
    session_clean()
    daily_report()
    daily_clean_buy_record()


def daily_clean_buy_record():
    tbaccounts = TBAccount.objects.all()
    for tb in tbaccounts:
        user_id = tb.user_id
        wangwang = tb.id
        logger.info('user_id:%d  wangwang:%d  clean today_receive_orders %d  cleaned'%(user_id,wangwang,tb.today_receive_orders))
        tb.today_receive_orders = 0
        tb.save()



def daily_report():
    logger.info('daily report start')
    today=date.today()
    yesterday=today-timedelta(days=1)
    start_stamp=time.mktime(yesterday.timetuple())*1000
    end_stamp=time.mktime(today.timetuple())*1000
    new_orders=Order.objects.filter(task__create_time__gte=start_stamp,
                                task__create_time__lt=end_stamp)
    #放单数
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.new_order_num'],value=new_orders.count())
    #放单金额
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.new_order_payment'],amount=new_orders.aggregate(Sum('seller_payment'))['seller_payment__sum'] if new_orders else 0)
    ##
    finish_orders=Order.objects.filter(status=Const['model.order.status.completed'],update_time__gte=start_stamp,update_time__lt=end_stamp)
    (finish_orders_num,finish_orders_payment,finish_orders_gain,finish_orders_principal)=reduce(lambda a,b:(a[0]+b[0],a[1]+b[1],a[2]+b[2],a[3]+b[3]), ( (1,o.seller_payment,o.buyer_gain,o.buyer_principal if o.task.return_type==Const['model.task.return_type.platform'] else 0) for o in finish_orders)) if finish_orders else (0,0,0,0) 
    #完成单数
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.finish_order_num'],value=finish_orders_num)
    #完成单金额
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.finish_order_payment'],amount=finish_orders_payment)
    #签到佣金金额
    signup_amount=Record.objects.filter(category=Const['model.record.category.signup'],create_time__gte=start_stamp,create_time__lt=end_stamp).aggregate(Sum('amount'))['amount__sum']
    signup_amount=signup_amount if signup_amount else 0
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.signup'],amount=signup_amount )
    #推广佣金金额
    promote_amount=Record.objects.filter(category=Const['model.record.category.promote'],create_time__gte=start_stamp,create_time__lt=end_stamp).aggregate(Sum('amount'))['amount__sum']
    promote_amount=promote_amount if promote_amount else 0
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.promote'],amount=promote_amount )
    #毛利润
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.profit'],amount=(finish_orders_payment-finish_orders_gain-finish_orders_principal-signup_amount-promote_amount))
    #充值金额
    recharge_amount=Recharge.objects.filter(verify_time__gte=start_stamp,verify_time__lt=end_stamp,verify_status=Const['model.verify.check_pass']).aggregate(Sum('amount'))['amount__sum'] 
    recharge_amount=recharge_amount if recharge_amount else 0
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.recharge'],amount=recharge_amount)
    #本金提现
    principal_withdraw_amount=Withdraw.objects.filter(type=Const['model.withdraw.type.principal'],verify_time__gte=start_stamp,verify_time__lt=end_stamp,verify_status=Const['model.verify.check_pass']).aggregate(Sum('amount'))['amount__sum']
    principal_withdraw_amount=principal_withdraw_amount if principal_withdraw_amount else 0
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.principal_withdraw'],amount=principal_withdraw_amount)
    #佣金提现
    commission_withdraw_amount=Withdraw.objects.filter(type=Const['model.withdraw.type.commission'],verify_time__gte=start_stamp,verify_time__lt=end_stamp,verify_status=Const['model.verify.check_pass']).aggregate(Sum('amount'))['amount__sum']
    commission_withdraw_amount=commission_withdraw_amount if commission_withdraw_amount else 0
    DailyReport.objects.create(date=yesterday,type=Const['model.dailyreport.type.commission_withdraw'],amount=commission_withdraw_amount)
    logger.info('daily report finish')
    
def field_clean():
    logger.info('Everyday-field clean start')
    logger.info('Everyday-field clean user')
    #User.objects.all().update(today_commission=0)
    #logger.info('Everyday-field clean tbaccount')
    #TBAccount.objects.all().update(today_receive_orders=0)
    today=time.mktime(date.today().timetuple())*1000
    before15d=today-Const['ms.per.day']*14
    logger.info('Everyday-field clean storerecent 15d')
    StoreRecentBuyer.objects.filter(create_time__lte=before15d,type=Const['model.ordergtype.comment']).delete()
    # logger.info('Everyday-field clean storerecent 1d')
    # StoreRecentBuyer.objects.filter(create_time__lte=today,type=Const['model.ordergtype.flow']).delete()
    logger.info('Everyday-field clean success')
    
def session_clean():
    Session.objects.filter(expire_date__lt=datetime.now()).delete()
    logger.info('unexpired session delete!')

def order_manage():
    logger.info('order_manage start')
    nowtime=msec_time()
    #自动返款
    orders=Order.objects.filter(status=Const['model.order.status.step3'],
                         receive_time__lte=nowtime- 12*Const['ms.per.hour'],#这里应该是12小时的，测试环境下的
                         task__return_type=Const['model.task.return_type.platform']).exclude(frozen=True)
    #logger.debug(orders.query)
    counter=0
    for o in orders:
        if _order_returndeliver(o):
            with transaction.atomic():
                counter=counter+1
                o.save()
                # 避免刷手提交资金和商家的商品资金不同的情况
                order_auto_returndeliver(o)
                # 原来的情况
                # o.tb.user.money_operate(Const['model.record.pricipal'],
                #     o.buyer_principal,'订单本金归还，订单编号：%d'%o.id,
                #     Const['model.record.category.principalreturn'])
    logger.info('自动还款数：%d'%counter)
    # 自动取消订单
    counter=0
    orders=Order.objects.filter(status=Const['model.order.status.received'],task__prepublish=False,
            receive_time__lte=nowtime-2*Const['ms.per.hour'],).exclude(frozen=True)
    for o in orders:
        order=Order.objects.get(pk=o.id)
        if order.status==Const['model.order.status.received']:
            with transaction.atomic():
                counter=counter+1
                order.tb.user.money_operate(Const['model.record.commission'],Decimal(-1) if order.is_buy_order() else Decimal(-0.3),
                               '取消订单惩罚，订单：%d'%order.id)
                if order.is_buy_order():
                    StoreRecentBuyer.objects.filter(tb_id=order.tb_id,store_id=order.task.store_id,type=Const['model.ordergtype.comment']).delete()
                    order.tb.today_receive_orders=order.tb.today_receive_orders-1
                    order.tb.save()
                else:
                    StoreRecentBuyer.objects.filter(tb_id=order.tb_id,
                                                    store_id=order.task.store_id,
                                                    type=order.order_type).delete()
                order.status=Const['model.order.status.init']
                order.tb=None
                order.receive_time=None
                order.step_detail='{}'
                order.save()
    logger.info('自动取消订单数：%d'%counter)
    #自动确认订单
    counter=0
    orders=Order.objects.filter(status=Const['model.order.status.comment'],update_time__lte=nowtime-2*Const['ms.per.hour']).exclude(frozen=True)
    for o in orders:
        if _order_affirm(o.id):
            counter=counter+1
    logger.info('自动确认订单数：%d'%counter)
    logger.info('order_manage end')
