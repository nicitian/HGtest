# encoding: utf-8
import decimal
import json
import logging
import math
import os

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import Http404, HttpResponse
from django.shortcuts import render

from laifu.const import Const
from laifu.filters import need_login, web_permission
from laifu.settings import LAIFU_IMAGE_DIR
from laifu.utils import del_dict_keys, get_date_by_stamp, get_datetime_by_stamp, \
    get_stamp_by_date, before15,make_conditions
from management.models import Recharge, Notice
import management.views
import others.views
from tasks.models import Store, Task, Order, Appeal, AppealType
import tasks.views
from users.models import User, Bankcard, Blacklist, Record
import users.views


logger=logging.getLogger(__name__)


def generic(request,app,model,action,id):
    #logger.info('request from %s'%request.path)
    return eval("%s.views.%s_%s(request,%s)" % (app,model,action,id))

def generic_2(request,app,model,action):
    #logger.info('request from %s'%request.path)
    return eval("%s.views.%s_%s(request)" % (app,model,action))

def generic_web(request,app,model,action,id):
    return eval("%s.views.%s_%s(request,%s)" % (app,model,action,id))

def generic_web_2(request,app,model,action):
    return eval("%s.views.%s_%s(request)" % (app,model,action))

def static_html(request,template_name):
    return render(request, template_name, None)

def image(request,fname):
    ftype=fname[fname.rindex('.')+1:].lower()
    logger.debug('file name: %s' % str(os.path.join(LAIFU_IMAGE_DIR , fname)))
    data = open(os.path.join(LAIFU_IMAGE_DIR , fname), "rb").read()
    return HttpResponse(data,content_type={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png',}[ftype])

def _home_init(r):
    allnotice = Notice.objects.filter(type=Const['model.notice.type.seller'])
    firstNotice = None
    if len(allnotice) > 0:
        firstNotice = allnotice[0]

    return User.objects.get_user_from_session(r),firstNotice
               
@need_login
def home_notice(request):
    user,last_notice=_home_init(request)
    notices=Notice.objects.filter(type=Const['model.notice.type.seller'])
    return render(request, 'home/home_notice.html', locals())

@need_login
def messages(request):
    user,last_notice=_home_init(request)
    return render(request, 'messages.html', locals())

@need_login
def startprivate_chat(request,uid):
    target_id = uid
    user,last_notice=_home_init(request)
    return render(request, 'messages.html', locals())

@need_login
def home_notice_detail(request):
    user,last_notice=_home_init(request)
    notice=Notice.objects.get(pk=request.REQUEST['notice_id'])
    return render(request, 'home/home_notice_detail.html', locals())

@need_login
def home_publish_post(request):
    user,last_notice=_home_init(request)
    store_list=Store.objects.filter(user_id=user.id,verify_status=Const['model.verify.check_pass'])
    if 'task_id' in request.REQUEST:
        task=Task.objects.get(pk=request.REQUEST['task_id'])
        commodities=json.loads(task.commodities)
    return render(request, 'home/home_publish_post.html', locals())

@web_permission('task','pay')
def home_publish_pay(request):
    #与Task.pay_all方法同步
    user,last_notice=_home_init(request)
    task=Task.objects.get(pk=request.REQUEST['task_id'])
    if task.status!=Const['model.task.status.need_payment']:
        raise Http404()
    commision_base=task._commision_base();
    commision_keyword=Const['payment.commision.extra.keyword'];
    commision_image=Const['payment.commision.extra.image'];
    commision_delaybuy = Const['payment.commision.deep.step'] * (task.step_interval - 1) + Const['payment.commision.base.deep']
    servicefee_base=Const['payment.fee.return'] if task.return_type==Const['model.task.return_type.platform'] else 0;
    normal_order_price=commision_base+task.bonus+servicefee_base;
    keyword_order_price=commision_base+commision_keyword+task.bonus+servicefee_base;
    image_order_price=commision_base+commision_image+task.bonus+servicefee_base;
    delaybuy_order_price = commision_base + commision_delaybuy + task.bonus + servicefee_base
    order_types=json.loads(task.order_types)
    logger.debug(order_types)
    normal_price=normal_order_price*order_types[Const['model.order.type.normal']]['order_total']
    keyword_price=keyword_order_price*order_types[Const['model.order.type.keyword']]['order_total']
    image_price=image_order_price*order_types[Const['model.order.type.image']]['order_total']
    delaybuy_price = delaybuy_order_price * order_types[Const['model.order.type.advance']]['order_total']
    payment_flow=Const['payment.commision.flow'];
    payment_collect=Const['payment.commision.collect'];
    flow_orders=order_types[Const['model.order.type.flow']]['order_total']
    collect_orders=order_types[Const['model.order.type.collect']]['order_total']
    flow_total=payment_flow*flow_orders+collect_orders*payment_collect
    order_total=order_types[Const['model.order.type.normal']]['order_total']+\
                order_types[Const['model.order.type.keyword']]['order_total'] + \
                order_types[Const['model.order.type.image']]['order_total'] + \
                order_types[Const['model.order.type.advance']]['order_total']
    commision_total=normal_price+keyword_price+image_price + delaybuy_price +decimal.Decimal(flow_total)
    dianzi=task.dianzi() if task.return_type==Const['model.task.return_type.platform'] else 0;
    dianzi_total=dianzi*order_total
    all_total=commision_total+dianzi_total
    can_afford=(user.principal>=all_total)
    return render(request, 'home/home_publish_pay.html', locals())

@need_login
def home_user(request):
    user,last_notice=_home_init(request)
    user.notice_set(Const['model.remind.store_verify'], False)
    register_date=get_date_by_stamp(user.register_time)
    store_list=user.store_set.all()
    return render(request, 'home/home_user.html', locals())

@need_login
def home_capital(request):
    user,last_notice=_home_init(request)
    user.notice_set(Const['model.remind.principal'], False)
    params=request.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num
    timestamp = before15(30)
    conditions=make_conditions(request)
    conditions['user_id'] = user.id
    if 'create_time_start' in params or 'create_time_end'in params:
        if 'create_time_start' in params:
            conditions['create_time__gte'] = get_stamp_by_date(params['create_time_start'])
        if 'create_time_end'in params:
            conditions['create_time__lte'] = get_stamp_by_date(params['create_time_end'])
    else:
        conditions['create_time__gte'] = 0

    if 'capital_type' in params:
        if int(params['capital_type'])==0:
            conditions['amount__lte'] = 0.0
        elif int(params['capital_type'])==1:
            conditions['amount__gte'] = 0.0
    query=Record.objects.filter(**conditions)

    pagebar=_pagebar_obj(query.count(),page,num)
    records=query[start:start+num]
    return render(request, 'home/home_capital.html', locals())

def home_appeal(request):
    user,last_notice=_home_init(request)
    user.notice_set(Const['model.remind.appeal'], False)
    appeals=Appeal.objects.filter(Q(complainant_id=user.id)|Q(respondent_id=user.id)) \
                                           .filter(order__task__store__user__id=user.id)
    return render(request, 'home/home_appeal.html', locals())

def home_tutorial(request):
    return render(request, 'home/home_tutorial.html', locals())

def _pagebar_obj(record_total,current_page,record_per_page):
    pagebar={
             'record_total':record_total,
             'record_per_page':record_per_page,
             'current_page':current_page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/record_per_page))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return pagebar

@need_login
def task_order_appeal(request, oid):
    user=User.objects.get_user_from_session(request)
    order = Order.objects.get(pk=oid)
    if order.receive_time:
        order.receive_time_str=get_datetime_by_stamp(order.receive_time)
    return render(request, 'task/order_appeal.html', locals())


@need_login
def home_capital_recharge(r):
    user,last_notice=_home_init(r)
    recharges=Recharge.objects.filter(user_id=user.id)[0:5]
    for re in recharges:
        re.create_time_str=get_datetime_by_stamp(re.create_time)
        re.verify_time_str=get_datetime_by_stamp(re.verify_time) if re.verify_time else ''
    return render(r, 'home/home_capital_recharge.html', locals())

@need_login
def home_task_tasks(r):
    user,last_notice=_home_init(r)
    stores=user.store_set.filter(verify_status=Const['model.verify.check_pass'])
    params=r.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num
    query_condition=[Q(store__user_id=user.id),]
    if 'store_id' in params:
        query_condition.append(Q(store_id=params['store_id']))
    if 'task_id' in params:
        query_condition.append(Q(id=params['task_id']))
    if 'publish_start' in params:
        query_condition.append(Q(publish_start_date__gte=params['publish_start']))
    if 'publish_end' in params:
        query_condition.append(Q(publish_start_date__lte=params['publish_end']))
    if 'task_status' in params:
        task_status=int(params['task_status'])
        if task_status==0:
            query_condition.append(Q(verify_status=Const['model.verify.need_check']))
        elif task_status==1:
            query_condition.append(Q(verify_status=Const['model.verify.check_pass']))
        elif task_status==2:
            query_condition.append(Q(status=Const['model.task.status.closed']))
        elif task_status==3:
            query_condition.append(Q(verify_status=Const['model.verify.check_deny']))
    if 'task_type' in params:
        task_type=int(params['task_type'])
        if task_type==0:
            query_condition.append(Q(task_type=Const['model.task.type.mobile_taobao']))
        elif task_type == 1:
            query_condition.append(Q(task_type=Const['model.task.type.pc_taobao']))
        elif task_type == 2:
            query_condition.append(Q(task_type=Const['model.task.type.flow']))
        elif task_type == 3:
            query_condition.append(Q(task_type=Const['model.task.type.special']))
    if 'keywords' in params:
        query_condition.append(Q(commodities_contains=params['keywords'])|\
                               Q(search_entries=params['keywords']))
    timestamp = before15(30)
    tasks=Task.objects.filter(*query_condition).exclude(task_type=Const['model.task.type.flow']) \
    .filter(create_time__gte=timestamp)[start:start+num]
    print(tasks.count())
    print(tasks)
    logger.debug(tasks.query)
    odd=True
    for task in tasks:
        logger.debug(task.id)
        task.odd=odd
        odd=not odd
        task.mobile = True if task.task_type in (Const['model.task.type.mobile_taobao'],) else False
        task.jcommodities=json.loads(task.commodities)
        task.jsearch_entries=json.loads(task.search_entries)
        task.create_time_str=get_datetime_by_stamp(task.create_time)
        orders = Order.objects.filter(task_id=task.id) \
        .exclude(order_type__in=[Const['model.order.type.flow'], Const['model.order.type.collect']])
        # orders=task.order_set.filter()
        task.total_orders=orders.count()
        if task.status==Const['model.task.status.need_payment']:
            task.status_str='待支付'
        elif task.status==Const['model.task.status.cancel']:
            task.status_str='已取消'
        elif task.verify_status==Const['model.verify.check_deny']:
            task.status_str='审核不通过'
        elif task.verify_status==Const['model.verify.need_check']:
            task.status_str='待审核'
        elif task.status==Const['model.task.status.in_progress']:
            task.status_str='进行中'
        elif task.status==Const['model.task.status.closed']:
            task.status_str='已完成'
        elif task.status == Const['model.task.status.frozen']:
            task.status_str = '已冻结'
        task.order_1=task.order_2=task.order_3=task.order_4=task.order_5=task.order_6=0
        for o in orders:
            if o.status==Const['model.order.status.init']:
                task.order_1=task.order_1+1;
            elif o.status==Const['model.order.status.step3'] or o.status==Const['model.order.status.returnmoney']:
                task.order_3=task.order_3+1;
            elif o.status==Const['model.order.status.deliver']:
                task.order_4=task.order_4+1;
            elif o.status==Const['model.order.status.comment']:
                task.order_5=task.order_5+1;
            elif o.status==Const['model.order.status.completed']:
                task.order_6=task.order_6+1;
            elif o.status in (Const['model.order.status.received'],
                              Const['model.order.status.step1'],
                              Const['model.order.status.step2'],
                              Const['model.order.status.step9']):
                task.order_2=task.order_2+1;
    pagebar={
             'record_total':Task.objects.filter(*query_condition).exclude(task_type=Const['model.task.type.flow']) \
                                                                        .filter(create_time__gte=timestamp).count(),
             'record_per_page':num,
             'current_page':page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/num))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return render(r, 'home/home_task_tasks.html', locals())

@need_login
def home_task_flows(r):
    user,last_notice=_home_init(r)
    stores=user.store_set.filter(verify_status=Const['model.verify.check_pass'])
    params=r.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num
    query_condition=[Q(store__user_id=user.id),]
    if 'store_id' in params:
        query_condition.append(Q(store_id=params['store_id']))
    if 'task_id' in params:
        query_condition.append(Q(id=params['task_id']))
    if 'publish_start' in params:
        query_condition.append(Q(publish_start_date__gte=params['publish_start']))
    if 'publish_end' in params:
        query_condition.append(Q(publish_start_date__lte=params['publish_end']))
    if 'task_status' in params:
        task_status=int(params['task_status'])
        if task_status==0:
            query_condition.append(Q(verify_status=Const['model.verify.need_check']))
        elif task_status==1:
            query_condition.append(Q(verify_status=Const['model.verify.check_pass']))
        elif task_status==2:
            query_condition.append(Q(status=Const['model.task.status.closed']))
        elif task_status==3:
            query_condition.append(Q(verify_status=Const['model.verify.check_deny']))
    if 'task_type' in params:
        task_type=int(params['task_type'])
        if task_type==0:
            query_condition.append(Q(task_type=Const['model.task.type.mobile_taobao']))
    if 'keywords' in params:
        query_condition.append(Q(commodities_contains=params['keywords'])| Q(search_entries=params['keywords']))
    timestamp = before15(30)
    tasks=Task.objects.filter(*query_condition).filter(create_time__gte=timestamp).filter(flow=True)[start:start+num]
    logger.debug(tasks.query)
    odd = True
    for task in tasks:
        orders = Order.objects.filter(task_id=task.id) \
        .filter(order_type__in=[Const['model.order.type.flow'], Const['model.order.type.collect']])
        # orders=task.order_set.filter()
        task.total_orders=orders.count()
        logger.debug(task.id)
        task.odd = odd
        odd = not odd
        task.jsearch_entries=json.loads(task.search_entries)
        task.mobile = True if task.task_type in (Const['model.task.type.mobile_taobao'],) else False
        task.jcommodities=json.loads(task.commodities)
        task.create_time_str=get_datetime_by_stamp(task.create_time)
        if task.status==Const['model.task.status.need_payment']:
            task.status_str='待支付'
        elif task.status==Const['model.task.status.cancel']:
            task.status_str='已取消'
        elif task.verify_status==Const['model.verify.check_deny']:
            task.status_str='审核不通过'
        elif task.verify_status==Const['model.verify.need_check']:
            task.status_str='待审核'
        elif task.status==Const['model.task.status.in_progress']:
            task.status_str='进行中'
        elif task.status==Const['model.task.status.closed']:
            task.status_str='已完成'
        elif task.status == Const['model.task.status.frozen']:
            task.status_str = '已冻结'
        task.order_1=task.order_2=task.order_5=task.order_6=0
        for o in orders:
            if o.status==Const['model.order.status.init']:
                task.order_1=task.order_1+1;
            elif o.status==Const['model.order.status.comment']:
                task.order_5=task.order_5+1;
            elif o.status==Const['model.order.status.completed']:
                task.order_6=task.order_6+1;
            elif o.status in (Const['model.order.status.received'],
                              Const['model.order.status.step1'],
                              Const['model.order.status.step2'],):
                task.order_2=task.order_2+1;
    pagebar={
             'record_total': Task.objects.filter(*query_condition).filter(create_time__gte=timestamp) \
                                .filter(Q(flow=True) | Q(task_type=Const['model.task.type.flow'])).count(),
             'record_per_page':num,
             'current_page':page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/num))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return render(r, 'home/home_task_flow.html', locals())

@need_login
def home_blicklist(r):
    user,last_notice=_home_init(r)
    blacklists=Blacklist.objects.filter(seller=user)
    for b in blacklists:
        b.time_str=get_datetime_by_stamp(b.create_time)
    return render(r, 'home/home_blacklist.html', locals())

@need_login
def modify_store(r):
    stores = Store.objects.filter(user_id=r.REQUEST['user_id'],id=r.REQUEST['store_id'])
    if len(stores)>0:
        store = stores[0]
        address = store.address
        address_splited = address.split('-')
        province = address_splited[0]
        city = address_splited[1]
        district = address_splited[2]
    return render(r, 'modify_store.html', locals())



@need_login
def task_task_detail(r):
    user=User.objects.get_user_from_session(r)
    task=Task.objects.get(pk=r.REQUEST['task_id']);
    task.create_time_str=get_datetime_by_stamp(task.create_time)
    orders= Order.objects.filter(task_id=r.REQUEST['task_id']).exclude(order_type=Const['model.order.type.flow'])
    total_orders=orders.count()
    receive_orders=0
    commodities=json.loads(task.commodities)
    search_entries=json.loads(task.search_entries)
    order_types=json.loads(task.order_types)
    store=task.store
    if task.status==Const['model.task.status.need_payment']:
        status=0
    elif task.verify_status==Const['model.verify.need_check']:
        status=1
    elif task.status==Const['model.task.status.in_progress']:
        status=2
    elif task.status==Const['model.task.status.closed']:
        status=3
    for order in orders:
        if(order.status!=Const['model.order.status.init']):
            receive_orders=receive_orders+1
    return render(r, 'task/task_detail.html', locals())

@need_login
def task_flow_detail(r):
    user=User.objects.get_user_from_session(r)
    task=Task.objects.get(pk=r.REQUEST['task_id']);
    task.create_time_str=get_datetime_by_stamp(task.create_time)
    orders = Order.objects.filter(task_id=r.REQUEST['task_id']) \
             .filter(order_type__in=[Const['model.order.type.flow'], Const['model.order.type.collect']])
    total_orders=orders.count()
    receive_orders=0
    commodities=json.loads(task.commodities)
    search_entries=json.loads(task.search_entries)
    order_types=json.loads(task.order_types)
    store=task.store
    if task.status==Const['model.task.status.need_payment']:
        status=0
    elif task.verify_status==Const['model.verify.need_check']:
        status=1
    elif task.status==Const['model.task.status.in_progress']:
        status=2
    elif task.status==Const['model.task.status.closed']:
        status=3
    for order in orders:
        if order.status != Const['model.order.status.init']:
            receive_orders = receive_orders+1
    return render(r, 'task/flow_task_detail.html', locals())

@need_login
def task_order_detail(r):
    user=User.objects.get_user_from_session(r)
    order=Order.objects.get(pk=r.REQUEST['order_id'])
    task=order.task
    bankcard=order.bankcard
    appeal_types=AppealType.objects.filter(type=Const['model.notice.type.seller'])
    progress_appeal=Appeal.objects.filter(order=order,status=Const['model.appeal.status.in_progress']) 
    task_type = task.task_type
    if bankcard:
        account=bankcard.account_id
        account_str=' '.join([account[i:i+4] for i in range(0,len(account),4)])
    is_comment_order=True if order.order_type in (Const['model.order.type.normal'],
                                                  Const['model.order.type.keyword'],
                                                  Const['model.order.type.image'],
                                                  ) else False
    if order.receive_time:
        order.receive_time_str=get_datetime_by_stamp(order.receive_time)
    order.check_upgrade()
    # 借用flags用来存储是否被拉黑的状态
    buyer = order.tb.user
    order.flags = 0
    if Blacklist.objects.filter(seller=user,buyer=buyer):
        order.flags = 1

    steps = []
    for key in order.get_steps():
        order.get_steps()[key]['time_str']=get_datetime_by_stamp(order.get_steps()[key]['create_time'])
        steps.append(order.get_steps()[key])

    #_steps=json.loads(order.step_detail)

    # logger.info(steps)
    # for key in steps:
    #    steps[key]['time_str']=get_datetime_by_stamp(steps[key]['create_time'])

    return render(r, 'task/order_detail.html', locals())

@need_login
def task_return_manage(r):
    user=User.objects.get_user_from_session(r)
    user.notice_set(Const['model.remind.no_money'], False)
    stores=user.store_set.filter(verify_status=Const['model.verify.check_pass'])
    params=r.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num

    q_not_return = Q(status=Const['model.order.status.step3'])
    q_returned = Q(status__in=[
        Const['model.order.status.completed'],
        Const['model.order.status.comment'],
        Const['model.order.status.returnmoney'],
        Const['model.order.status.deliver'],
        Const['model.order.status.affirm']
    ])
    q_all = Q(status__in=[
        Const['model.order.status.step3'],
        Const['model.order.status.completed'],
        Const['model.order.status.comment'],
        Const['model.order.status.returnmoney'],
        Const['model.order.status.deliver'],
        Const['model.order.status.affirm']
    ])

    query_condition=[Q(order_type__in=[Const['model.order.type.normal'],
                                       Const['model.order.type.keyword'],
                                       Const['model.order.type.image'],
                                       Const['model.order.type.advance'],
                                      ]),\
                     Q(task__store__user_id=user.id)\
                    ]
    if 'store_id' in params:
        query_condition.append(Q(task__store_id=params['store_id']))
    if 'task_id' in params:
        query_condition.append(Q(task_id=params['task_id']))
    if 'order_id' in params:
        query_condition.append(Q(pk=params['order_id']))
    if 'buyer_id' in params:
        query_condition.append(Q(tb__user_id=params['buyer_id']))
    if 'return_status' in params:
        if params['return_status']=='1':
            query_condition.append(q_returned)
        else:
            query_condition.append(q_not_return)
    else:
        query_condition.append(q_not_return)
    if 'buyer_wangwang' in params:
        query_condition.append(Q(tb__wangwang=params['buyer_wangwang']))
    orders=Order.objects.filter(*query_condition)[start:start+num]
    logger.debug(orders.query)
    for order in orders:
        order.buy_time_str=get_datetime_by_stamp(order.get_step_item(2,'create_time'))
        if order.task.task_type == Const['model.task.type.special'] or \
        order.order_type == Const['model.order.type.flow'] or \
        order.order_type == Const['model.order.type.collect']:
            order.buy_pic1=order.get_step_item(0, 'pic_path')[0]
            order.buy_pic2=order.get_step_item(0,'pic_path')[1]
        elif order.order_type == Const['model.order.type.advance']:
            order.buy_pic1 = order.get_step_item(0, 'pic_path')[0];
            order.buy_pic2 = order.get_step_item(0, 'pic_path')[1];
        else:
            order.buy_pic1=order.get_step_item(2, 'pic_path')[0]
            order.buy_pic2=order.get_step_item(2, 'pic_path')[1]
        # logger.info('task_return_manage order_type is %d'%order.order_type)
    pagebar={
             'record_total':Order.objects.filter(*query_condition).count(),
             'record_per_page':num,
             'current_page':page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/num))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return render(r, 'task/return_manage.html', locals())

@need_login
def task_order_manage(r):
    user=User.objects.get_user_from_session(r)
    stores=user.store_set.filter(verify_status=Const['model.verify.check_pass'])
    params=r.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num
    query_condition=[Q(task__store__user_id=user.id),]
    be15 = before15(15)
    if 'store_id' in params:
        query_condition.append(Q(task__store_id=params['store_id']))
    if 'buyer_id' in params:
        query_condition.append(Q(tb__user_id=params['buyer_id']))
    if 'buyer_wangwang' in params:
        query_condition.append(Q(tb__wangwang=params['buyer_wangwang']))
    if 'task_id' in params:
        query_condition.append(Q(task_id=params['task_id']))
    if 'order_id' in params:
        query_condition.append(Q(pk=params['order_id']))
    if 'order_type' in params:
        ordertype = int(params['order_type'])
        if ordertype <= Const['model.order.type.max']:
            query_condition.append(Q(order_type=ordertype))
    if 'order_status' in params:
        if params['order_status']=='1':
            query_condition.append(Q(status__in=[
                Const['model.order.status.received'],
                Const['model.order.status.step1'],
                Const['model.order.status.step2'],
                Const['model.order.status.step9'],
            ]))
        elif params['order_status']=='2':
            query_condition.append(Q(status__in=[
                                                 Const['model.order.status.step3'],
                                                 Const['model.order.status.returnmoney'],
                                                ]))
        elif params['order_status']=='3':
            query_condition.append(Q(status=Const['model.order.status.deliver']))
        elif params['order_status']=='4':
            query_condition.append(Q(status=Const['model.order.status.comment']))
        elif params['order_status']=='5':
            query_condition.append(Q(status=Const['model.order.status.completed']))
    if 'receive_start' in params:
        query_condition.append(Q(receive_time__gte=get_stamp_by_date(params['receive_start'])))
    if 'receive_end' in params:
        query_condition.append(Q(receive_time__lte=get_stamp_by_date(params['receive_end'])))
    q=Order.objects.exclude(status__in=[Const['model.order.status.init'], Const['model.order.status.cancel']]) \
        .exclude(order_type__in=[Const['model.order.type.flow'], Const['model.order.type.collect']]) \
        .filter(*query_condition).filter((Q(status=Const['model.order.status.completed']) & \
        Q(update_time__gte=be15)) | ~Q(status=Const['model.order.status.completed']))
    orders=q[start:start+num]
    logger.debug(orders.query)
    for o in orders:
        # 判断是否已经被拉黑了,暂时借用了flags标志位
        buyer = o.tb.user
        o.flags = 0
        if Blacklist.objects.filter(seller=user,buyer=buyer):
            o.flags = 1
        if o.receive_time:
            o.receive_time_str=get_datetime_by_stamp(o.receive_time)
    pagebar={
             'record_total':q.count(),
             'record_per_page':num,
             'current_page':page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/num))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return render(r, 'task/order_manage.html', locals())


@need_login
def task_flow_manage(r):
    user=User.objects.get_user_from_session(r)
    stores=user.store_set.filter(verify_status=Const['model.verify.check_pass'])
    params=r.REQUEST
    page=int(params['page']) if 'page' in params else 1
    num=int(params['num']) if 'num' in params else 10
    start=(page-1)*num
    query_condition=[Q(task__store__user_id=user.id),]
    be15 = before15(15)
    if 'store_id' in params:
        query_condition.append(Q(task__store_id=params['store_id']))
    if 'buyer_id' in params:
        query_condition.append(Q(tb__user_id=params['buyer_id']))
    if 'buyer_wangwang' in params:
        query_condition.append(Q(tb__wangwang=params['buyer_wangwang']))
    if 'task_id' in params:
        query_condition.append(Q(task_id=params['task_id']))
    if 'order_id' in params:
        query_condition.append(Q(pk=params['order_id']))
#    if 'order_type' in params:
#        ordertype = int(params['order_type'])
#        if ordertype <= Const['model.order.type.max']:
#            query_condition.append(Q(order_type=ordertype))
    if 'order_status' in params:
        if params['order_status']=='1':
            query_condition.append(Q(status__in=[
                Const['model.order.status.received'],
                Const['model.order.status.step1'],
                Const['model.order.status.step2'],
            ]))
        elif params['order_status']=='4':
            query_condition.append(Q(status=Const['model.order.status.comment']))
        elif params['order_status']=='5':
            query_condition.append(Q(status=Const['model.order.status.completed']))
    if 'receive_start' in params:
        query_condition.append(Q(receive_time__gte=get_stamp_by_date(params['receive_start'])))
    if 'receive_end' in params:
        query_condition.append(Q(receive_time__lte=get_stamp_by_date(params['receive_end'])))
    q=Order.objects.exclude(status__in=[Const['model.order.status.init'],
        Const['model.order.status.cancel']]).filter(*query_condition) \
        .filter(order_type__in=[Const['model.order.type.flow'], Const['model.order.type.collect']]) \
        .filter((Q(status=Const['model.order.status.completed']) & Q(update_time__gte=be15)) | \
        ~Q(status=Const['model.order.status.completed']))
    orders=q[start:start+num]
    logger.debug(orders.query)
    for o in orders:
        if o.receive_time:
            o.receive_time_str=get_datetime_by_stamp(o.receive_time)
    pagebar={
             'record_total':q.count(),
             'record_per_page':num,
             'current_page':page,
            }
    pagebar['page_total']=int(math.ceil(1.0*pagebar['record_total']/num))
    pagebar['page_total_list']=range(1,pagebar['page_total']+1)
    return render(r, 'task/flow_manage.html', locals())


@need_login
def home_promote(request):
    user,last_notice=_home_init(request)
    return render(request, 'home/home_promote.html', locals())


def notice(r,nid):
    notice=Notice.objects.get(pk=nid)
    notice.update_time=get_datetime_by_stamp(notice.update_time)
    return render(r, 'mobile/notice.html', {'notice':notice})


