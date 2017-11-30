# encoding: utf-8
from decimal import Decimal, getcontext
import logging

from django.db import transaction
from django.shortcuts import render

from shouzhuan.const import Const
from shouzhuan.filters import userid_check, admin_permission, mutex_lock
from shouzhuan.utils import make_conditions, JsonResponse, obj_to_dict, CsvResponse, \
    get_paginator, obj_verify, obj_verify_strict, get_stamp_by_date, obj_modify, msec_time,get_datetime_by_stamp
from management.forms import RechargeForm, NoticeForm
from management.models import Recharge, Notice, Administrator, Withdraw
from users.models import Record
from tasks.models import Store, Task, Order
from users.models import TBAccount, Bankcard, User

logger = logging.getLogger(__name__)


@userid_check
def recharge_create(r):
    form = RechargeForm(r.POST)
    if form.is_valid():
        data = form.cleaned_data
        data['user_id'] = r.REQUEST['user_id']
        Recharge.objects.create(**data)
        return JsonResponse(code=Const['code.success'])
    return JsonResponse(code=Const['code.request_error'])


def notice_listbuyernotice(r):
    notices = Notice.objects.filter(type=Const['model.notice.type.buyer'])
    return JsonResponse(code=Const['code.success'],
                        data=[n.to_exc_dict('publish_admin', 'content', 'type') for n in notices])


def administrator_login(r):
    params = r.REQUEST
    admin = Administrator.objects.filter(adminname=params['adminname'],
                                         password=params['password'])
    if not admin:
        return JsonResponse(code=Const['code.login_error'])
    else:
        r.session['admin_id'] = admin[0].id
        return JsonResponse(code=Const['code.success'])


def administrator_logout(r):
    r.session.clear()
    result = JsonResponse(code=Const['code.success'])
    result.delete_cookie('sessionid')
    return result


@admin_permission('finance')
def recharge_list(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, user_id='user_id', verify_status='verify_status')
    recharges = Recharge.objects.filter(**condition)[start:start + num]
    total = Recharge.objects.filter(**condition).count()
    data = []
    for rec in recharges:
        d = rec.to_dict()
        d['user_qq'] = rec.user.qq
        d['user_name'] = rec.user.idc_name
        d['user_phone'] = rec.user.phone
        data.append(d)
    return JsonResponse(code=Const['code.success'],
                        data={'total': total, 'recharges': data})


@admin_permission('finance')
@transaction.atomic
@mutex_lock
def cash_back(r, oid):
    record = Record.objects.get(pk=oid)
    record.user.money_operate(Const['model.record.commission'], Decimal(-record.amount),
                              '返还取消订单惩罚佣金，扣款记录：%d' % record.id)
    return JsonResponse(code=Const['code.success'])


@admin_permission('finance')
@transaction.atomic
@mutex_lock
def recharge_verify(r, rid):
    logger.debug('start to recharge_verify')
    recharge = Recharge.objects.get(pk=rid)
    logger.debug('start to recharge_verify status=%s' % r.REQUEST['verify_status'])
    if obj_verify_strict(r, recharge):
        if int(r.REQUEST['verify_status']) == Const['model.verify.check_pass']:
            # logger.debug('start to recharge_verify pass %f,%f'%(recharge.amount,recharge.user.principal))
            recharge.user.money_operate(Const['model.record.pricipal'],
                                        recharge.amount,
                                        '本金账户充值成功',
                                        Const['model.record.category.recharge']
                                        )
            # logger.debug('start to recharge_verify finish %f'%recharge.user.principal)
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@admin_permission('finance')
def withdraw_list(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    condition = make_conditions(r, type='type', bankcard_id='bankcard_id', verify_status='verify_status')
    if 'create_time_start' in params:
        condition['create_time__gte'] = get_stamp_by_date(params['create_time_start'])
    if 'create_time_end' in params:
        condition['create_time__lte'] = get_stamp_by_date(params['create_time_end'])
    if 'user_id' in r.REQUEST:
        condition['bankcard__user_id'] = r.REQUEST['user_id']
    withdraws = Withdraw.objects.filter(**condition)[start:start + num]
    total = Withdraw.objects.filter(**condition).count()
    data = []
    for wit in withdraws:
        d = wit.to_dict()
        if wit.reward == 0:
            d['reward'] = wit.amount
        d['bank_name'] = wit.bankcard.bank_name
        d['bank_city'] = wit.bankcard.bank_city
        d['owner_name'] = wit.bankcard.owner_name
        d['account_id'] = wit.bankcard.account_id
        d['account_name'] = wit.bankcard.account_name
        d['user_id'] = wit.bankcard.user_id
        d['user_qq'] = wit.bankcard.user.qq
        d['user_name'] = wit.bankcard.user.idc_name
        d['user_phone'] = wit.bankcard.user.phone
        d['create_time'] = wit.create_time
        data.append(d)

    return JsonResponse(code=Const['code.success'],
                        data={'total': total, 'withdraws': data})


@admin_permission('finance')
def rebate_export(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    condition = make_conditions(r, type='type', bankcard_id='bankcard_id', verify_status='verify_status')
    if 'create_time_start' in params:
        condition['create_time__gte'] = get_stamp_by_date(params['create_time_start'])
    if 'create_time_end' in params:
        condition['create_time__lte'] = get_stamp_by_date(params['create_time_end'])
    if 'user_id' in r.REQUEST:
        condition['bankcard__user_id'] = r.REQUEST['user_id']
    withdraws = Withdraw.objects.filter(**condition)
    data = []
    for wit in withdraws:
        d = {}
        d['account_id'] = wit.bankcard.account_id
        d['owner_name'] = wit.bankcard.owner_name
        if wit.type == Const['model.withdraw.type.principal']:
            d['amount'] = wit.amount
        else:
            d['amount'] = wit.reward
        d['bank_name'] = wit.bankcard.bank_name
        d['account_name'] = wit.bankcard.account_name
        d['bank_city'] = wit.bankcard.bank_city
        data.append(d)
    metas = {
        'account_id': u'收款卡号',
        'owner_name': u'收款用户',
        'amount': u'返款金额',
        'bank_name': u'收款银行',
        'account_name': u'收款支行',
        'bank_city': u'归属',
    }
    return CsvResponse(metas, data)


@admin_permission('finance')
@transaction.atomic
@mutex_lock
def withdraw_verify(r, wid):
    withdraw = Withdraw.objects.get(pk=wid)
    if obj_verify_strict(r, withdraw, admin_submit=r.REQUEST['admin_submit'] if 'admin_submit' in r.REQUEST else 0):
        if int(r.REQUEST['verify_status']) == Const['model.verify.check_deny']:
            if withdraw.type == Const['model.withdraw.type.principal']:
                withdraw.bankcard.user.money_operate(Const['model.record.pricipal'],
                                                     withdraw.amount,
                                                     '本金提现失败返还',
                                                     Const['model.record.category.principalwithdraw'])
            else:
                withdraw.bankcard.user.money_operate(Const['model.record.commission'],
                                                     withdraw.amount,
                                                     '佣金提现失败返还',
                                                     Const['model.record.category.commissionwithdraw'])
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


def notice_list(r):
    start, num = get_paginator(r)
    conditions = {}
    params = r.REQUEST
    if 'type' in params:
        conditions['type'] = params['type']
    if 'publish_start_date' in params:
        conditions['create_time__gte'] = get_stamp_by_date(params['publish_start_date'])
    if 'publish_end_date' in params:
        conditions['create_time__lte'] = get_stamp_by_date(params['publish_end_date'])
    if 'keyword' in params:
        conditions['title__contains'] = params['keyword']
    total = Notice.objects.filter(**conditions).count()
    notices = Notice.objects.filter(**conditions)[start:start + num]
    return JsonResponse(code=Const['code.success'],
                        data={'total': total, 'notices': [n.to_dict() for n in notices]})


def notice_last(r):
    return JsonResponse(code=Const['code.success'],
                        data=Notice.objects.filter(type=Const['model.notice.type.buyer']).first().to_sub_dict('title',
                                                                                                              'url'))


@admin_permission('normal')
def notice_create(r):
    form = NoticeForm(r.POST)
    if form.is_valid():
        notice = form.save(commit=False)
        notice.publish_admin_id = r.admin_id
        notice.important = bool(int(r.POST['important']))
        notice.save()
        if not notice.url:
            notice.url = 'http://www.shouzhuanvip.com/notice/%d' % notice.id
            notice.save()
        return JsonResponse(code=Const['code.success'])
    return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
def notice_modify(r, nid):
    notice = Notice.objects.get(pk=nid)
    conditions = make_conditions(r, content='content', url='url', pic_path='pic_path', important='important')
    if 'important' in conditions:
        conditions['important'] = bool(int(conditions['important']))
    conditions['update_time'] = msec_time()
    obj_modify(notice, conditions)
    notice.save()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def notice_delete(r, nid):
    Notice.objects.filter(pk=nid).delete()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def user_storeinfo(r, uid):
    store_list = Store.objects.filter(user_id=uid)
    data = []
    for b in store_list:
        d = b.to_dict()
        data.append(d)
    return JsonResponse(code=Const['code.success'], data=data)


@admin_permission('normal')
def user_listtbaccount(request, user_id):
    user_id = int(user_id)
    tbaccounts = TBAccount.objects.filter(user_id=user_id)
    tbaccounts = [tba.to_dict() for tba in tbaccounts]
    return JsonResponse(code=Const['code.success'], data=tbaccounts)


@admin_permission('normal')
def user_listbankcard(r, mid):
    bankcards = Bankcard.objects.filter(user_id=mid)
    bankcards = [x.to_dict() for x in bankcards]
    return JsonResponse(code=Const['code.success'], data=bankcards)


@admin_permission('normal')
def task_get(r, tid):
    task = Task.objects.get(pk=tid)
    task_data = task.to_dict()
    task_data['store'] = task.store.to_dict()
    orders = task.order_set.all()
    orders_data = []
    for order in orders:
        order_data = order.to_dict()
        tb = order.tb
        if tb:
            order_data['taobao'] = tb.to_dict()
        orders_data.append(order_data)
    return JsonResponse(code=Const['code.success'], data={'task': task_data, 'orders': orders_data})


@admin_permission('finance')
@transaction.atomic
@mutex_lock
def finance_add(r, uid):
    user = User.objects.get(pk=uid)
    user.money_operate(int(r.REQUEST['type']), Decimal(r.REQUEST['amount']), r.REQUEST['reason'])
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def user_updatesellerlevel(r, uid):
    uid = int(uid)
    level = int(r.REQUEST['seller_level'])
    user = User.objects.get(pk=uid)
    user.seller_level = level
    user.save()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def store_updatestorename(r, sid):
    store = Store.objects.get(pk=sid)
    store.name = r.REQUEST['name']
    store.save()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def store_updatewangwang(r, sid):
    store = Store.objects.get(pk=sid)
    store.wangwang = r.REQUEST['wangwang']
    store.save()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def seller_return(r, uid):
    user = User.objects.get(id=uid)
    user.is_close_sellerreturn = 1 ^ user.is_close_sellerreturn
    user.save()
    return JsonResponse(code=Const['code.success'])


def order_detail(r):
    order = Order.objects.get(pk=r.REQUEST['order_id'])
    if order.status == 0:
        user = None
    else:
        user = order.tb.user
    task = order.task
    bankcard = order.bankcard
    task_type = task.task_type
    if bankcard:
        account = bankcard.account_id
        account_str = ' '.join([account[i:i + 4] for i in range(0, len(account), 4)])
    is_comment_order = True if order.order_type in (Const['model.order.type.normal'],
                                                    Const['model.order.type.keyword'],
                                                    Const['model.order.type.image'],
                                                    ) else False
    if order.receive_time:
        order.receive_time_str = get_datetime_by_stamp(order.receive_time)
    order.check_upgrade()

    steps = []
    for key in order.get_steps():
        order.get_steps()[key]['time_str'] = get_datetime_by_stamp(order.get_steps()[key]['create_time'])
        steps.append(order.get_steps()[key])
    return render(r, 'admin/order_detail.html', locals())


# def test(request):
#     store = Store.objects.get(id=354)
#     tb = TBAccount.objects.get(id=2046)
#     from tasks.models import StoreRecentBuyer
#     StoreRecentBuyer.objects.create(store=store, tb=tb, type=1)
#     return JsonResponse(code=1)
