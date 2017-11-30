# encoding: utf-8
from datetime import datetime, date
from decimal import Decimal
import json
import logging
import time
from django.db.models import Sum
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q
from django.db.models.expressions import F

from shouzhuan.const import Const
from management.models import Recharge, Withdraw
from shouzhuan.filters import rest_permission, mutex_lock, \
    admin_permission, need_login, userid_check, app_check
from shouzhuan.utils import JsonResponse, make_conditions, get_paginator, obj_to_dict, \
    sub_dict, msec_time, fix_length_random_int, obj_verify, get_stamp_by_date, \
    CsvResponse, get_datetime_by_stamp, get_stamp_by_datetime, protect_storename, before15
from tasks.forms import StoreCreateForm, TaskCreateForm
from tasks.models import Store, Task, Order, Appeal, AppealType, \
    StoreRecentBuyer, StoreRecentBuyerUser
from users.models import TBAccount, User, Record
from random import randint
from django.db import connection, transaction
from others.models import DailyReport

logger = logging.getLogger(__name__)



# #任务发布部分##
@rest_permission
def store_create(request):
    form = StoreCreateForm(request.POST)
    if form.is_valid():
        logger.debug(form.cleaned_data['name'])
        if Store.objects.filter(name=form.cleaned_data['name']).count() > 0:
            return JsonResponse(code=Const['code.store.exist'])
        store = Store.objects.create(**form.cleaned_data)
        return JsonResponse(code=Const['code.success'], data=store.to_dict())


@rest_permission
def store_modify(r):
    if Store.objects.filter(user_id=int(r.REQUEST['user_id']), id=int(r.REQUEST['store_id'])).count() > 0:
        if Store.objects.filter(name=r.REQUEST['name']).exclude(id=int(r.REQUEST['store_id'])).count() > 0:
            return JsonResponse(code=Const['code.store.exist'])
        Store.objects.filter(user_id=int(r.REQUEST['user_id']), id=int(r.REQUEST['store_id'])).update(
                name=r.REQUEST['name'], buy_time_limit=int(r.REQUEST['buy_time_limit']),
                wangwang=r.REQUEST['wangwang'], url=r.REQUEST['url'],
                address=r.REQUEST['address'])
        return JsonResponse(code=Const['code.success'])
    return JsonResponse(code=Const['code.request_error'])


@rest_permission
def store_delete(request):
    Store.objects.filter(user_id=int(request.REQUEST['user_id']), id=int(request.REQUEST['store_id'])).delete()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def task_create(request):
    form = TaskCreateForm(request.POST)
    if form.is_valid():
        formdata = form.cleaned_data
        logger.info('task_create %s' % formdata)

        if formdata['id']:
            task = Task.objects.get(pk=formdata['id'])
            if task.status != Const['model.task.status.need_payment']:
                return JsonResponse(code=Const['code.request_error'])
        if formdata['store_id']:
            store = Store.objects.get(id=formdata['store_id'])
            user = store.user
            if user.is_close_sellerreturn == 1 and formdata['return_type'] == 1:
                return JsonResponse(code=136, msg=u'您已多次未按时效返款，手段返款通道被关闭。请返回上一步选择平台返款，如须帮助联系平台管理员')
        # 验证
        ok = True

        if formdata['publish_start_date']:
            if int(formdata['publish_num']) <= 0 or int(formdata['publish_total']) <= 0:
                return JsonResponse(code=Const['code.request_error'])

        # if formdata['order_type_order_total4'] > formdata['order_type_order_total3']:
        #  return JsonResponse(code=Const['code.request_error']) 

        # 流量任务包含收藏任务，所以先减掉
        # formdata['order_type_order_total3'] -= formdata['order_type_order_total4']

        # 千人千面任务校验 order_type_order_total6不为0 其他为0
        if formdata['is_qian']:
            for i in range(1, 6):
                if formdata['order_type_order_total' + str(i)] > 0:
                    return JsonResponse(code=Const['code.request_error'], msg=u'任务提交有误，请刷新页面重新发布')
            if formdata['order_type_order_total6'] == 0:
                return JsonResponse(code=Const['code.request_error'], msg=u'任务提交有误，请刷新页面重新发布')

        all_sd_order = formdata['order_type_order_total0'] + formdata['order_type_order_total1'] + formdata[
            'order_type_order_total2'] + formdata['order_type_order_total6']
        all_flow_order = formdata['order_type_order_total3'] + formdata['order_type_order_total5']
        all_collect_order = formdata['order_type_order_total4']
        all_search_sd = all_search_flow = all_search_collect = 0
        if formdata['search_entry_total']:
            for i in range(1, formdata['search_entry_total'] + 1):
                key_order = 'search_entry_order_total' + str(i)
                key_flow = 'search_entry_flow_total' + str(i)
                key_collect = 'search_entry_collect_total' + str(i)
                key_order_num = formdata[key_order] if formdata[key_order] else 0
                key_flow_num = formdata[key_flow] if formdata[key_flow] else 0
                key_collect_num = formdata[key_collect] if formdata[key_collect] else 0
                all_search_sd = all_search_sd + key_order_num
                all_search_flow = all_search_flow + key_flow_num
                all_search_collect = all_search_collect + key_collect_num
            if all_sd_order != all_search_sd:
                return JsonResponse(code=Const['code.request_error'], msg=u'垫付任务数量有误')
            if all_flow_order != all_search_flow:
                return JsonResponse(code=Const['code.request_error'], msg=u'浏览任务数量有误')
            if all_collect_order != all_search_collect:
                return JsonResponse(code=Const['code.request_error'], msg=u'收藏任务数量有误')

        if int(formdata['order_type_order_total6']) > 0 >= int(formdata['step_interval']):
            return JsonResponse(code=Const['code.request_error'], msg=u"时间间隔不能为空")
        # logger.debug('b')
        # JSON封装
        total_price = 0
        commodities = []
        for i in range(1, formdata['commodity_total'] + 1):
            commodities.append({
                'num': formdata['commodity_num' + str(i)],
                'name': formdata['commodity_name' + str(i)],
                'url': formdata['commodity_url' + str(i)],
                'pic_path': formdata['commodity_pic_path' + str(i)],
                'displayprice': formdata['commodity_displayprice' + str(i)],
                'unitprice': formdata['commodity_unitprice' + str(i)],
            })
            # 商品单价*商品数量
            total_price = total_price + Decimal(formdata['commodity_unitprice' + str(i)]) * Decimal(
                    formdata['commodity_num' + str(i)])
        # 单品价格之前的限制是1200，但是现在要改为8000
        if total_price > 8000:
            return JsonResponse(code=Const['code.request_error'])
        search_entries = []
        for i in range(1, formdata['search_entry_total'] + 1):
            key_order = 'search_entry_order_total' + str(i)
            key_flow = 'search_entry_flow_total' + str(i)
            key_collect = 'search_entry_collect_total' + str(i)
            search_entries.append({
                'keyword': formdata['search_entry_keyword' + str(i)],
                'pay_num': formdata['search_entry_pay_num' + str(i)],
                'order_total': formdata[key_order] if formdata[key_order] else 0,
                'flow_total': formdata[key_flow] if formdata[key_flow] else 0,
                'collect_total': formdata[key_collect] if formdata[key_collect] else 0,
                'sort_method': formdata['search_entry_sort' + str(i)],
            })
        flow = False
        if not search_entries:
            flow = False
        elif search_entries[0]["flow_total"] > 0 or search_entries[0]["collect_total"] > 0:
            flow = True
        order_types = []
        for i in range(0, 7):
            order_types.append({
                'order_total': formdata['order_type_order_total' + str(i)],
            })

        '''
    "task_type": "0",
    "publish_start_date": "2015-10-04",
    "publish_start_time": "16:00",
    "publish_end_time": "20:00",
    "publish_num": "5",

    "order_type_order_total0": 10,
    "order_type_order_total1": 0,
    "order_type_order_total2": 0,
    "order_type_order_total3": "7",
    "order_type_order_total4": "0",
    "order_type_order_total5": 0,

    "search_entry_total": 3,

    "search_entry_keyword1": "SearchA",
    "search_entry_order_total1": 2,
    "search_entry_flow_total1": 2,
    "search_entry_keyword2": "SearchB",
    "search_entry_order_total2": 3,
    "search_entry_flow_total2": 2,
    "search_entry_keyword3": "SearchC",
    "search_entry_order_total3": 5,
    "search_entry_flow_total3": 3
        '''
        wangwang_condition = {
            'tb_register_time': formdata['tb_register_time'],
            'tb_gender': formdata['tb_gender'],
            'tb_age': formdata['tb_age'],
            'tb_is_credit_card_open': formdata['tb_is_credit_card_open'],
            'tb_wangwang_level': formdata['tb_wangwang_level'],
            'tb_is_huabei_open': formdata['tb_is_huabei_open'],
            # 是否假聊
            'tb_is_talk': formdata['tb_is_talk']
        }
        qian_search_entry = []
        for i in range(1, 7):
            if formdata['qian_keyword' + str(i)]:
                qian_search_entry.append(formdata['qian_keyword' + str(i)])
        others = {}
        if formdata['special_code']:
            others['special_code'] = formdata['special_code']
        if formdata['special_pics']:
            others['special_pics'] = formdata['special_pics']
        formdata['total_price'] = total_price
        formdata['others'] = json.dumps(others, cls=DjangoJSONEncoder)
        formdata['commodities'] = json.dumps(commodities, cls=DjangoJSONEncoder)
        formdata['search_entries'] = json.dumps(search_entries, cls=DjangoJSONEncoder)
        formdata['order_types'] = json.dumps(order_types, cls=DjangoJSONEncoder)
        formdata['wangwang_condition'] = json.dumps(wangwang_condition, cls=DjangoJSONEncoder)
        formdata['qian_search_entry'] = json.dumps(qian_search_entry, cls=DjangoJSONEncoder)
        formdata = sub_dict(formdata, 'id', 'platform', 'store_id', 'task_type', 'return_type',
                            'low_price', 'up_price', 'commodity_address', 'publish_start_date',
                            'publish_start_time', 'publish_end_time', 'publish_num', 'publish_total', 'bonus',
                            'task_remark', 'commodities', 'order_types', 'search_entries',
                            'order_comment', 'comment_keyword', 'comment_image', 'others', 'total_price',
                            'step_interval', 'prepublish', 'wangwang_condition', 'is_qian', 'qian_search_entry')
        if not 'id' in formdata:
            while True:
                formdata['id'] = fix_length_random_int(7)
                if Task.objects.filter(pk=formdata['id']).count() == 0:
                    break
        t = Task(**formdata)
        t.flow = flow
        t.save()
        return JsonResponse(code=Const['code.success'], data=t.to_dict())
    return JsonResponse(code=Const['code.request_error'], msg=form.errors)


@transaction.atomic
@rest_permission
def task_pay(r, mid):
    task = Task.objects.get(pk=mid)
    user = task.store.user
    payment = task.payment()
    if task.status != Const['model.task.status.need_payment']:
        return JsonResponse(code=Const['code.request_error'])
        # 邀请人奖励 商家推广奖励，之前被去掉了，现在又放了回来了
        now = msec_time()
        if user.inviter and (now - user.register_time < Const['ms.per.year']):
            award = task.get_inviter_award()
            user.inviter.money_operate(Const['model.record.commission'], award
                                       , '商家推广奖励，商家id：%d' % user.id,
                                       Const['model.record.category.promote'])
            user.inviter.promote_award = user.inviter.promote_award + award
            user.inviter.save()

    ret = user.money_operatesafe(
            Const['model.record.pricipal'],
            -payment,
            '任务支出，任务编号：' + str(task.id),
            Const['model.record.category.taskpay'])

    if ret < 0:
        return JsonResponse(code=Const['code.insufficient.balance'], msg=u'余额不足')
    # user.principal = user.principal - payment;
    user.seller_orders = user.seller_orders + task.get_total_buy_orders()
    user.set_user_level('s')
    user.save()
    # Record.objects.create(id=Record.objects.avaliable_id(),
    #                      user=user, amount=(-payment), balance=user.principal,
    #                      type=Const['model.record.pricipal'],
    #                      description=('任务支出，任务编号：' + str(task.id)),
    #                      category=Const['model.record.category.taskpay'])
    task.status = Const['model.task.status.in_progress']
    if True or user.flag_has(Const['user.flags.taskfreeverify']):
        task.verify_status = Const['model.verify.check_pass']
        _generate_task_order(task)
    task.save()
    return JsonResponse(code=Const['code.success'])


@transaction.atomic
def task_verify(r, mid):
    task = Task.objects.get(pk=mid)
    verify = int(r.REQUEST['verify'])
    if task.verify_status == Const['model.verify.need_check']:
        task.verify_status = verify
        task.save()
        if verify == Const['model.verify.check_pass']:
            _generate_task_order(task)
    return JsonResponse(code=Const['code.success'])


'''
计算所有任务的发布时间， 
@start_date=开始发布日期, 
@start_time=开始发布时间, 
@end_time=结束发布时间,
@daily_amount=每天发布数量
@total_amount=任务总数

@return Array[@total_amount](datetime)
'''


def _get_publish_time(times, order_type):
    type_times = times[order_type]
    if type_times['index'] < len(type_times['times']):
        time = type_times['times'][type_times['index']]
        type_times['index'] = type_times['index'] + 1
    else:
        time = 0
    return time


def _calc_publish_time(start_date, start_time, end_time, daily_amount_rate, total_amount):
    times = []

    now = msec_time()

    p_start_time = datetime.combine(start_date, start_time)
    p_end_time = datetime.combine(start_date, end_time)

    p_start_time_st = get_stamp_by_datetime(p_start_time)
    p_end_time_st = get_stamp_by_datetime(p_end_time)
    daily_amount = int(total_amount * daily_amount_rate);
    # 两头对齐要-1
    daily_amount = daily_amount - 1;
    if daily_amount <= 1:
        daily_amount = 1
    # 先计算时间间隔
    interval = (p_end_time_st - p_start_time_st) / daily_amount

    logger.info('interval:%d' % interval)

    index = 0
    p_next_time_st = p_start_time_st
    while index < total_amount:
        if now - p_next_time_st > 0 and daily_amount_rate < 1:
            p_next_time_st = p_next_time_st + interval
            continue
        if p_next_time_st - p_end_time_st > 0:
            p_start_time_st = p_start_time_st + Const['ms.per.day']
            p_end_time_st = p_end_time_st + Const['ms.per.day']
            p_next_time_st = p_start_time_st;
            continue
        times.append(p_next_time_st)
        p_next_time_st = p_next_time_st + interval
        index = index + 1
    return times


# 0-99999, 0-19999:20000-49999:50000-99999
def _get_order_weights():
    return randint(20000, 49999)


def _generate_task_order(task):
    search_entries = json.loads(task.search_entries)
    order_types = json.loads(task.order_types)
    publish_time = 0
    # 刷单
    sd_order_enum = (Const['model.order.type.normal'], Const['model.order.type.keyword'],
                     Const['model.order.type.image'], Const['model.order.type.advance'])

    dianzi = task.dianzi()
    if task.publish_start_date != None:
        has_publish_time = True
        publish_times = []
        daily_amount_rate = 0.0
        if task.publish_num > 0:
            if task.publish_total > 0:
                daily_amount_rate = float(task.publish_num) / task.publish_total
            else:
                # 第一给有数字的刷单任务个数计算总任务
                for o in sd_order_enum:
                    total_amount = order_types[o]['order_total']
                    if total_amount > 0:
                        daily_amount_rate = float(task.publish_num) / total_amount
                        pass
        else:
            daily_amount_rate = 1.0

        for x in range(0, 7):
            total_amount = order_types[x]['order_total']
            if total_amount > 0:
                publish_times.append({'index': 0, 'times': _calc_publish_time(task.publish_start_date, \
                                                                              task.publish_start_time,
                                                                              task.publish_end_time, daily_amount_rate,
                                                                              total_amount)})
            else:
                publish_times.append({'index': 0, 'times': []})
        # 所有任务的发布时间都算好了
        logger.info('daily_amount_rate:%f, times:%s' % (daily_amount_rate, publish_times))
    else:
        has_publish_time = False

    if search_entries:
        search_entry_index = 0
        search_orders = search_entries[search_entry_index]['order_total']
        for order_type in sd_order_enum:
            type_orders = order_types[order_type]['order_total']
            for i in range(0, type_orders):
                if search_orders == 0:
                    search_entry_index = search_entry_index + 1
                    search_orders = search_entries[search_entry_index]['order_total']
                if has_publish_time:
                    publish_time = _get_publish_time(publish_times, order_type)
                Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type,
                                     task=task, search_entry_index=search_entry_index,
                                     seller_payment=task.order_payment(order_type),
                                     publish_time=publish_time, buyer_principal=dianzi,
                                     weights=_get_order_weights(), step_interval=task.step_interval)
                logger.info('publish_time for order_type %d, search_index %d, %d' % (
                    order_type, search_entry_index, publish_time))
                search_orders = search_orders - 1
    else:
        for order_type in sd_order_enum:
            type_orders = order_types[order_type]['order_total']
            for i in range(0, type_orders):
                if has_publish_time:
                    publish_time = _get_publish_time(publish_times, order_type)
                Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type,
                                     task=task, search_entry_index=-1,
                                     seller_payment=task.order_payment(order_type),
                                     publish_time=publish_time, buyer_principal=dianzi,
                                     weights=_get_order_weights(), step_interval=task.step_interval)
                logger.info('publish_time for order_type %d, search_index %d, %d' % (order_type, -1, publish_time))

    # 流量
    if search_entries:
        search_entry_index = 0
        search_orders = search_entries[search_entry_index]['flow_total']
        flow_order_enum = (Const['model.order.type.flow'], Const['model.order.type.direct'])
        for order_type in flow_order_enum:
            type_orders = order_types[order_type]['order_total']
            for i in range(0, type_orders):
                if search_orders == 0:
                    search_entry_index = search_entry_index + 1
                    search_orders = search_entries[search_entry_index]['flow_total']
                if has_publish_time:
                    publish_time = _get_publish_time(publish_times, order_type)
                Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type,
                                     task=task, search_entry_index=search_entry_index,
                                     seller_payment=task.order_payment(order_type),
                                     publish_time=publish_time, weights=_get_order_weights(),
                                     step_interval=task.step_interval)
                logger.info('publish_time for order_type %d, search_index %d, %d' % (
                    order_type, search_entry_index, publish_time))
                search_orders = search_orders - 1
    else:
        flow_order_enum = (Const['model.order.type.flow'], Const['model.order.type.direct'])
        for order_type in flow_order_enum:
            type_orders = order_types[order_type]['order_total']
            for i in range(0, type_orders):
                if has_publish_time:
                    publish_time = _get_publish_time(publish_times, order_type)
                Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type, \
                                     task=task, search_entry_index=-1,
                                     seller_payment=task.order_payment(order_type),
                                     publish_time=publish_time, weights=_get_order_weights())
                logger.info('publish_time for order_type %d, search_index %d, %d' % (order_type, -1, publish_time))

    # 收藏
    if search_entries:
        search_entry_index = 0
        search_orders = search_entries[search_entry_index]['collect_total']
        order_type = Const['model.order.type.collect']
        type_orders = order_types[order_type]['order_total']
        for i in range(0, type_orders):
            if search_orders == 0:
                search_entry_index = search_entry_index + 1
                search_orders = search_entries[search_entry_index]['collect_total']
            if has_publish_time:
                publish_time = _get_publish_time(publish_times, order_type)
            Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type,
                                 task=task, search_entry_index=search_entry_index,
                                 seller_payment=task.order_payment(order_type),
                                 publish_time=publish_time, weights=_get_order_weights(),
                                 step_interval=task.step_interval)
            logger.info('publish_time for order_type %d, search_index %d, %d' % (
                order_type, search_entry_index, publish_time))
            search_orders = search_orders - 1
    else:
        order_type = Const['model.order.type.collect']
        type_orders = order_types[order_type]['order_total']
        for i in range(0, type_orders):
            if has_publish_time:
                publish_time = _get_publish_time(publish_times, order_type)
            Order.objects.create(id=Order.objects.avaliable_id(), order_type=order_type, \
                                 task=task, search_entry_index=-1,
                                 seller_payment=task.order_payment(order_type),
                                 publish_time=publish_time, weights=_get_order_weights())
            logger.info('publish_time for order_type %d, search_index %d, %d' % (order_type, -1, publish_time))


# # 任务浏览、接单##
@rest_permission
def order_listavaliable(r):
    user = User.objects.get(pk=r.REQUEST['user_id'])
    order_type = int(r.REQUEST['order_type'])
    start, num = get_paginator(r)
    now = datetime.now()
    # args=[Q(publish_time__lte=now)|Q(publish_time__isnull=True),\
    #      Q(status=Const['model.order.status.init']),]
    args = [Q(status=Const['model.order.status.init']), ]
    buy_order_q = Q(order_type__in=(Const['model.order.type.normal'],
                                    Const['model.order.type.keyword'],
                                    Const['model.order.type.image']))
    if r.c_type == Const['model.device.android'] and r.c_versioncode > 36:
        buy_order_q = Q(order_type__in=(Const['model.order.type.normal'],
                                        Const['model.order.type.keyword'],
                                        Const['model.order.type.image'],
                                        Const['model.order.type.advance']))

    if order_type == Const['app.order.type.mobile_tb']:
        args.append(buy_order_q)
        args.append(Q(task__task_type=Const['model.task.type.mobile_taobao']))
        # TODO:: is tm
        # args.append(Q(task__store__istm=False))
    elif order_type == Const['app.order.type.pc_tb']:
        args.append(buy_order_q)
        args.append(Q(task__task_type=Const['model.task.type.pc_taobao']))
    elif order_type == Const['app.order.type.mobile_scan']:
        args.append(Q(order_type__in=(Const['model.order.type.flow'],
                                      Const['model.order.type.collect'],
                                      Const['model.order.type.direct'])))
    elif order_type == Const['app.order.type.mobile_tm']:
        # args.append(buy_order_q)
        # args.append(Q(task__task_type=Const['model.task.type.mobile_taobao']))
        # args.append(Q(task__store__istm=True))
        return JsonResponse(code=Const['code.success'], data=[])
    elif order_type == Const['app.order.type.special']:
        args.append(buy_order_q)
        args.append(Q(task__task_type=Const['model.task.type.special']))

    if 'task_id' in r.REQUEST:
        args.append(Q(task_id=int(r.REQUEST['task_id'])))

    ordering = 'if(publish_time > %d, publish_time, 0)' % msec_time()
    # timestamp = before15()
    orders = Order.objects.filter(*args) \
                 .extra(select={'_ordering': ordering}, order_by=('_ordering', '-weights', 'receive_time')) \
                 .exclude(task__status=Const['model.task.status.frozen'])[start:start + num]
    logger.info(orders.query)
    data = []
    for o in orders:
        t = o.task
        search_entry = json.loads(t.search_entries)[o.search_entry_index] if o.search_entry_index >= 0 else None
        data.append({'order_id': o.id,
                     'store_id': o.task.store.user_id,
                     'pay': o.commision(user),
                     'goods_num': len(json.loads(o.task.commodities)),
                     'cost': o.task.total_price,
                     'return_type': o.task.return_type,
                     'requirements': o.task.task_remark,
                     'address': o.task.commodity_address,
                     'order_comment': o.task.order_comment,
                     'up_price': o.task.up_price,
                     'low_price': o.task.low_price,
                     'search_key': search_entry['keyword'] if search_entry else '',
                     'sort_method': search_entry[
                         'sort_method'] if search_entry and 'sort_method' in search_entry else 0,
                     'search_position': search_entry['pay_num'] if search_entry else '',
                     'order_type2': o.order_type,
                     'publish_time': o.publish_time,
                     'is_qian': o.task.is_qian,
                     'wangwang_condition': json.loads(o.task.wangwang_condition),
                     })

    return JsonResponse(code=Const['code.success'], data=data)


@app_check
def orders_num(r):
    ordering = 'if(publish_time > %d, publish_time, 0)' % msec_time()
    args = [Q(status=Const['model.order.status.init']), Q(order_type__in=(Const['model.order.type.normal'],
                                                                          Const['model.order.type.keyword'],
                                                                          Const['model.order.type.image'],
                                                                          Const['model.order.type.advance']))]

    mobile_tb_num = Order.objects.filter(*args).filter(Q(task__task_type=Const['model.task.type.mobile_taobao'])) \
        .extra(select={'_ordering': ordering}).count()
    pc_tb_num = Order.objects.filter(*args).filter(Q(task__task_type=Const['model.task.type.pc_taobao'])) \
        .extra(select={'_ordering': ordering}).count()
    mobile_tm_num = Order.objects.filter(*args).filter(Q(task__task_type=Const['model.task.type.mobile_taobao'])) \
        .extra(select={'_ordering': ordering}).count()
    special_num = Order.objects.filter(*args).filter(Q(task__task_type=Const['model.task.type.special'])) \
        .extra(select={'_ordering': ordering}).count()
    mobile_scan_num = Order.objects.filter(Q(order_type__in=(Const['model.order.type.flow'],
                                                             Const['model.order.type.collect'],
                                                             Const['model.order.type.direct']))) \
        .filter(status=Const['model.order.status.init']).count()

    data = {'mobile_tb': mobile_tb_num, 'pc_tb': pc_tb_num, 'mobile_scan': mobile_scan_num,
            'mobile_tm': mobile_tm_num, 'special': special_num}
    return JsonResponse(code=Const['code.success'], data=data)


@app_check
@rest_permission
# only support type=3 or 4
def order_listgroup(r):
    user = User.objects.get(pk=r.REQUEST['user_id'])
    start, num = get_paginator(r)
    now = datetime.now()
    sql = 'select count(t.task_id) as `remain_count`, if(publish_time > %d, publish_time, 0) as `_ordering`,t.* from (SELECT * from tasks_order where order_type in (3,4,5) and status = 0 order by publish_time ) as t group by task_id order by _ordering' % msec_time()

    if start == 0:
        sql += ' limit %d' % num
    else:
        sql = sql + ' limit %d,%d' % (start, num)

    # cursor = connection.cursor()
    #
    # # 数据检索操作,不需要提交
    # cursor.execute(sql)
    # rows = cursor.fetchall()
    # data = []
    # for item in rows:
    #     remain_count = item[0]
    #     order_id = item[2]
    #     task_id = item[10]
    #     task = Task.objects.filter(pk=task_id)
    #     o = Order.objects.get(pk=order_id)
    #     data.append({'order_id': o.id,
    #                  'task_id': o.task.id,
    #                  'store_id': o.task.store.user_id,
    #                  'store_name': protect_storename(o.task.store.name),
    #                  'goods_num': len(json.loads(o.task.commodities)),
    #                  'order_type2': o.order_type,
    #                  'publish_time': o.publish_time,
    #                  'remain_count': o.remain_count,
    #                  })
    # return JsonResponse(code=Const['code.success'], data=data)
    #

    orders = Order.objects.raw(sql)
    data = []
    for o in orders:
        t = o.task
        search_entry = json.loads(t.search_entries)[o.search_entry_index] if o.search_entry_index >= 0 else None
        data.append({'order_id': o.id,
                     'task_id': o.task.id,
                     'store_id': o.task.store.user_id,
                     'store_name': protect_storename(o.task.store.name),
                     'goods_num': len(json.loads(o.task.commodities)),
                     'order_type2': o.order_type,
                     'publish_time': o.publish_time,
                     'remain_count': o.remain_count,
                     })
    return JsonResponse(code=Const['code.success'], data=data)


@app_check
# @rest_permission
def order_detailbyappv2(r, mid):
    o = Order.objects.get(pk=mid)
    t = o.task
    commodities = json.loads(t.commodities)
    search_entry = json.loads(t.search_entries)[o.search_entry_index] if o.search_entry_index >= 0 else None
    data = {
        'seller_id': t.store.user_id,
        'order_id': o.id,
        'major_commodity': commodities[:1],
        'extras': commodities[1:],
        'store_name': protect_storename(t.store.name),
        'return_type': t.return_type,
        'cost': o.task.total_price,
        'frozen': o.frozen,
        'task_remark': t.task_remark,
        'search_key': search_entry['keyword'] if search_entry else '',
        'sort_method': search_entry['sort_method'] if search_entry and 'sort_method' in search_entry else 0,
        'search_position': search_entry['pay_num'] if search_entry else '',
        'up_price': t.up_price,
        'low_price': t.low_price,
        'address': t.commodity_address,
        'order_comment': t.order_comment,
        'receive_time': o.receive_time,
        'tb_wangwang': o.tb.wangwang if o.tb else '',
        'order_status': o.status,
        'step_1': o.get_step1_pic(),
        'step_2': o.get_step2_pic(),
        'step_3': o.get_step3_pic(),
        'step_0': o.get_step0_pic(),
        'step_extra1': o.get_extrastep1_pic(),
        'step_extra2': o.get_extrastep2_pic(),
        'qian_create_time': o.get_qian_create_time() * 1000,
        'qian_interval': o.get_qian_interval_ms(),
        'last_step_time': o.get_extrastep_time() * 1000,
        'step_interval': o.get_step_interval_ms(),
        'return_account': o.bankcard.account_id if o.bankcard else None,
        'bank_name': o.bankcard.bank_name if o.bankcard else None,
        'comment_img': o.get_comment_pic(),
        'order_type': o.get_general_order_type(),
        'image_require': json.loads(t.comment_image) if t.comment_image and \
                                                        (o.order_type == Const['model.order.type.image']) else None,
        'keyword_require': json.loads(t.comment_keyword) if t.comment_keyword and \
                                                            (
                                                                o.order_type == Const[
                                                                    'model.order.type.keyword'])else None,
        'buyer_commit': o.get_buyer_commit(),
        'seller_commit': o.get_seller_commit(),
        'others': json.loads(t.others) if t.others else None,
        'order_type2': o.order_type,
        'is_qian': o.task.is_qian,
        'qian_search_entry': o.task.qian_search_entry,
        'wangwang_condition': json.loads(o.task.wangwang_condition),
    }
    return JsonResponse(code=Const['code.success'], data=data)


def _order_can_receive(userid):
    '''
    if a user can receive order.
    :param userid: user_id for user
    :return: (code, msg)
    '''

    code = 0
    msg = u''

    sql = u'''SELECT user_can_receive_order(%s)''' % userid
    cursor = connection.cursor()
    cursor.execute(sql)
    raw = cursor.fetchone()
    if raw is None or len(raw) <= 0:
        code = Const['code.request_error']
        msg = u'系统异常'
    else:
        if raw[0] == 1:
            code = Const['code.success']
            msg = u''
        elif raw[0] == 1001:
            code = Const['code.request_error']
            msg = u'有任务未操作， 请先操作后再接新任务'
        elif raw[0] == 1002:
            code = Const['code.idc_verify.error']
            msg = u'身份证没有验证'
        else:
            code = Const['code.request_error']
            msg = u'服务器异常'
    return code, msg


@app_check
@rest_permission
@mutex_lock
def order_receive(r, mid):
    if r.c_userid <= 0:
        return JsonResponse(code=Const['code.request_error'], msg=u'服务器异常')
    code, msg = _order_can_receive(r.c_userid)
    if code != Const['code.success']:
        return JsonResponse(code=code, msg=msg)

    conditions = make_conditions(r, tb_id='tb_id', bankcard_id='bankcard_id', device='device')

    order = Order.objects.get(pk=mid)
    if order.status != Const['model.order.status.init']:
        return JsonResponse(code=Const['code.order.has.been.received'], msg='订单已经被接')

    tb = TBAccount.objects.get(pk=conditions['tb_id'])
    store = order.task.store

    # 加入设备拦截 禁止IOS操作千人千面任务
    if r.c_type == Const['model.device.ios'] and order.task.is_qian == 1:
        return JsonResponse(code=Const['code.request_error'], msg='千人千面任务暂不支持iOS用户')

    # 新人限制
    if tb.user.is_new == 1 and order.is_buy_order():
        if tb.user.liulan_order_num < 5:
            return JsonResponse(code=Const['code.request_error'], msg='新人先做满5单浏览任务')
        # 好评单大于30或者注册时间大于30天解除新人限制
        if tb.user.haoping_order_num >= 30 and int(time.time() * 1000) - tb.user.register_time > 30 * 24 * 60 * 60 * 1000:
            tb.user.is_new = 0
            tb.user.save()
        else:
            if order.buyer_principal > 200:
                return JsonResponse(code=Const['code.request_error'], msg='暂不能接此单子')

    # 接单金额限制
    if tb.user.order_money_limit and order.buyer_principal > tb.user.order_money_limit:
        return JsonResponse(code=Const['code.request_error'], msg='您的条件不符合商家要求')
    # 旺旺要求
    wangwang_condition = order.task.wangwang_condition
    if wangwang_condition:
        wangwang_condition = json.loads(wangwang_condition)
        # 性别不为空并且不等于刷手淘宝的性别
        if wangwang_condition['tb_gender'] is not None and not tb.gender == wangwang_condition['tb_gender']:
            return JsonResponse(code=Const['code.request_error'], msg=u'与订单性别要求不符')
        if wangwang_condition['tb_age'] is not None and not tb.age == wangwang_condition['tb_age']:
            return JsonResponse(code=Const['code.request_error'], msg=u'与订单年龄要求不符')
        if wangwang_condition['tb_register_time'] is not None and tb.register_time > wangwang_condition[
            'tb_register_time']:
            return JsonResponse(code=Const['code.request_error'], msg=u'与订单注册时间要求不符')
        if wangwang_condition['tb_wangwang_level'] is not None and tb.wangwang_level < wangwang_condition[
            'tb_wangwang_level']:
            return JsonResponse(code=Const['code.request_error'], msg=u'与订单旺旺等级要求不符')
    today = time.mktime(date.today().timetuple()) * 1000
    before_n_d = today - Const['ms.per.day'] * int(store.buy_time_limit)
    before5d = today - Const['ms.per.day'] * 5
    # before15d = today - Const['ms.per.day'] * 15
    before7d = today - Const['ms.per.day'] * 7
    before1d = today - Const['ms.per.day']
    # 购买任务
    if order.is_buy_order():
        # 判断该旺旺号是否被冻结
        if tb.frozen_start_datetime and tb.frozen_days:
            end_time = tb.frozen_start_datetime + datetime.timedelta(days=tb.frozen_days)
            now = datetime.datetime.utcnow()
            now_stmp = time.mktime(now.timetuple())
            end_time_stmp = time.mktime(end_time.timetuple())
            if now_stmp < end_time_stmp:
                msg = '此旺旺号已被冻结' + str(tb.frozen_days) + '天，如有疑问请联系客服'
                return JsonResponse(code=Const['code.request_error'], msg=msg)
        # 1.判断当天接单数量限制
        if tb.today_receive_orders >= Const['max.receive.ordersperday']:
            return JsonResponse(code=Const['code.today.receive.orders.exceed'],
                                msg=u'您的今日接单数已满！请更换淘宝账户试试')
        # 2.判断该买手的此淘宝账号是否在此店铺下购买过，如果购买过判断间隔时间
        store_recent_buy = StoreRecentBuyer.objects.filter(tb_id=tb.id,
                                                           store_id=store.id,
                                                           type__in=(Const['model.order.type.normal'],
                                                                     Const['model.order.type.keyword'],
                                                                     Const['model.order.type.image'],
                                                                     Const['model.order.type.advance'])
                                                           ).extra(
                order_by=('-id', 'tb_id'))
        print store_recent_buy.query
        if len(store_recent_buy) > 0 and store_recent_buy[0].create_time >= before_n_d:
            return JsonResponse(code=Const['code.recent.buyer'],
                                msg=u'该商家要求%d天内无法接该店铺任务,请更换淘宝账户或去其他店铺试试' % store.buy_time_limit)
        # 3.判断该买手是否在该商家的其他店铺购买过如果购买过，7天内不能购买此商家其他店铺
        # 获取该商家的其他店铺
        stores = Store.objects.filter(user=store.user)
        for s in stores:
            inner_recent = StoreRecentBuyerUser.objects.filter(user_id=tb.user_id,
                                                               store_id=s.id,
                                                               type__in=(Const['model.order.type.normal'],
                                                                         Const['model.order.type.keyword'],
                                                                         Const['model.order.type.image'],
                                                                         Const['model.order.type.advance'])
                                                               ).extra(order_by=('-id', 'user_id'))
            if len(inner_recent) > 0 and inner_recent[0].create_time >= before7d:
                return JsonResponse(code=Const['code.recent.buyer'],
                                    msg=u'7天之内您已经接了该商家任务,请更换淘宝账户或去其他店铺试试')
    # 浏览任务
    else:
        recent_collect = StoreRecentBuyer.objects.filter(tb_id=tb.id,
                                                         store_id=store.id,
                                                         type=Const['model.order.type.collect']).extra(
                order_by=('-id', 'tb_id')
        )
        recent_flow = StoreRecentBuyer.objects.filter(tb_id=tb.id,
                                                      store_id=store.id,
                                                      type=Const['model.order.type.flow']).extra(
                order_by=('-id', 'tb_id')
        )
        # 5天之内有收藏任务， 就不能接收藏任务了
        if len(recent_collect) > 0 and recent_collect[0].create_time >= before5d:
            return JsonResponse(code=Const['code.recent.buyer'], msg=u'5天之内不能接同一家浏览+收藏任务')

        # 1天之内有收藏/浏览任务不能接浏览任务了
        if (len(recent_collect) > 0 and recent_collect[0].create_time >= before1d) \
                or (len(recent_flow) > 0 and recent_flow[0].create_time >= before1d):
            return JsonResponse(code=Const['code.recent.buyer'], msg=u'1天之内不能接同一家浏览/收藏任务')

            # if (order.order_type == Const['model.order.type.collect'] and not can_collect) \
            #         or (order.order_type == Const['model.order.type.flow'] and not can_flow):
            #     return JsonResponse(code=Const['code.recent.buyer'], msg=flow_msg)

    task = order.task
    if order.publish_time > msec_time():
        return JsonResponse(code=Const['code.receive.time.error'])
    if task.store.user.has_blacklist_with(tb.user_id):
        return JsonResponse(code=Const['code.receive.in.blacklist'])
    with transaction.atomic():
        order.tb = tb
        order.bankcard_id = conditions['bankcard_id'] if 'bankcard_id' in conditions else None
        order.device = conditions['device'] if 'device' in conditions else None
        order.status = Const['model.order.status.received']
        order.receive_time = msec_time()
        order.buyer_gain = order.commision(tb.user)
        order.save()
        StoreRecentBuyerUser.objects.create(user=tb.user, store=store, type=order.order_type)
        StoreRecentBuyer.objects.create(store=store, tb=tb, type=order.order_type)
        if order.is_buy_order():
            order.tb.user.notice_set(Const['model.remind.received'], True)
            tb.today_receive_orders += 1
            tb.save()
        else:
            order.tb.user.notice_set(Const['model.remind.flowReceived'], True)
    return JsonResponse(code=Const['code.success'])


# 任务具体操作##
def _general_add_order_step(o, step_num, prev_status, next_status, **step):
    if o.status != prev_status:
        return False
    nowt = msec_time()
    step['create_time'] = nowt
    o.add_step_by(step_num, **step)
    o.status = next_status
    o.update_time = nowt
    return True


def _general_order_process(r, oid, step_num, prev_status, next_status):
    o = Order.objects.get(pk=oid)
    if o.frozen:
        return JsonResponse(code=Const['code.order.frozen'], msg=u'订单已冻结无法操作')
    params = r.REQUEST
    step = {}
    if 'pic_num' in params:
        pic_num = int(params['pic_num'])
        step['pic_path'] = []
        for i in range(pic_num):
            step['pic_path'].append(params['pic' + str(i)])
        logger.debug(step)
    if _general_add_order_step(o, step_num, prev_status, next_status, **step):
        o.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@app_check
@rest_permission
def order_operategroup(r, mid):
    o = Order.objects.get(pk=mid)
    if o.status not in [
        Const['model.order.status.received'],
        Const['model.order.status.step9'],
        Const['model.order.status.step10'],
    ]:
        return JsonResponse(code=Const['code.request_error'])
    params = r.REQUEST

    nowt = msec_time()
    if o.order_type != Const['model.order.type.advance']:
        return JsonResponse(code=Const['code.order.steperror'], msg="客户端操作错误")

    if o.status == Const['model.order.status.received'] and \
            (
                        ('step_1_pic' not in params or len(params['step_1_pic']) <= 2) or
                        ('step_2_pic' not in params or len(params['step_2_pic']) <= 2)
            ):
        return JsonResponse(code=Const['code.order.steperror'], msg='数据提交错误')
    elif o.status == Const['model.order.status.step9'] and \
            (
                    # TODO:: check
                        (o.get_extrastep_time() + o.get_step_interval_ms()) >= nowt
            ):
        return JsonResponse(code=Const['code.order.steplocked'], msg="操作时间未到, 请在浏览%d小时后操作" % (o.step_interval * 24))

    step = {}
    if o.status == Const['model.order.status.step9']:
        for i in range(1, 4):
            if ('step_' + str(i) + '_pic') in params:
                step['pic_path'] = json.loads(params['step_' + str(i) + '_pic'])
            step['create_time'] = nowt
            if i == 3:
                step['buyer_commit'] = Decimal(params['buyer_commit'])
            o.add_step_by(i - 1, **step)
        o.status = Const['model.order.status.step3']
        o.task.store.user.notice_set(Const['model.remind.no_money'], True)
        # o.task.store.user.save()
    elif o.status == Const['model.order.status.step10']:
        # 肯定是千人千面任务 并且第一步已经做完 千人千面任务第二部：添加收藏加购物车的照片
        step['pic_path'] = json.loads(params['step_1_pic'])
        step['create_time'] = nowt
        o.add_step_by(9, **step)
        step['pic_path'] = json.loads(params['step_2_pic'])
        step['create_time'] = nowt
        o.add_step_by(8, **step)
        o.status = Const['model.order.status.step9']
    else:
        # 已接单状态分为 千人千面任务和普通延迟任务
        if o.task.is_qian == 0:
            # 普通延迟任务第一步
            step['pic_path'] = json.loads(params['step_1_pic'])
            step['create_time'] = nowt
            o.add_step_by(9, **step)
            step['pic_path'] = json.loads(params['step_2_pic'])
            step['create_time'] = nowt
            o.add_step_by(8, **step)
            o.status = Const['model.order.status.step9']
        elif o.task.is_qian == 1:
            # 千人千面任务第一步

            step['pic_path'] = json.loads(params['step_0_pic'])
            step['create_time'] = nowt
            # if o.get_qian_create_time():
            #     step['create_time'] = o.get_qian_create_time()
            o.add_step_by(10, **step)
            o.status = Const['model.order.status.step10']
    o.update_time = nowt
    o.save()
    return JsonResponse(code=Const['code.success'])


@app_check
@rest_permission
def order_operate(r, mid):
    o = Order.objects.get(pk=mid)
    if o.status != Const['model.order.status.received']:
        return JsonResponse(code=Const['code.request_error'])
    if o.frozen:
        return JsonResponse(code=Const['code.order.frozen'], msg=u'订单已冻结无法操作')
    params = r.REQUEST

    # 收藏任务 需要第二步
    logger.info(params)
    if o.order_type == Const['model.order.type.collect']:
        if 'step_2_pic' not in params or len(params['step_2_pic']) <= 2:
            return JsonResponse(code=Const['code.order.steperror'])

    nowt = msec_time()
    if o.is_buy_order():
        for i in range(1, 4):
            step = {}
            if ('step_' + str(i) + '_pic') in params:
                step['pic_path'] = json.loads(params['step_' + str(i) + '_pic'])
            step['create_time'] = nowt
            if i == 3:
                step['buyer_commit'] = Decimal(params['buyer_commit'])
            o.add_step_by(i - 1, **step)
        o.status = Const['model.order.status.step3']
        o.task.store.user.notice_set(Const['model.remind.no_money'], True)
        # o.task.store.user.save()
        # 普通好评任务数量加1
        o.tb.user.haoping_order_num += 1
        o.tb.user.save()
    else:
        step = {'pic_path': json.loads(params['step_1_pic']), 'create_time': nowt}
        o.add_step_by(0, **step)
        if o.order_type == Const['model.order.type.collect']:
            step = {'pic_path': json.loads(params['step_2_pic']), 'create_time': nowt}
            o.add_step_by(1, **step)
        o.status = Const['model.order.status.comment']
        # 浏览任务数量加1
        o.tb.user.liulan_order_num += 1
        o.tb.user.save()
    o.update_time = nowt
    o.save()
    return JsonResponse(code=Const['code.success'])


# 图片修改接口
def image_revise(r, mid):
    o = Order.objects.get(pk=mid)
    params = r.REQUEST
    if 'user_id' in params:
        user_id = int(params['user_id'])
    else:
        return JsonResponse(code=Const['code.request_error'])
    if o.tb.user.id == user_id:
        if o.status not in (Const['model.order.status.comment'], Const['model.order.status.step1'],
                            Const['model.order.status.step2'], Const['model.order.status.step3'],
                            Const['model.order.status.step9'],
                            Const['model.order.status.returnmoney'], Const['model.order.status.deliver']):
            return JsonResponse(code=Const['code.request_error'], msg=u'订单已确认')
        logger.info(params)
        nowt = msec_time()
        if 'step' in params:
            num = int(params['step'])
            if ('step_' + str(num + 1) + '_pic') in params:
                step_num = json.loads(params['step_' + str(num + 1) + '_pic'])
                o.image_gb(num, step_num)
            else:
                return JsonResponse(code=Const['code.request_error'])
        else:
            return JsonResponse(code=Const['code.request_error'])
        o.update_time = nowt
        o.save()
        return JsonResponse(code=Const['code.success'], data=o.to_dict(), msg=u'图片修改成功')
    else:
        return JsonResponse(code=Const['code.request_error'], msg=u'非法修改')


def _order_returndeliver(o, sc=None):
    if sc is None:
        sc = o.buyer_principal
    return _general_add_order_step(o, 3, Const['model.order.status.step3'],
                                   Const['model.order.status.returnmoney'], seller_commit=sc
                                   ) and \
           _general_add_order_step(o, 4, Const['model.order.status.returnmoney'],
                                   Const['model.order.status.deliver'])


# 12小时平台自动返款逻辑
def order_auto_returndeliver(order):
    seller = order.task.store.user
    buyer = order.tb.user
    sell = order.get_seller_commit()
    buyer_commit = Decimal(order.get_buyer_commit())
    if sell == None:
        seller_commit = order.buyer_principal
    else:
        seller_commit = Decimal(sell)
    if buyer_commit <= seller_commit:
        difference = seller_commit - buyer_commit
        buyer.money_operate(Const['model.record.pricipal'],
                            buyer_commit, '订单本金归还，订单编号：%d' % order.id,
                            Const['model.record.category.principalreturn'])
        seller.money_operate(Const['model.record.pricipal'],
                             difference, '订单剩余本金归还，订单编号：%d' % order.id,
                             Const['model.record.category.principalreturn'])
        buyer.notice_set(Const['model.remind.evaluated'], True)  # 待评价通知标志位
        # buyer.save()
        return JsonResponse(code=Const['code.success'])
    else:
        buyer.money_operate(Const['model.record.pricipal'],
                            seller_commit, '订单本金归还，订单编号：%d' % order.id,
                            Const['model.record.category.principalreturn'])
        order.flag_set(2, True)
        buyer.notice_set(Const['model.remind.evaluated'], True)  # 待评价通知标志位
        # buyer.save()
        order.flag_set(Const['model.remind.idc_verify'], True)  # 问题订单标志位
        order.difference = buyer_commit - seller_commit
        print order.difference
        order.save()
        return JsonResponse(code=Const['code.success'])


@rest_permission
@transaction.atomic
def order_returndeliver(r, mid):
    o = Order.objects.get(pk=mid)
    if o.frozen:
        return JsonResponse(code=Const['code.order.frozen'], msg=u'订单已冻结无法操作')
    logger.info(r.REQUEST)
    if o.task.return_type == Const['model.task.return_type.platform']:
        if _order_returndeliver(o, Decimal(r.REQUEST['seller_commit'])):
            code = _rebate_judge(o, Decimal(r.REQUEST['seller_commit']))
            if code == Const['code.success']:
                o.save()
                return JsonResponse(code=Const['code.success'])
            elif code == Const['code.amount.exceed']:
                return JsonResponse(code=Const['code.amount.exceed'])
                #            o.tb.user.money_operate(Const['model.record.pricipal'],
                #                                    o.buyer_principal, '订单本金归还，订单编号：%d' % o.id,
                #                                    Const['model.record.category.principalreturn'])
                #            return JsonResponse(code=Const['code.success'])
        return JsonResponse(code=Const['code.request_error'])
    else:
        if _order_returndeliver(o, Decimal(r.REQUEST['seller_commit'])):
            o.save()
            o.tb.user.notice_set(Const['model.remind.evaluated'], True)
            # o.tb.user.save()
            return JsonResponse(code=Const['code.success'])
        return JsonResponse(code=Const['code.request_error'])


@app_check
@rest_permission
def order_comment(r, mid):
    return _general_order_process(r, mid, 5, Const['model.order.status.deliver'],
                                  Const['model.order.status.comment'])


@transaction.atomic
def _check_task_award(task, seller):
    # 邀请人奖励
    now = msec_time()
    if not task.inviter_awarded and seller.inviter and (now - seller.register_time < Const['ms.per.year']):
        task.inviter_awarded = True
        task.save()
        orders_count = task.order_set.filter(status=Const['model.order.status.completed'],
                                             order_type__in=(Const['model.order.type.normal'],
                                                             Const['model.order.type.keyword'],
                                                             Const['model.order.type.image'])).count()
        if orders_count > 0:
            award = orders_count * task._commision_base() * Const['inviter.seller.award.ratio']
            seller.inviter.money_operate(Const['model.record.commission'], award,
                                         '商家推广奖励，商家id：%d' % seller.id,
                                         Const['model.record.category.promote'])
            seller.inviter.promote_award = seller.inviter.promote_award + award
            seller.inviter.save(update_fields=['promote_award'])


@rest_permission
@transaction.atomic
def order_affirm(r, mid):
    o = Order.objects.get(pk=mid)
    if o.frozen:
        return JsonResponse(code=Const['code.order.frozen'])
    if _general_add_order_step(o, 6, Const['model.order.status.comment'], Const['model.order.status.completed']):
        o.save()
        logger.info("订单为：876")
        buyer = o.tb.user
        logger.info("买手：978")
        ##邀请人奖励
        if o.is_buy_order() and buyer.inviter:
            logger.info("进入if o.is_buy_order() and buyer.inviter:")
            hasAward = False
            if buyer.buyer_invitee_award:
                logger.info("buyer.buyer_invitee_award:")
                hasAward = True
                buyer.buyer_invitee_award = False
                buyer.inviter.money_operate(Const['model.record.commission'],
                                            Const['inviter.buyer.award'], '买手推广奖励，买手id：%d' % buyer.id,
                                            Const['model.record.category.promote'])
                buyer.inviter.promote_award = buyer.inviter.promote_award + Const['inviter.buyer.award']
                logger.info(" buyer.inviter.promote_award991")
            now = msec_time()
            if (now - buyer.register_time) < (0.5 * Const['ms.per.year']):
                hasAward = True
                award = o.buyer_gain * Const['inviter.buyer.award.ratio']
                buyer.inviter.money_operate(Const['model.record.commission'],
                                            award, '买手推广奖励，买手id：%d' % buyer.id,
                                            Const['model.record.category.promote'])
                buyer.inviter.promote_award = buyer.inviter.promote_award + award
                logger.info("买手推广奖励1000")
            if hasAward:
                buyer.inviter.save()
            logger.info("最终的hasAward1003")
            # 如果是有邀请人的， 完成第一单垫资任务后， 奖励5元  2016.03.08注册的时候已经奖励过了，不需要验证
            # if not buyer.join_award:
            #     buyer.money_operate(Const['model.record.commission'],
            #                         Const['common.join.award'], '注册奖励',
            #                         Const['model.record.category.join'])
            #     buyer.join_award = True
        ## 买手佣金
        buyer.money_operate(Const['model.record.commission'], o.buyer_gain, '订单佣金收入，订单编号：' + str(o.id))
        # buyer.commission = buyer.commission + o.buyer_gain
        buyer.today_commission = buyer.today_commission + o.buyer_gain
        if o.is_buy_order():
            buyer.buyer_orders = buyer.buyer_orders + 1
            buyer.set_user_level('b')
            # buyer.notice_set(Const['model.remind.buyer_orders'], True)
        buyer.save()
        logger.info("最终买手1020")
        # Record.objects.create(id=Record.objects.avaliable_id(),
        #                      user=buyer, amount=o.buyer_gain, balance=buyer.commission,
        #                      type=Const['model.record.commission'],
        #                      description=('订单佣金收入，订单编号：' + str(o.id)), )
        if o.task.order_set.exclude(status__in=(Const['model.order.status.cancel'], \
                                                Const['model.order.status.completed'])).count() == 0:
            o.task.status = Const['model.task.status.closed']
            _check_task_award(o.task, o.task.store.user)
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@transaction.atomic
def _order_affirm(mid):
    o = Order.objects.get(pk=mid)
    if _general_add_order_step(o, 6, Const['model.order.status.comment'], Const['model.order.status.completed']):
        o.save()
        buyer = o.tb.user
        ##邀请人奖励
        if o.is_buy_order() and buyer.inviter:
            hasAward = False
            if buyer.buyer_invitee_award:
                hasAward = True
                buyer.buyer_invitee_award = False
                buyer.inviter.money_operate(Const['model.record.commission'],
                                            Const['inviter.buyer.award'], '买手推广奖励，买手id：%d' % buyer.id,
                                            Const['model.record.category.promote'])
                buyer.inviter.promote_award = buyer.inviter.promote_award + Const['inviter.buyer.award']
            now = msec_time()
            if (now - buyer.register_time) < (0.5 * Const['ms.per.year']):
                hasAward = True
                award = o.buyer_gain * Const['inviter.buyer.award.ratio']
                buyer.inviter.money_operate(Const['model.record.commission'],
                                            award, '买手推广奖励，买手id：%d' % buyer.id,
                                            Const['model.record.category.promote'])
                buyer.inviter.promote_award = buyer.inviter.promote_award + award
            if hasAward:
                buyer.inviter.save()

            # 如果是有邀请人的， 完成第一单垫资任务后， 奖励5元
            if not buyer.join_award:
                buyer.money_operate(Const['model.record.commission'],
                                    Const['common.join.award'], '注册奖励',
                                    Const['model.record.category.join'])
                buyer.join_award = True
        ##买手佣金
        buyer.money_operate(Const['model.record.commission'], o.buyer_gain, '订单佣金收入，订单编号：' + str(o.id))
        # buyer.commission = buyer.commission + o.buyer_gain
        buyer.today_commission = buyer.today_commission + o.buyer_gain
        if o.is_buy_order():
            buyer.buyer_orders = buyer.buyer_orders + 1
            buyer.set_user_level('b')
        buyer.save()
        # Record.objects.create(id=Record.objects.avaliable_id(),
        #                      user=buyer, amount=o.buyer_gain, balance=buyer.commission,
        #                      type=Const['model.record.commission'],
        #                      description=('订单佣金收入，订单编号：' + str(o.id)), )
        if o.task.order_set.exclude(status__in=(Const['model.order.status.cancel'], \
                                                Const['model.order.status.completed'])).count() == 0:
            o.task.status = Const['model.task.status.closed']
            _check_task_award(o.task, o.task.store.user)
        return True
    else:
        return False


@rest_permission
@transaction.atomic
def task_cancel(r, mid):
    task = Task.objects.get(pk=mid)
    if task.status == Const['model.task.status.in_progress']:
        ##退还所有未接订单的钱
        remain_orders = task.order_set.filter(status=Const['model.order.status.init']).all()
        if not remain_orders:
            return JsonResponse(code=Const['code.request_error'])
        remain_money = reduce(lambda a, b: a + b, [o.seller_payment for o in remain_orders])
        user = task.store.user
        user.money_operatesafe(Const['model.record.pricipal'],
                               remain_money,
                               '任务撤销本金返还，任务编号：' + str(task.id))
        # user.principal = user.principal + remain_money
        # user.save()
        remain_orders.update(status=Const['model.order.status.cancel'])
        # Record.objects.create(id=Record.objects.avaliable_id(),
        #                      user=user, amount=remain_money, balance=user.principal,
        #                      type=Const['model.record.pricipal'],
        #                      description=('任务撤销本金返还，任务编号：' + str(task.id)), )
        # 取消订单的时候用户等级变化。
        remain_amount = 0
        # for o in remain_orders:
        #     remain_amount = remain_amount + 1;
        # user.seller_orders = user.seller_orders - remain_amount
        # user.set_user_level('s')
        # user.save()

    task.status = Const['model.task.status.cancel']
    if task.order_set.exclude(status__in=(Const['model.order.status.cancel'], \
                                          Const['model.order.status.completed'])).count() == 0:
        _check_task_award(task, task.store.user)
    task.save()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def task_getremainbuyerorder(r, mid):
    task = Task.objects.get(pk=mid)
    orders = task.order_set.filter(status=Const['model.order.status.init'],
                                   order_type__in=[Const['model.order.type.normal'],
                                                   Const['model.order.type.keyword'],
                                                   Const['model.order.type.image']]).count()
    return JsonResponse(code=Const['code.success'], data={'orders': orders})


@rest_permission
@transaction.atomic
def task_speed(r, mid):
    task = Task.objects.get(pk=mid)
    if not task.status == Const['model.task.status.in_progress']:
        return JsonResponse(code=Const['code.request_error'])
    remain_orders = task.order_set.filter(status=Const['model.order.status.init'],
                                          order_type__in=[Const['model.order.type.normal'],
                                                          Const['model.order.type.keyword'],
                                                          Const['model.order.type.image']])
    if not remain_orders:
        return JsonResponse(code=Const['code.request_error'])
    extra_bonus = Decimal(r.REQUEST['extra_bonus'])
    if extra_bonus < 0:
        return JsonResponse(code=Const['code.request_error'])
    extra_payment = len(remain_orders) * extra_bonus
    seller = task.store.user

    # if seller.principal < extra_payment:
    #    return Const['code.insufficient.balance']
    ret = seller.money_operatesafe(Const['model.record.pricipal'],
                                   -extra_payment,
                                   '任务加速，任务编号：%d' % task.id,
                                   Const['model.record.category.taskpay'])
    if ret < 0:
        return Const['code.insufficient.balance']
    remain_orders.update(seller_payment=F('seller_payment') + extra_bonus)
    task.bonus = task.bonus + extra_bonus
    task.save()
    return JsonResponse(code=Const['code.success'])


def appealtype_list(r):
    if 'type' in r.REQUEST:
        if r.REQUEST['type'] == '-1':
            aptypes = AppealType.objects.all()
        else:
            aptypes = AppealType.objects.filter(type=r.REQUEST['type'])
    else:
        aptypes = AppealType.objects.filter(type=Const['model.notice.type.buyer'])
    return JsonResponse(code=Const['code.success'], data=[x.to_dict() for x in aptypes])


@admin_permission('normal')
def appealtype_create(r):
    AppealType.objects.create(description=r.REQUEST['description'])
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def appealtype_delete(r, aid):
    AppealType.objects.filter(pk=aid).delete()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def order_applyappeal(r, oid):
    if Appeal.objects.filter(order_id=oid).count() > 0:
        return JsonResponse(code=Const['code.request_error'], msg=u'此订单已有申诉')
    user = User.objects.get_user_from_session(r)
    order = Order.objects.get(pk=oid)
    order.frozen = True
    order.save(update_fields=['frozen'])
    params = r.REQUEST
    id = fix_length_random_int(9)
    logger.info(params)
    complainant_id = user.id
    if complainant_id == order.tb.user_id:
        respondent_id = order.task.store.user_id
        order.task.store.user.notice_set(Const['model.remind.appeal'], True)  # 申诉通知
    else:
        respondent_id = order.tb.user_id
        order.tb.user.notice_set(Const['model.remind.appeal'], True)
    pic_path = []
    for i in range(3):
        pkey = 'pic' + str(i)
        if pkey in params:
            pic_path.append(params[pkey])
    pic_path = json.dumps(pic_path)
    appeal = Appeal(id, order=order, complainant_id=complainant_id,
                    respondent_id=respondent_id,
                    appealtype_id=params['appealtype_id'], pic_path=pic_path)
    if 'description' in params:
        appeal.add_general_progress(Const['model.appeal.progress.source.complainant'], params['description'])
    appeal.save()
    if int(params['appealtype_id']) == 2:  # 商品问题
        appeal.order.task.appealnum = appeal.order.task.appealnum + 1
        appeal.order.task.save(update_fields=['appealnum'])
    if appeal.order.task.appealnum >= 5 and appeal.order.task.status == Const['model.task.status.in_progress']:
        appeal.order.task.status = Const['model.task.status.frozen']
        appeal.order.task.save(update_fields=['status'])
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def thaw_task(r, task_id):
    task = Task.objects.get(pk=task_id)
    task.status = Const['model.task.status.in_progress']
    task.save(update_fields=['status'])
    return JsonResponse(code=Const['code.success'])


@app_check
@transaction.atomic
@rest_permission
def order_cancel(r, oid):
    user = User.objects.get_user_from_session(r)
    order = Order.objects.get(pk=oid)
    if order.frozen:
        return JsonResponse(code=Const['code.order.frozen'], msg=u'订单已冻结无法操作')
    if user.id == order.tb.user_id:
        if order.status in (Const['model.order.status.received'],
                            Const['model.order.status.step1'],
                            Const['model.order.status.step2'],):
            nowt = msec_time()
            if order.task.prepublish:
                return JsonResponse(code=Const['code.order.uncancelable'], msg=u'当前订单不可取消')
            if (nowt - order.receive_time) > (Const['ms.per.minute'] * 20):
                user.money_operate(Const['model.record.commission'],
                                   Decimal(-1) if order.is_buy_order() else Decimal(-0.01), '取消订单惩罚，订单：%d' % order.id)
            if order.is_buy_order():
                StoreRecentBuyer.objects.filter(tb_id=order.tb_id, store_id=order.task.store_id,
                                                type=order.order_type).delete()
                order.tb.today_receive_orders -= 1
                order.tb.save()
            else:
                StoreRecentBuyer.objects.filter(tb_id=order.tb_id, store_id=order.task.store_id,
                                                type=order.order_type).delete()
            StoreRecentBuyerUser.objects.filter(user_id=user.id, store_id=order.task.store_id,
                                                type=order.order_type).delete()
            order.status = Const['model.order.status.init']
            order.tb = None
            order.receive_time = None
            order.step_detail = '{}'
            order.save()
            logger.debug("response success")
            return JsonResponse(code=Const['code.success'])
    else:
        if order.status == Const['model.order.status.init']:
            order.status = Const['model.order.status.cancel']
            order.save()
            user.money_operate(Const['model.record.pricipal'], Decimal(order.seller_payment),
                               '取消订单本金返还，订单：%d' % order.id)
            return JsonResponse(code=Const['code.success'])
    return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
def order_forcecancel(r, oid):
    order = Order.objects.get(pk=oid)
    code = _order_forcecancel(order)
    if code == Const['code.success']:
        return JsonResponse(code=Const['code.success'])
    elif code == Const['code.amount.exceed']:
        return JsonResponse(code=Const['code.amount.exceed'])
    else:
        return JsonResponse(code=Const['code.order.unsupportaction'])


def _order_forcecancel(order):
    if order.is_buy_order():
        logger.info(order.status)
        if order.status in (
                Const['model.order.status.received'],
                Const['model.order.status.step1'],
                Const['model.order.status.step2'],
                Const['model.order.status.step3'],
                Const['model.order.status.step9'],
                Const['model.order.status.step10'],
                Const['model.order.status.init'],
                Const['model.order.status.deliver'],
                Const['model.order.status.comment']):
            if order.status in (
                    Const['model.order.status.deliver'],
                    Const['model.order.status.comment']) \
                    and order.task.return_type == Const['model.task.return_type.platform']:
                seller_commit = Decimal(order.get_step4_seller_commit())
                buyer_commit = Decimal(order.get_buyer_commit())
                commission = order.seller_payment - order.buyer_principal
                logger.info(seller_commit)
                ret = order.tb.user.money_operatesafe(Const['model.record.pricipal'], -buyer_commit,
                                                      '强制撤销本金扣款，订单编号：%d' % order.id)
                if ret < 0:
                    return Const['code.amount.exceed']
                else:
                    order.status = Const['model.order.status.cancel']
                    order.save(update_fields=['status'])
                    order.task.store.user.money_operate(Const['model.record.pricipal'], seller_commit + commission,
                                                        '强制撤销订单本金佣金返还，订单编号：%d' % order.id)
                    return Const['code.success']
            else:
                order.status = Const['model.order.status.cancel']
                order.save(update_fields=['status'])
                order.task.store.user.money_operate(Const['model.record.pricipal'], Decimal(order.seller_payment),
                                                    '强制取消订单本金返还，订单编号：%d' % order.id)
                return Const['code.success']
        return Const['code.order.unsupportaction']
    else:
        if order.status in (
                Const['model.order.status.init'],
                Const['model.order.status.received'],
                Const['model.order.status.comment']):
            order.status = Const['model.order.status.cancel']
            order.save(update_fields=['status'])
            order.task.store.user.money_operate(Const['model.record.pricipal'], Decimal(order.seller_payment),
                                                '强制取消订单本金返还，订单编号：%d' % order.id)
            return Const['code.success']
        return Const['code.order.unsupportaction']


@mutex_lock
@rest_permission
def appeal_reply(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.status != Const['model.appeal.status.in_progress']:
        return JsonResponse(code=Const['code.request_error'])
    source = appeal.which(int(r.session['user_id']) if 'user_id' in r.session else -1)
    params = r.REQUEST
    #    pic_path = json.loads(appeal.pic_path)
    #    for i in range(3):
    #        pkey = 'pic' + str(i)
    #        if pkey in params:
    #            pic_path.append(params[pkey])
    #    appeal.pic_path = json.dumps(pic_path)
    appeal.add_general_progress(source, params['content'])
    appeal.save()
    return JsonResponse(code=Const['code.success'])


# @admin_permission('normal')
# def platform_reply(r, aid):
#    appeal = Appeal.objects.get(pk=aid)
#    if not appeal.platform_involve:
#        return  JsonResponse(code=Const['code.request_error'])
#    if appeal.status != Const['model.appeal.status.in_progress']:
#        return JsonResponse(code=Const['code.request_error'])
#    source = Const['model.appeal.progress.soure.platform']
#    appeal.add_general_progress(source, r.REQUEST['content'])
#    appeal.save()
#    return JsonResponse(code=Const['code.success'])


# @admin_permission('normal')
# def frozen_order(r, order_id):
#    order = Order.objects.get(pk=order_id)
#    if order.status in (Const['model.order.status.init'], Const['model.order.status.cancel']):
#        return JsonResponse(code=Const['code.system_error'])
#    order.frozen = True
#    order.save(update_fields=['frozen'])
#    return JsonResponse(code=Const['code.success'])

# @admin_permission('normal')
# def thaw_order(r, order_id):
#    order = Order.objects.get(pk=order_id)
#    order.frozen = False
#    order.save(update_fields=['frozen'])
#    return JsonResponse(code=Const['code.success'])


# @rest_permission
def appeal_get(r, aid):
    return JsonResponse(code=Const['code.success'], data=Appeal.objects.get(pk=aid).to_dict())


@admin_permission('normal')
def cancel_handle(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.order.status == Const['model.order.status.cancel']:
        return JsonResponse(code=Const['code.system_error'])
    if not appeal.forced:
        return JsonResponse(code=Const['code.request_error'])

    code = _order_forcecancel(appeal.order)
    if code == Const['code.success']:
        appeal.status = Const['model.appeal.status.closed']
        appeal.forced = False
        appeal.add_general_progress(Const['model.appeal.progress.source.platform'], \
                                    u'平台已强制撤销当前订单任务，返还商家发布任务支付的本金、佣金，买手不罚款，申诉完结！')
        appeal.save()
        return JsonResponse(code=Const['code.success'])
    elif code == Const['code.amount.exceed']:
        return JsonResponse(code=Const['code.amount.exceed'])
    else:
        return JsonResponse(code=Const['code.order.unsupportaction'])


# 申诉中撤销订单的接口
@need_login
def appeal_order(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.status == Const['model.appeal.status.closed']:
        return JsonResponse(code=Const['code.request_error'], msg=u'申诉已完成')
    params = r.REQUEST
    logger.info(params)

    id = int(params['user_id']) if 'user_id' in params else None
    if id == None:
        user = User.objects.get_user_from_session(r)
        id = user.id

    if 'agree' in params and params['agree'] == 'true':  # 同意请求
        if appeal.order_cancel:
            order = appeal.order
            if order.status in (Const['model.order.status.init'], Const['model.order.status.cancel']):
                return JsonResponse(code=Const['code.system_error'])
            appeal.forced = _cancel_order(order)  # forced 表示需不需要由后台强制撤销订单
            appeal.save(update_fields=['forced'])
            if appeal.forced:
                appeal.platform_involve == True
                appeal.launch = 0
                appeal.add_general_progress(Const['model.appeal.progress.source.platform'], \
                                            u'%s 同意撤销订单，由于当前订单已返款，平台已经介入，请等待平台处理' % id)
                appeal.save()
                return JsonResponse(code=Const['code.success'], msg=u'同意撤销订单，等待平台处理。')
            else:
                appeal.status = Const['model.appeal.status.closed']
                appeal.add_general_progress(Const['model.appeal.progress.source.platform'], u'%s 同意撤销当前订单' % id)
                appeal.save()
                return JsonResponse(code=Const['code.success'], msg=u'撤销订单成功')
        else:
            return JsonResponse(code=Const['code.request_error'])

    if 'cancel' in params and params['cancel'] == 'true':  # 撤销订单请求
        if appeal.order.status == Const['model.order.status.completed']:
            return JsonResponse(code=Const['code.request_error'], msg=u'订单已完成')
        appeal.order_cancel = True
        appeal.launch = id
        appeal.add_general_progress(Const['model.appeal.progress.source.platform'], u'%s 申请撤销当前订单' % id)
        appeal.save()
        return JsonResponse(code=Const['code.success'], msg=u'申请撤销订单等待对方确认')


def _cancel_order(o):
    if o.status == Const['model.order.status.received']:
        o.status = Const['model.order.status.cancel']
        o.save(update_fields=['status'])
        o.task.store.user.money_operate(Const['model.record.pricipal'], Decimal(o.seller_payment),
                                        '经申诉协商后撤销订单本金佣金返还，订单编号：%d' % o.id)
        return False
    elif o.status == Const['model.order.status.step3']:
        o.status = Const['model.order.status.cancel']
        o.save(update_fields=['status'])
        o.task.store.user.money_operate(Const['model.record.pricipal'], Decimal(o.seller_payment),
                                        '经申诉协商后撤销订单本金佣金返还，订单编号：%d' % o.id)
        return False
    elif o.status == Const['model.order.status.comment']:
        if o.is_buy_order():
            return True
        else:
            o.status = Const['model.order.status.cancel']
            o.save(update_fields=['status'])
            o.task.store.user.money_operate(Const['model.record.commission'], Decimal(o.seller_payment),
                                            '经申诉协商后撤销订单佣金返还，订单编号：%d' % o.id)
            return False
    else:
        return True


# 平台完结申述接口
@admin_permission('normal')
def platform_finish(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.status == Const['model.appeal.status.closed']:
        return JsonResponse(code=Const['code.request_error'], msg=u'申诉已完结')
    appeal.status = Const['model.appeal.status.closed']
    appeal.save(update_fields=['status'])
    appeal.order.frozen = False
    appeal.order.save(update_fields=['frozen'])
    return JsonResponse(code=Const['code.success'])


# 完结申诉
@need_login
def appeal_finish(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.status == Const['model.appeal.status.closed']:
        return JsonResponse(code=Const['code.request_error'], msg=u'申诉已完结')
    if appeal.order_cancel:
        return JsonResponse(code=Const['code.request_error'], msg=u'撤销订单的事务没有完成，不能完结申诉')
    params = r.REQUEST

    id = int(params['user_id']) if 'user_id' in params else None
    if id == None:
        user = User.objects.get_user_from_session(r)
        id = user.id

    if 'agree' in params and params['agree'] == 'true':  # 同意请求
        if appeal.finish:
            appeal.status = Const['model.appeal.status.closed']
            appeal.add_general_progress(Const['model.appeal.progress.source.platform'], u'%s 同意完结申诉！' % id)
            appeal.save()
            appeal.order.frozen = False
            appeal.order.save(update_fields=['frozen'])
            return JsonResponse(code=Const['code.success'], msg=u'申诉完结')
        else:
            return JsonResponse(code=Const['code.request_error'])

    if id == appeal.complainant_id:
        appeal.status = Const['model.appeal.status.closed']
        appeal.add_general_progress(Const['model.appeal.progress.source.platform'], u'%s 已经确认申诉完结！' % id)
        appeal.save()
        appeal.order.frozen = False
        appeal.order.save(update_fields=['frozen'])
        return JsonResponse(code=Const['code.success'], msg=u'申请完结申诉成功')
    elif id == appeal.respondent_id:
        appeal.finish = True
        appeal.add_general_progress(Const['model.appeal.progress.source.platform'], u'%s 申请完结申诉！' % id)
        appeal.save()
        return JsonResponse(code=Const['code.success'], msg=u'申请完结等待对方确认')


# @rest_permission
# def appeal_platinvolve(r, aid):
#    appeal = Appeal.objects.get(pk=aid)
#    appeal.platform_involve = True
#    appeal.save()
#    return JsonResponse(code=Const['code.success'])

@rest_permission
def appeal_platinvolve(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    if appeal.status == Const['model.appeal.status.closed']:
        return JsonResponse(code=Const['code.request_error'], msg=u'申诉已完结')
    if appeal.platform_involve == True:
        return JsonResponse(code=Const['code.success'], msg=u'平台已介入请耐心等待')
    now = msec_time()
    interval = now - appeal.create_time
    if interval >= 6 * Const['ms.per.hour']:
        appeal.platform_involve = True
        appeal.save(update_fields=['platform_involve'])
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'], msg=u'请在发起申诉后的 6 小时后申请平台介入')


# @rest_permission
# def appeal_finish(r, aid):
#    appeal = Appeal.objects.get(pk=aid)
#    if appeal.status == Const['model.appeal.status.in_progress']:
#        appeal.status = Const['model.appeal.status.closed']
#        appeal.save()
#        return JsonResponse(code=Const['code.success'])
#    return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
def store_list(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, user_id='user_id', verify_status='verify_status')
    if 'register_start_time' in r.REQUEST:
        condition['user__register_time__gte'] = get_stamp_by_date(r.REQUEST['register_start_time'])
    stores = Store.objects.filter(**condition)[start:start + num]
    total = Store.objects.filter(**condition).count()
    data = []
    for s in stores:
        d = s.to_dict()
        d['register_time'] = s.user.register_time
        data.append(d)
    return JsonResponse(code='code.success', data={'total': total,
                                                   'stores': data})


@admin_permission('normal')
@mutex_lock
def store_verify(r, sid):
    store = Store.objects.get(pk=sid)
    if obj_verify(r, store, istm=bool(int(r.REQUEST['istm']))):
        store.user.notice_set(Const['model.remind.tb_verify'], True)  # 店铺验证状态
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
def task_list(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    conditions = make_conditions(r, store__user_id='seller_id', pk='task_id', store__name='store_name')
    if 'publish_start_date' in params:
        conditions['create_time__gte'] = get_stamp_by_date(params['publish_start_date'])
    if 'publish_end_date' in params:
        conditions['create_time__lte'] = get_stamp_by_date(params['publish_end_date'])
    if 'task_type' in params:
        if params['task_type'] == '1':
            conditions['task_type'] = Const['model.task.type.mobile_taobao']
        if params['task_type'] == '2':
            conditions['task_type'] = Const['model.task.type.pc_taobao']
        if params['task_type'] == '3':
            conditions['task_type'] = Const['model.task.type.flow']
        if params['task_type'] == '4':
            conditions['task_type'] = Const['model.task.type.special']

    total = Task.objects.filter(**conditions).count()
    tasks = Task.objects.filter(**conditions)[start:start + num]
    data = []
    for t in tasks:
        d = {}
        commodities = json.loads(t.commodities)
        try:
            search_entries = json.loads(t.search_entries)
        except Exception:
            search_entries = None
        orders = t.order_set.all()
        d['total_order'] = len(orders)
        d['store_name'] = t.store.name
        d['id'] = t.id
        d['status'] = t.status
        d['create_time'] = t.create_time
        # d['task_type'] = 2 if t.task_type == Const['model.task.type.pc_taobao'] else t.task_type
        d['task_type'] = t.task_type
        d['commodity_name'] = commodities[0]['name']
        d['commodity_image'] = commodities[0]['pic_path']
        d['search_keyword'] = search_entries[0]['keyword'] if search_entries else None
        d['order_1'] = d['order_2'] = d['order_3'] = d['order_4'] = d['order_5'] = d['order_6'] = 0
        for o in orders:
            if o.status == Const['model.order.status.init']:
                d['order_1'] = d['order_1'] + 1;
            elif o.status == Const['model.order.status.step3'] or o.status == Const['model.order.status.returnmoney']:
                d['order_3'] = d['order_3'] + 1;
            elif o.status == Const['model.order.status.deliver']:
                d['order_4'] = d['order_4'] + 1;
            elif o.status == Const['model.order.status.comment']:
                d['order_5'] = d['order_5'] + 1;
            elif o.status == Const['model.order.status.completed']:
                d['order_6'] = d['order_6'] + 1;
            elif o.status in (Const['model.order.status.received'],
                              Const['model.order.status.step1'],
                              Const['model.order.status.step2'],
                              Const['model.order.status.step9']):
                d['order_2'] = d['order_2'] + 1;
        data.append(d)
    return JsonResponse(code=Const['code.success'], data={'total': total,
                                                          'tasks': data})


@rest_permission
def task_get(r, tid):
    return JsonResponse(code=Const['code.success'], data=Task.objects.get(pk=tid).to_dict())


# @admin_permission('normal')
def order_listv2(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    conditions = make_conditions(r, task__store__user_id='seller_id', pk='order_id', task__store__name='store_name',
                                 tb__wangwang='buyer_wangwang', task_id='task_id')
    if 'publish_start_date' in params:
        conditions['task__create_time__gte'] = get_stamp_by_date(params['publish_start_date'])
    if 'publish_end_date' in params:
        conditions['task__create_time__lte'] = get_stamp_by_date(params['publish_end_date'])
    if 'task_type' in params:
        if params['task_type'] == '1':
            conditions['task__task_type__in'] = [Const['model.task.type.mobile_taobao'],
                                                 Const['model.task.type.flow'],
                                                 Const['model.task.type.special'], ]
        if params['task_type'] == '2':
            conditions['task__task_type'] = Const['model.task.type.pc_taobao']
    if 'order_status' in params:
        if params['order_status'] == '1':
            conditions['status'] = Const['model.order.status.init']
        elif params['order_status'] == '2':
            conditions['status__in'] = [Const['model.order.status.received'],
                                        Const['model.order.status.step1'],
                                        Const['model.order.status.step2'],
                                        Const['model.order.status.step9']]
        elif params['order_status'] == '3':
            conditions['status__in'] = [Const['model.order.status.returnmoney'],
                                        Const['model.order.status.step3']]
        elif params['order_status'] == '4':
            conditions['status'] = Const['model.order.status.deliver']
        elif params['order_status'] == '5':
            conditions['status'] = Const['model.order.status.comment']
        elif params['order_status'] == '6':
            conditions['status'] = Const['model.order.status.completed']
    total = Order.objects.filter(**conditions).count()
    orders = Order.objects.filter(**conditions)[start:start + num]
    data = []
    for o in orders:
        d = {}
        d['order_id'] = o.id
        d['store_name'] = o.task.store.name
        d['store_id'] = o.task.store.id
        d['seller_id'] = o.task.store.user_id
        d['buyer_wangwang'] = o.tb.wangwang if o.tb else None
        d['buyer_id'] = o.tb.user_id if o.tb else None
        d['task_id'] = o.task_id
        d['receive_time'] = o.receive_time
        d['order_type'] = 2 if o.task.task_type == Const['model.task.type.pc_taobao'] else 1
        d['order_status'] = o.status
        data.append(d)
    return JsonResponse(code=Const['code.success'], data={'total': total,
                                                          'orders': data})


# @admin_permission('normal')
def order_list(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    conditions = make_conditions(r, task__store__user_id='seller_id', pk='order_id', task__store__name='store_name',
                                 tb__wangwang='buyer_wangwang', task_id='task_id', tb__user_id='user_id')
    if 'publish_start_date' in params:
        conditions['task__create_time__gte'] = get_stamp_by_date(params['publish_start_date'])
    if 'publish_end_date' in params:
        conditions['task__create_time__lte'] = get_stamp_by_date(params['publish_end_date'])
    if 'task_type' in params:
        if params['task_type'] == '1':
            conditions['task__task_type__in'] = [Const['model.task.type.mobile_taobao'],
                                                 Const['model.task.type.flow'],
                                                 Const['model.task.type.special'], ]
        if params['task_type'] == '2':
            conditions['task__task_type'] = Const['model.task.type.pc_taobao']
    if 'order_status' in params:
        if params['order_status'] == '1':
            conditions['status'] = Const['model.order.status.init']
        elif params['order_status'] == '2':
            conditions['status__in'] = [Const['model.order.status.received'],
                                        Const['model.order.status.step1'],
                                        Const['model.order.status.step2'],
                                        Const['model.order.status.step9'],
                                        Const['model.order.status.step10']]
        elif params['order_status'] == '3':
            conditions['status__in'] = [Const['model.order.status.returnmoney'],
                                        Const['model.order.status.step3']]
        elif params['order_status'] == '4':
            conditions['status'] = Const['model.order.status.deliver']
        elif params['order_status'] == '5':
            conditions['status'] = Const['model.order.status.comment']
        elif params['order_status'] == '6':
            conditions['status'] = Const['model.order.status.completed']
    if 'format' in params and params['format'] == 'csv':
        csv_output = True
    else:
        csv_output = False
    total = Order.objects.filter(**conditions).count()
    orders = Order.objects.filter(**conditions)[start:start + num]
    data = []
    for o in orders:
        d = {}
        d['return_type'] = o.task.return_type
        d['order_id'] = o.id
        d['store_name'] = o.task.store.name
        d['store_id'] = o.task.store.id
        d['seller_id'] = o.task.store.user_id
        d['buyer_wangwang'] = o.tb.wangwang if o.tb else None
        d['buyer_id'] = o.tb.user_id if o.tb else None
        d['task_id'] = o.task_id
        d['receive_time'] = get_datetime_by_stamp(o.receive_time) if csv_output else o.receive_time
        # d['order_type'] = ('电脑单' if csv_output else 2) if o.task.task_type == Const['model.task.type.pc_taobao'] else (
        #     '手机单' if csv_output else 1)
        d['order_type'] = o.order_type
        if o.status == Const['model.order.status.init']:
            d['order_status'] = '未接单' if csv_output else 1
        elif o.status == Const['model.order.status.step3'] or o.status == Const['model.order.status.returnmoney']:
            d['order_status'] = '待返款发货' if csv_output else 3
        elif o.status == Const['model.order.status.deliver']:
            d['order_status'] = '待评价' if csv_output else 4
        elif o.status == Const['model.order.status.comment']:
            d['order_status'] = '待确认' if csv_output else 5
        elif o.status == Const['model.order.status.completed']:
            d['order_status'] = '已完成' if csv_output else 6
        elif o.status in (Const['model.order.status.received'],
                          Const['model.order.status.step1'],
                          Const['model.order.status.step2'],
                          Const['model.order.status.step9'],
                          Const['model.order.status.step10']):
            d['order_status'] = '待操作' if csv_output else 2
        data.append(d)
    if csv_output:
        return CsvResponse({
            'store_name': u'店铺名',
            'store_id': u'店铺ID',
            'seller_id': u'商家ID',
            'buyer_wangwang': u'买手旺旺',
            'task_id': u'任务ID',
            'receive_time': u'接单时间',
            'order_type': u'订单类型',
            'order_status': u'订单状态',
        }, data)
    else:
        return JsonResponse(code=Const['code.success'], data={'total': total,
                                                              'orders': data})


# @admin_permission('finance')
# def order_returnlist(r):
#     start,num=get_paginator(r)
#     condition=make_conditions(r,tb__user_id='buyer_id')
#     if 'return_status' in r.REQUEST:
#         if r.REQUEST['return_status'] == '1':
#             condition['step_number']=3
#         elif r.REQUEST['return_status'] == '2':
#             condition['step_number__gt']=3
#     condition['step_number__gte']=3
#     condition['task__return_type']=Const['model.task.return_type.platform']
#     condition['order_type__in']=[Const['model.order.type.normal'],
#                                 Const['model.order.type.keyword'],
#                                 Const['model.order.type.image'],]
#     orders=Order.objects.filter(**condition)[start:start+num]
#     total=Order.objects.filter(**condition).count()
#     data=[]
#     for o in orders:
#         data.append({
#         'buyer_id':o.tb.user_id,
#         'buyer_name':o.tb.user.idc_name,
#         'buyer_phone':o.tb.user.phone,
#         'buyer_qq':o.tb.user.qq,
#         'bank_name':o.bankcard.bank_name if o.bankcard else None,
#         'bank_city':o.bankcard.bank_city if o.bankcard else None,
#         'owner_name':o.bankcard.owner_name if o.bankcard else None,
#         'account_id':o.bankcard.account_id if o.bankcard else None,
#         'account_name':o.bankcard.account_name if o.bankcard else None,
#         'has_return':True if o.step_number>3 else False,
#         'buyer_commit':o.get_buyer_commit(),
#         'seller_payment':o.dianzi(),
#                    })
#     return JsonResponse(code=Const['code.success'],data={
#                 'total':total,'orders':data})

# @admin_permission('finance')
# @mutex_lock
# def order_platreturn(r,oid):
#     o=Order.objects.get(pk=oid)
#     if o.task.return_type==Const['model.task.return_type.platform']:
#         if _order_returndeliver(o,Decimal(r.REQUEST['seller_commit'])):
#             o.save()
#             return JsonResponse(code=Const['code.success'])
#     return JsonResponse(code=Const['code.request_error'])

@admin_permission('normal')
def appeal_list(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    conditions = make_conditions(r, status='status', pk='appeal_id', order_id='order_id',
                                 appealtype_id='appealtype_id', complainant_id='complainant',
                                 respondent_id='respondent_id')
    if 'start_date' in params:
        conditions['create_time__gte'] = get_stamp_by_date(params['start_date'])
    if 'end_date' in params:
        conditions['create_time__lte'] = get_stamp_by_date(params['end_date'])
    if 'platform_involve' in params:
        conditions['platform_involve'] = bool(int(params['platform_involve']))
    total = Appeal.objects.filter(**conditions).count()
    appeals = Appeal.objects.filter(**conditions)[start:start + num]
    data = [a.to_exc_dict('progress', 'avaliable_sources', 'finish', 'order_cancel', 'launch') for a in appeals]
    return JsonResponse(code=Const['code.success'], data={'total': total, 'appeals': data})


@need_login
def task_delete(r, task_id):
    tasks = Task.objects.get(pk=task_id)
    order = Order.objects.filter(task__pk=task_id)
    user_id = tasks.store.user.id
    if user_id == r.session['user_id']:
        if tasks.status == Const['model.task.status.need_payment']:
            tasks.delete()
            return JsonResponse(code=Const['code.success'])
        elif tasks.status == Const['model.task.status.cancel']:
            i = 0
            for o in order:
                if o.status != Const['model.order.status.init'] and o.status != Const['model.order.status.cancel']:
                    i = i + 1
            if i == 0:
                tasks.delete()
                return JsonResponse(code=Const['code.success'])
            else:
                return JsonResponse(code=Const['code.notdelete.data'], msg=u'订单状态不允需删除')
        elif tasks.verify_status == Const['model.verify.check_deny']:
            tasks.delete()
            return JsonResponse(code=Const['code.success'])
        else:
            return JsonResponse(code=Const['code.notdelete.data'], msg=u'任务状态不允许删除')
    else:
        return JsonResponse(code=Const['code.permission_deny'])


@need_login
@userid_check
def order_delete(r, order_id):
    order = Order.objects.get(pk=order_id)
    if order.status in Const['model.order.status.cancel']:
        order.delete()
    else:
        return JsonResponse(code=Const['code.notdelete.data'], msg=u'订单状态不允需删除')


def task_test(r):
    Task.objects.get(pk=2534515).delete()


# @rest_permission
def _rebate_judge(order, seller_commit):
    buyer_principal = Decimal(order.buyer_principal)
    if seller_commit < buyer_principal:
        order.task.store.user.money_operatesafe(Const['model.record.pricipal'], \
                                                buyer_principal - seller_commit, '订单剩余本金归还，订单编号：%d' % order.id)
        order.tb.user.money_operatesafe(Const['model.record.pricipal'], seller_commit, \
                                        '订单本金归还，订单编号：%d' % order.id)
    elif seller_commit == buyer_principal:
        order.tb.user.money_operatesafe(Const['model.record.pricipal'], seller_commit, \
                                        '订单本金归还，订单编号：%d' % order.id)
    elif seller_commit > buyer_principal:
        ret = order.task.store.user.money_operatesafe(Const['model.record.pricipal'], \
                                                      buyer_principal - seller_commit, '返款金额不足扣款，订单编号：%d' % order.id)
        if ret < 0:
            return Const['code.amount.exceed']
        else:
            order.tb.user.money_operatesafe(Const['model.record.pricipal'], seller_commit, \
                                            '订单本金归还，订单编号：%d' % order.id)
    return Const['code.success']


#    order = Order.objects.get(pk=order_id)
#    seller = order.task.store.user
#    buyer = order.tb.user
#    sell = order.get_seller_commit()
#    buyer_commit = Decimal(order.get_buyer_commit())
#    if sell == None:
#        seller_commit = order.buyer_principal
#    else:
#        seller_commit = Decimal(sell)
#    if buyer_commit < seller_commit:
#        difference = seller_commit - buyer_commit
#        buyer.money_operate(Const['model.record.pricipal'],
#                                    buyer_commit, '订单本金归还，订单编号：%d' % order.id,
#                                    Const['model.record.category.principalreturn'])
#        seller.money_operate(Const['model.record.pricipal'],
#                                    difference, '订单剩余本金归还，订单编号：%d' % order.id,
#                                    Const['model.record.category.principalreturn'])
#        buyer.notice_set(Const['model.remind.evaluated'], True)  # 待评价通知标志位
#        # buyer.save()
#        return JsonResponse(code=Const['code.success'])
#    elif buyer_commit == seller_commit:
#        buyer.money_operate(Const['model.record.pricipal'],
#                                    buyer_commit, '订单本金归还，订单编号：%d' % order.id,
#                                    Const['model.record.category.principalreturn'])
#        buyer.notice_set(Const['model.remind.evaluated'], True)  # 待评价通知标志位
#        # buyer.save()
#        return JsonResponse(code=Const['code.success'])
#    else:
#        buyer.money_operate(Const['model.record.pricipal'],
#                                    seller_commit, '订单本金归还，订单编号：%d' % order.id,
#                                    Const['model.record.category.principalreturn'])
#        order.flag_set(2, True)
#        buyer.notice_set(Const['model.remind.evaluated'], True)  # 待评价通知标志位
#        # buyer.save()
#        order.flag_set(Const['model.remind.idc_verify'], True)    # 问题订单标志位
#        order.difference = buyer_commit - seller_commit
#        order.save()
#        return JsonResponse(code=Const['code.success'])

@admin_permission('normal')
def rebate_difference(r):
    start, num = get_paginator(r)
    params = r.REQUEST
    conditions = make_conditions(r, pk='order_id', task__store_id='store_id', tb__user_id='buyer_id')
    if 'start_date' in params:
        conditions['receive_time__gte'] = get_stamp_by_date(params['start_date'])
    if 'end_date' in params:
        conditions['receive_time__lte'] = get_stamp_by_date(params['end_date'])
    orders = Order.objects.filter(**conditions).filter(flags__gte=4)[start:start + num]
    total = Order.objects.filter(**conditions).filter(flags__gte=4).count()
    data = []
    for o in orders:
        d = {}
        d['receive_time'] = o.receive_time
        d['store_name'] = o.task.store.name
        d['store_id'] = o.task.store.user.id
        d['buyer_wangwang'] = o.tb.wangwang
        d['buyer_id'] = o.tb.user.id
        d['order_id'] = o.id
        d['difference'] = o.difference
        d['order_principal'] = o.buyer_principal
        d['order_seller_commit'] = o.get_seller_commit()
        d['order_buyer_commit'] = o.get_buyer_commit()
        flags = o.flag_has(1)  # 取出处理标志位
        if flags == 1:
            d['handle'] = 1
        else:
            d['handle'] = 0
        data.append(d)
    return JsonResponse(code=Const['code.success'], data={'total': total, 'orders': data})


@admin_permission('normal')
def flags_handle(r, order_id):
    order = Order.objects.get(pk=order_id)
    if order.frozen:
        return JsonResponse(code=Const['code.order.frozen'], msg=u'订单已冻结无法操作')
    seller = order.task.store.user
    buyer = order.tb.user
    flags = order.flag_has(2)  # 取出问题标志位
    if flags == 1:
        order.flag_set(1, True)  # 处理标志位
        order.save()
        buyer.money_operate(Const['model.record.pricipal'],
                            order.difference, '买手实际支付金额与平台返款差额补款，订单编号：%d' % order.id,
                            Const['model.record.category.principalreturn'])
        seller.money_operate(Const['model.record.pricipal'],
                             -order.difference, '买手实际支付金额与平台返款差额扣款，订单编号：%d' % order.id,
                             Const['model.record.category.principalreturn'])
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.system_error'])


# 老数据迁移程序
@admin_permission('normal')
def flow_handle(r):
    timestamp = before15(30)
    tasks = Task.objects.filter(create_time__gte=timestamp)
    for task in tasks:
        search_entries = json.loads(task.search_entries)
        if not search_entries:
            continue
        if search_entries[0]["flow_total"] > 0:
            task.flow = True
        task.save(update_fields=['flow'])
    return JsonResponse(code=Const['code.success'])


# 下面的代码全部为测试
def test_reset(r, id):
    user = User.objects.get(pk=id)
    user_id = user.id
    tb = TBAccount.objects.get(user=user)
    tb_id = tb.id
    code = 0
    msg = u''

    sql = u'''update users_tbaccount set today_receive_orders='0' where id='44' '''
    sql2 = u''' delete from tasks_storerecentbuyer where tb_id='44' '''
    sql3 = u''' delete from tasks_storerecentbuyeruser where user_id='29720' '''
    sql4 = u''' delete from tasks_order where tb_id='44' '''

    sql = u'''update users_tbaccount set today_receive_orders='0' where id='44' '''
    sql2 = u''' delete from tasks_storerecentbuyer where tb_id='44' '''
    sql3 = u''' delete from tasks_storerecentbuyeruser where user_id='29720' '''
    sql4 = u''' delete from tasks_order where tb_id='44' '''
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.execute(sql4)
        return JsonResponse(code=code, msg=msg)
    except:
        code = -1
        msg = u'error'
        return JsonResponse(code=code, msg=msg)


# 测试每天清除旺旺号的购买记录
def test_daily_clean_buy_record():
    tbaccounts = TBAccount.objects.all()
    for tb in tbaccounts:
        user_id = tb.user_id
        wangwang = tb.id
        logger.info('user_id:%d  wangwang:%d  clean today_receive_orders %d  cleaned' % (
            user_id, wangwang, tb.today_receive_orders))
        tb.today_receive_orders = 0
        tb.save()


# 测试自动返款
def testorder_manager(r):
    o = Order.objects.get(pk=669938616)
    order_auto_returndeliver(o)


def testauto_return(r):
    nowtime = msec_time()
    # 自动返款
    orders = Order.objects.filter(status=Const['model.order.status.step3'],
                                  receive_time__lte=nowtime - 12 * Const['ms.per.hour'],  # 这里应该是12小时的，测试环境下的
                                  task__return_type=Const['model.task.return_type.platform']).exclude(frozen=True)
    # logger.debug(orders.query)
    counter = 0
    for o in orders:
        if _order_returndeliver(o):
            with transaction.atomic():
                counter = counter + 1
                o.save()
                # 避免刷手提交资金和商家的商品资金不同的情况
                # order_auto_returndeliver(o)
                # 原来的情况
                o.tb.user.money_operate(Const['model.record.pricipal'],
                                        o.buyer_principal, '订单本金归还，订单编号：%d' % o.id,
                                        Const['model.record.category.principalreturn'])
    logger.info('自动还款数：%d' % counter)


# 系统统计功能如果缺失的话进行硬性启动
def testdaily_report(r):
    logger.info('daily report start')
    today = date.today() - timedelta(days=1)
    yesterday = today - timedelta(days=1)
    start_stamp = time.mktime(yesterday.timetuple()) * 1000
    end_stamp = time.mktime(today.timetuple()) * 1000
    new_orders = Order.objects.filter(task__create_time__gte=start_stamp,
                                      task__create_time__lt=end_stamp)
    # 放单数
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.new_order_num'],
                               value=new_orders.count())
    # 放单金额
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.new_order_payment'],
                               amount=new_orders.aggregate(Sum('seller_payment'))[
                                   'seller_payment__sum'] if new_orders else 0)
    ##
    finish_orders = Order.objects.filter(status=Const['model.order.status.completed'], update_time__gte=start_stamp,
                                         update_time__lt=end_stamp)
    (finish_orders_num, finish_orders_payment, finish_orders_gain, finish_orders_principal) = reduce(
            lambda a, b: (a[0] + b[0], a[1] + b[1], a[2] + b[2], a[3] + b[3]), ((1, o.seller_payment, o.buyer_gain,
                                                                                 o.buyer_principal if o.task.return_type ==
                                                                                                      Const[
                                                                                                          'model.task.return_type.platform'] else 0)
                                                                                for o in
                                                                                finish_orders)) if finish_orders else (
        0, 0, 0, 0)
    # 完成单数
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.finish_order_num'],
                               value=finish_orders_num)
    # 完成单金额
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.finish_order_payment'],
                               amount=finish_orders_payment)
    # 签到佣金金额
    signup_amount = Record.objects.filter(category=Const['model.record.category.signup'], create_time__gte=start_stamp,
                                          create_time__lt=end_stamp).aggregate(Sum('amount'))['amount__sum']
    signup_amount = signup_amount if signup_amount else 0
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.signup'], amount=signup_amount)
    # 推广佣金金额
    promote_amount = \
        Record.objects.filter(category=Const['model.record.category.promote'], create_time__gte=start_stamp,
                              create_time__lt=end_stamp).aggregate(Sum('amount'))['amount__sum']
    promote_amount = promote_amount if promote_amount else 0
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.promote'], amount=promote_amount)
    # 毛利润
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.profit'], amount=(
        finish_orders_payment - finish_orders_gain - finish_orders_principal - signup_amount - promote_amount))
    # 充值金额
    recharge_amount = Recharge.objects.filter(verify_time__gte=start_stamp, verify_time__lt=end_stamp,
                                              verify_status=Const['model.verify.check_pass']).aggregate(Sum('amount'))[
        'amount__sum']
    recharge_amount = recharge_amount if recharge_amount else 0
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.recharge'], amount=recharge_amount)
    # 本金提现
    principal_withdraw_amount = \
        Withdraw.objects.filter(type=Const['model.withdraw.type.principal'], verify_time__gte=start_stamp,
                                verify_time__lt=end_stamp, verify_status=Const['model.verify.check_pass']).aggregate(
                Sum('amount'))['amount__sum']
    principal_withdraw_amount = principal_withdraw_amount if principal_withdraw_amount else 0
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.principal_withdraw'],
                               amount=principal_withdraw_amount)
    # 佣金提现
    commission_withdraw_amount = \
        Withdraw.objects.filter(type=Const['model.withdraw.type.commission'], verify_time__gte=start_stamp,
                                verify_time__lt=end_stamp, verify_status=Const['model.verify.check_pass']).aggregate(
                Sum('amount'))['amount__sum']
    commission_withdraw_amount = commission_withdraw_amount if commission_withdraw_amount else 0
    DailyReport.objects.create(date=yesterday, type=Const['model.dailyreport.type.commission_withdraw'],
                               amount=commission_withdraw_amount)
    logger.info('daily report finish')
