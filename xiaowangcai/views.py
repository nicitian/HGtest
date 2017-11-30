# encoding: utf-8
import json
import logging
import random
from decimal import Decimal
from random import randint

from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from qiniu.auth import Auth

from lib.sms.CCPRestSDK import SMSService
from management.models import Withdraw
from shouzhuan.const import Const
from shouzhuan.filters import rest_permission, admin_permission, mutex_lock, \
    need_login, app_check
from shouzhuan.utils import JsonResponse, msec_time, get_paginator, fix_length_random_int, make_conditions, sub_dict, obj_to_dict, \
    get_date_by_stamp, get_stamp_by_date, obj_verify, CsvResponse, \
    get_datetime_by_stamp, before15, reward
from tasks.models import Order, Appeal
from users.forms import SignupForm, IdcForm, LoginForm, TBAccountForm, BankcardForm
from users.models import Bankcard, Blacklist, Record
from .models import User, Smscaptcha, TBAccount

logger = logging.getLogger(__name__)
qiniu = Auth(Const['qiniu.ak'], Const['qiniu.sk'])
qiniu_token = None
qiniu_expires = 0


@need_login
def user_qninfo(self):
    global qiniu, qiniu_token, qiniu_expires
    now = msec_time()
    if now > qiniu_expires:
        logger.debug('qiniu token reflush')
        qiniu_token = qiniu.upload_token(Const['qiniu.workspace'], None, Const['qiniu.maxage'])
        qiniu_expires = now + 1000 * (Const['qiniu.maxage'] - Const['qiniu.safe'])
    return JsonResponse(code=Const['code.success'], data={
        'token': qiniu_token,
        'expires': qiniu_expires,
        'domain': Const['qiniu.domain'],})


def smscaptcha_request(request, phone):
    capt = str(randint(100000, 999999))
    nowtime = msec_time()
    try:
        r = Smscaptcha.objects.get(phone=phone)
        r.create_time = nowtime
        r.captcha = capt
        r.save()
    except ObjectDoesNotExist:
        r = Smscaptcha.objects.create(phone=phone, captcha=capt, create_time=nowtime)
    result = SMSService.sendTemplateSMS(phone, [capt, Const['sms.valid.time']], 89306)
    if (result['statusCode'] == '000000'):
        return JsonResponse(code=Const['code.success'])
    else:
        logger.error(result)
        return JsonResponse(code=Const['code.system_error'])


def _smscaptcha_verify(phone, captcha):
    cap = Smscaptcha.objects.filter(phone=phone)
    if (not cap) or (cap[0].captcha != captcha) or \
            (msec_time() > cap[0].create_time + Const['sms.valid.time'] * Const['const.msperminute']):
        return False
    else:
        return True


@transaction.atomic
def user_create(request):
    form = SignupForm(request.POST)
    if form.is_valid():
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']
        captcha = form.cleaned_data['captcha']
        inviterId = form.cleaned_data['inviter']
        qq = form.cleaned_data['qq']
        if not qq:
            qq = ' '
        user = User.objects.filter(phone=phone)
        if user:
            return JsonResponse(code=Const['code.username_exist'])
        if not _smscaptcha_verify(phone, captcha):
            return JsonResponse(code=Const['code.sms_error'])
        while True:
            uid = fix_length_random_int(5)
            if User.objects.filter(pk=uid).count() == 0:
                break

        if inviterId:
            inviter = User.objects.filter(id=inviterId)
            if not inviter:
                return JsonResponse(code=Const['code.inviter_not_exist'])
            inviter = inviter[0]
            inviter.promote_num = inviter.promote_num + 1
            inviter.save()
            curUser = User.objects.create(id=uid, username=phone, phone=phone, password=password, inviter=inviter,
                                          join_award=True, qq=qq)
        else:
            curUser = User.objects.create(id=uid, username=phone, phone=phone, password=password, join_award=True,
                                          qq=qq)
        #         无论是否有邀请人都给奖励
        curUser.money_operate(Const['model.record.commission'],
                              Const['common.join.award'], '注册奖励',
                              Const['model.record.category.join'])
        return JsonResponse(code=Const['code.success'])


def user_changepwd(r, uid):
    params = r.REQUEST;
    old_password = params['old_password']
    new_password = params['new_password']
    u = User.objects.get(pk=uid)
    if old_password == u.password:
        u.password = new_password
        u.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.password_error'])


def user_forgetpwd(r):
    params = r.REQUEST;
    phone = params['phone']
    new_password = params['new_password']
    captcha = params['captcha']
    try:
        u = User.objects.get(phone=phone)
    except ObjectDoesNotExist:
        return JsonResponse(code=Const['code.user_not_exists'])
    if _smscaptcha_verify(phone, captcha):
        u.password = new_password
        u.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.sms_error'])


def user_login(request):
    form = LoginForm(request.REQUEST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return JsonResponse(code=Const['code.login_error'])
        if user.is_freezed():
            return JsonResponse(code=Const['code.request_error'])
        if user.password != password:
            return JsonResponse(code=Const['code.login_password_error'])
        if user.flag_has(Const['user.flags.locked']):
            return JsonResponse(code=Const['code.login_accountlocked'], msg=u'账号异常')
        request.session['user_id'] = user.id
        if (form.cleaned_data['persistent'] == 1):
            request.session.set_expiry(Const['session.persistent.time'])
        #        for i in range(8):
        #            if user.notice_has(i) == 1:
        #                d['notice_' + str(i)] = True
        #            else:
        #                d['notice_' + str(i)] = False
        return JsonResponse(code=Const['code.success'], data=user.to_data())
    return JsonResponse(code=Const['code.request_error'])


def get_notice(r, user_id):
    user = User.objects.get(pk=user_id)
    data = []
    for i in range(15):
        if user.notice_has(i) == 1:
            d = 100 + i
            data.append(d)
        #    d = {}
        #    for i in range(8):
        #        if user.notice_has(i) == 1:
        #            d['notice_'+str(i)] = True
        #        else:
        #            d['notice_'+str(i)] = False
    return JsonResponse(code=Const['code.success'], data=data)


def get_remind(r, p):
    user = User.objects.get(phone=p)
    data = []
    for i in [1, 5, 6, 9]:
        if user.notice_has(i) == 1:
            d = 100 + i
            data.append(d)
    return JsonResponse(code=Const['code.success'], data=data)


def notice_sets(r, uid):
    user = User.objects.get(pk=uid)
    params = r.REQUEST
    logger.info(params)
    if 'bit' in params:
        n = int(params['bit'])
        user.notice_set(n, False)
        # user.save()
        data = []
        for i in range(15):
            if user.notice_has(i) == 1:
                d = 100 + i
                data.append(d)
        return JsonResponse(code=Const['code.success'], data=data)
    else:
        return JsonResponse(code=Const['code.request_error'])


def user_this(request):
    if 'user_id' in request.session:
        return JsonResponse(code=Const['code.success'], data=User.objects.get(pk=request.session['user_id']).to_data())
    else:
        return JsonResponse(code=Const['code.permission_deny'])


def user_get(request, mid):
    return JsonResponse(code=Const['code.success'], data=User.objects.get(pk=mid).to_data())


def user_logout(request):
    request.session.clear()
    result = JsonResponse(code=Const['code.success'])
    result.delete_cookie('sessionid')
    return result


@admin_permission('normal')
def user_kickoff(r, uid):
    for s in Session.objects.all():
        data = s.get_decoded()
        if data.get('user_id', None) == uid:
            s.delete()
    return JsonResponse(code=Const['code.success'])


# def user_uploadimage(request, user_id):
#     form=ImageUploadForm(request.POST, request.FILES)
#     if form.is_valid():
#         image=request.FILES['image']
#         if(image.size>Const['file.max.size']):
#             return JsonResponse(code=Const['code.file.exceed.size'])
#         ftype=image.name[image.name.rindex('.')+1:].lower()
#         if(not ftype in ('jpg','png','jpeg')):
#             return JsonResponse(code=Const['code.image.unknown.type'])
#         fpath = '%d/' % user_id
#         fname='%d.%s' % (msec_time(),ftype)
#         fstorepath=os.path.join(LAIFU_IMAGE_DIR, fpath)
#         logger.debug('filename : %s' % fstorepath)
#         if not os.path.exists(fstorepath):
#             os.makedirs(fstorepath)
#         with open(fstorepath+fname, 'wb+') as destination:
#             for chunk in image.chunks():
#                 destination.write(chunk)
#         return JsonResponse(code=Const['code.success'],path='http://'+request.get_host()+\
#                             '/image/'+fpath+fname)
#     return JsonResponse(code=Const['code.request_error'])


@rest_permission
def user_setidc(request, user_id):
    user_id = int(user_id)
    user = get_object_or_404(User, pk=user_id)
    form = IdcForm(request.POST)
    if form.is_valid():
        user.idc_name = form.cleaned_data['idc_name']
        # user.idc_number = form.cleaned_data['idc_number']
        user.idc_photo = json.dumps([
            form.cleaned_data['idc_photo1'],
            form.cleaned_data['idc_photo2'],
        ])
        user.verify_status = Const['model.verify.need_check']
        user.save()
        return JsonResponse(code=Const['code.success'])
    return JsonResponse(code=Const['code.request_error'], errmsg=form.errors)


@rest_permission
def user_setphoto(request, user_id):
    u = User.objects.get(pk=user_id)
    u.photo = request.REQUEST['photo']
    u.save(update_fields=['photo'])
    # u.ry_info_refresh()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_createbankcard(request, user_id):
    form = BankcardForm(request.POST)
    if Bankcard.objects.filter(account_id=form.data['account_id']).count() > 0:
        return JsonResponse(code=Const['code.bankcard.repeat'])
    user = get_object_or_404(User, pk=user_id)
    if form.is_valid():
        bankcard = form.save(commit=False)
        bankcard.user_id = user_id
        bankcard.save()
        return JsonResponse(code=Const['code.success'], data=bankcard.to_dict())
    return JsonResponse(code=Const['code.request_error'], errmsg=form.errors)


@app_check
@rest_permission
def user_setqq(request, user_id):
    user_id = int(user_id)
    user = get_object_or_404(User, pk=user_id)
    qq = request.POST['qq']
    user.qq = qq
    user.save()
    return JsonResponse(code=Const['code.success'])


@app_check
@rest_permission
def user_createtbaccount(request, user_id):
    form = TBAccountForm(request.POST)
    user = User.objects.get(pk=user_id)
    # 等级一可以绑定两个账户
    if user.buyer_level == 1:
        if user.tbaccount_set.count() >= 2:
            return JsonResponse(code=Const['code.tbaccount.exceed'])
    # 其他等级绑定账户不能大于自身等级
    else:
        if user.tbaccount_set.count() >= user.buyer_level:
            return JsonResponse(code=Const['code.tbaccount.exceed'])

    if TBAccount.objects.filter(wangwang=form.data['wangwang']).count():
        return JsonResponse(code=Const['code.tbaccount.exist'])
    if form.is_valid():
        tbaccount = form.save(commit=False)
        tbaccount.user_id = user_id
        tbaccount.save()
        return JsonResponse(code=Const['code.success'], data=tbaccount.to_dict())
    return JsonResponse(code=Const['code.request_error'], errmsg=form.errors)


@app_check
@rest_permission
def user_listtbaccount(request, user_id):
    user_id = int(user_id)
    tbaccounts = TBAccount.objects.filter(user_id=user_id)
    tbaccounts = [tba.to_dict() for tba in tbaccounts]
    return JsonResponse(code=Const['code.success'], data=tbaccounts)


@app_check
@rest_permission
def user_listbankcard(r, mid):
    bankcards = Bankcard.objects.filter(user_id=mid)
    bankcards = [x.to_dict() for x in bankcards]
    return JsonResponse(code=Const['code.success'], data=bankcards)


@app_check
@rest_permission
def user_listbuyerorder(r, mid):
    order_type = int(r.REQUEST['order_type']) if 'order_type' in r.REQUEST else -1
    order_status = int(r.REQUEST['order_status']) if 'order_status' in r.REQUEST else 0
    logger.debug(order_status)
    start, num = get_paginator(r)
    # buyer = User.objects.get(pk=mid)
    sort_adv = False
    args = [Q(tb__user__id=mid), ]

    if order_type == 0:
        args.append(Q(order_type__in=(Const['model.order.type.flow'], Const['model.order.type.collect'])))
    elif order_type == 1:
        args.append(~Q(order_type__in=(Const['model.order.type.flow'], Const['model.order.type.collect'])))
        # else:
        # return JsonResponse(code=Const['code.request_error'])

    if order_status == 1:
        # 待操作
        args.append(Q(status__in=[
            Const['model.order.status.received'],
            Const['model.order.status.step1'],
            Const['model.order.status.step2'],
            # Const['model.order.status.step3'],
            Const['model.order.status.step9'],
            Const['model.order.status.step10'],
        ]))
    elif order_status == 3:
        args.append(Q(status=Const['model.order.status.completed']))
        # 待返款
    #        args.append(Q(status__in=[
    #                    Const['model.order.status.step3'],
    #                    Const['model.order.status.returnmoney'],
    #                    ]))
    elif order_status == 2:
        # 待评价
        args.append(Q(status=Const['model.order.status.deliver']))
    #                    Q(status__in=[
    #                    Const['model.order.status.deliver'],
    #                    Const['model.order.status.comment'],
    #                    Const['model.order.status.affirm'],
    #                    Const['model.order.status.completed'],
    #                    ]))
    else:
        sort_adv = True
        status_list = [
            Const['model.order.status.received'],
            Const['model.order.status.step1'],
            Const['model.order.status.step2'],
            Const['model.order.status.step3'],
            Const['model.order.status.step9'],
            Const['model.order.status.returnmoney'],
            Const['model.order.status.comment'],
            Const['model.order.status.deliver'],
            Const['model.order.status.affirm'],
        ]
        clauses = ' '.join(
                ['WHEN `tasks_order`.`status`=%s THEN %s' % (pk, 100 - i) for i, pk in enumerate(status_list)])
        ordering = 'CASE %s END' % clauses

        args.append(~Q(status__in=[Const['model.order.status.cancel'], ]))
    be15 = before15(15)
    if sort_adv:
        orders = Order.objects.filter(*args) \
                     .extra(select={'_ordering': ordering}, order_by=('-_ordering', 'receive_time')) \
                     .filter((Q(status=Const['model.order.status.completed']) & Q(update_time__gte=be15)) | \
                             ~Q(status=Const['model.order.status.completed']))[start:start + num]
    else:
        orders = Order.objects.filter(*args).filter((Q(status=Const['model.order.status.completed']) & \
                                                     Q(update_time__gte=be15)) | ~Q(
            status=Const['model.order.status.completed']))[start:start + num]
    # logger.info('user_listbuyerorder sql:%s'%orders.query)
    data = []
    for o in orders:
        data.append({
            'order_id': o.id,
            'frozen': o.frozen,
            'photo_url': json.loads(o.task.commodities)[0]['pic_path'],
            'date': o.receive_time,
            'pay': o.buyer_gain,
            'cost': o.dianzi(),
            'order_type': o.get_general_order_type(),
            'order_status': 1 if o.status == 108 else o.status,
            'return_type': o.task.return_type,
            'tb_wangwang': o.tb.wangwang if o.tb else '',
            'order_type2': o.order_type,
        })
    return JsonResponse(code=Const['code.success'], data=data)


@rest_permission
def user_lahei(r, uid):
    params = r.REQUEST
    u = User.objects.get(pk=uid)
    u.lahei(params['buyer_id'], params['reason'])
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_blackcancel(r, uid):
    Blacklist.objects.filter(seller_id=uid, buyer_id=r.REQUEST['buyer_id']).delete()
    return JsonResponse(code=Const['code.success'])


@app_check
@rest_permission
def user_listrecord(r, uid):
    start, num = get_paginator(r)
    return JsonResponse(code=Const['code.success'], data=[x.to_dict() for x in \
                                                          Record.objects.filter(user_id=uid, type=r.REQUEST['type'])[
                                                          start:start + num]])


@app_check
@rest_permission
@transaction.atomic
@mutex_lock
def bankcard_withdraw(r, bid):
    params = r.REQUEST
    bankcard = Bankcard.objects.get(pk=bid)
    user = bankcard.user
    if params['password'] != user.password:
        return JsonResponse(code=Const['code.password_error'])
    timestamp = msec_time() - 24 * Const['ms.per.hour']
    logger.info(timestamp)
    if Withdraw.objects.filter(bankcard_id=bid).filter(Q(verify_time__gte=timestamp) | Q(verify_time=None)).count() > 0:
        return JsonResponse(code=Const['code.request_error'], msg=u'距离上次提现成功小于24小时')
    amount = Decimal(params['amount'])
    if amount <= 0:
        return
    if 'type' in params and params['type'] == '0':
        ret = user.money_operatesafe(Const['model.record.pricipal'],
                                     -amount,
                                     '本金提现',
                                     Const['model.record.category.principalwithdraw'])
        rew = reward(amount, type=0)
        if ret < 0:
            return JsonResponse(code=Const['code.amount.exceed'], msg=u"余额不足")
        Withdraw.objects.create(bankcard=bankcard, amount=amount, reward=rew,
                                type=Const['model.withdraw.type.principal'])

    else:
        ret = user.money_operatesafe(Const['model.record.commission'],
                                     -amount,
                                     '佣金提现',
                                     Const['model.record.category.commissionwithdraw'])
        rew = reward(amount, type=1)
        if ret < 0:
            return JsonResponse(code=Const['code.amount.exceed'])
        Withdraw.objects.create(bankcard=bankcard, amount=amount, reward=rew,
                                type=Const['model.withdraw.type.commission'])
        # user.money_operate(Const['model.record.commission'],
        #                   -amount,
        #                   '佣金提现',
        #                   Const['model.record.category.commissionwithdraw'])
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_listappeal(r, uid):
    start, num = get_paginator(r)
    if r.REQUEST['type'] == '0':
        appeals = Appeal.objects.filter(complainant_id=uid).filter(order__tb__user__id=uid)[start:start + num]
    else:
        appeals = Appeal.objects.filter(respondent_id=uid).filter(order__tb__user__id=uid)[start:start + num]
    data = []
    for a in appeals:
        data.append(obj_to_dict(a, 'id', 'order_id',
                                'complainant_id', 'respondent_id', 'create_time',
                                'status', pics='get_pics', description='get_description',
                                complainant_qq='get_complainant_qq', respondent_qq='get_respondent_qq',
                                talks='get_talks', type='get_type'))
    return JsonResponse(code=Const['code.success'], data=data)


def user_getappeal(r, aid):
    appeal = Appeal.objects.get(pk=aid)
    data = obj_to_dict(appeal, 'id', 'order_id', 'complainant_id', 'finish', 'launch',
                       'respondent_id', 'create_time', 'status', 'order_cancel', pics='get_pics',
                       description='get_description', talks='get_talks', complainant_qq='get_complainant_qq',
                       respondent_qq='get_respondent_qq', type='get_type', task_pic_path='get_task_pic_path',
                       order_status='get_order_status')
    return JsonResponse(code=Const['code.success'], data=data)


@app_check
@rest_permission
def user_setimei(r, uid):
    if 'imei' not in r.REQUEST or r.REQUEST['imei'] is None or r.REQUEST['imei'] == '':
        logger.info(str(uid) + ' has no imei')
        return JsonResponse(code=Const['code.success'])
    user = User.objects.get(pk=uid)
    user.imei = r.REQUEST['imei']
    user.save(update_fields=['imei'])
    return JsonResponse(code=Const['code.success'])


def user_resetimei(r, uid):
    user = User.objects.get(pk=uid)
    user.imei = ""
    user.save(update_fields=['imei'])
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_getrytoken(request, uid):
    user = User.objects.get(pk=uid)
    token = user.ry_get_token();
    return JsonResponse(code=Const['code.success'],
                        data={'token': token})


def user_publicinfo(r, uid):
    try:
        user = User.objects.get(pk=uid);
    except Exception:
        return JsonResponse(code=Const['code.user.nonexists'])
    return JsonResponse(code=Const['code.success'], data=user.to_sub_dict('id', 'photo'))


@rest_permission
def user_award(r, uid):
    user = User.objects.get(pk=uid)
    now = msec_time()
    last = user.last_award_time
    if (not last) or (get_date_by_stamp(now) != get_date_by_stamp(last)):
        award = random.uniform(Const['min.award'], Const['max.award'])
        user.money_operate(Const['model.record.commission'], award, '签到奖励', Const['model.record.category.signup'])
        user.last_award_time = now
        user.save()
        return JsonResponse(code=Const['code.success'], data={'award': award})
    else:
        return JsonResponse(code=Const['code.award.already.receive'])


@admin_permission('normal')
def user_listidc(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, id='user_id', verify_status='verify_status')
    if 'register_start_time' in r.REQUEST:
        condition['register_time__gte'] = get_stamp_by_date(r.REQUEST['register_start_time'])
    users = User.objects.exclude(idc_name='').filter(**condition)[start:start + num]
    logger.debug(users.query)
    total = User.objects.exclude(idc_name='').filter(**condition).count()
    data = []
    for u in users:
        try:
            idcphotos = json.loads(u.idc_photo)
        except Exception:
            idcphotos = [None, None]
        data.append({
            'user_id': u.id,
            'register_time': u.register_time,
            'user_name': u.idc_name,
            'idc_photo1': idcphotos[0],
            'idc_photo2': idcphotos[1],
            'verify_status': u.verify_status,
        })
    return JsonResponse(code=Const['code.success'], data={'total': total,
                                                          'users': data})


@admin_permission('finance')
def user_listaccount(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, id='user_id')
    total = User.objects.filter(**condition).count()
    users = User.objects.filter(**condition)[start:start + num]
    data = []
    for u in users:
        data.append({'principal': u.principal, 'commission': u.commission,
                     'is_close_seller_return': u.is_close_sellerreturn,
                     'user_id': u.id})
    return JsonResponse(code=Const['code.success'], data={
        'total': total, 'users': data})


# 管理员拉黑某一个账号
@admin_permission('normal')
def user_adminlahei(r, uid):
    params = r.REQUEST
    u = User.objects.get(pk=uid)
    u.freeze(uid)
    return JsonResponse(code=Const['code.success'])


# 管理员拉黑某一个账号
@admin_permission('normal')
def user_2normal(r, uid):
    params = r.REQUEST
    u = User.objects.get(pk=uid)
    u.normalize_flags(uid)
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def tbaccount_list(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, user_id='user_id', status='verify_status')
    if 'register_start_time' in r.REQUEST:
        condition['user__register_time__gte'] = get_stamp_by_date(r.REQUEST['register_start_time'])
    tbs = TBAccount.objects.filter(**condition)[start:start + num]
    total = TBAccount.objects.filter(**condition).count()
    data = []
    for t in tbs:

        d = t.to_dict()
        try:
            pics = json.loads(t.pic_paths)
        except Exception:
            pics = [None, None]
        if not isinstance(pics, list):
            pics = [None, None]

        # 获取user的身份证姓名信息，如果没有提交，那么使用旺旺号码
        idc_name = t.user.idc_name
        if (idc_name):
            d['name'] = idc_name
        else:
            d['name'] = u'未绑定身份证--' + d['name']
        d['pic1'] = pics[0]
        d['pic2'] = pics[1]
        d['register_time'] = t.user.register_time
        d['tb_register_time'] = t.register_time  # 旺旺注册时间
        data.append(d)
    return JsonResponse(code='code.success', data={'total': total,
                                                   'tbaccounts': data})


@admin_permission('normal')
def bankcard_list(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, user_id='user_id', verify_status='verify_status')
    if 'register_start_time' in r.REQUEST:
        condition['user__register_time__gte'] = get_stamp_by_date(r.REQUEST['register_start_time'])
    bankcards = Bankcard.objects.filter(**condition)[start:start + num]
    total = Bankcard.objects.filter(**condition).count()
    data = []
    for b in bankcards:
        d = b.to_dict()
        d['register_time'] = b.user.register_time
        data.append(d)
    return JsonResponse(code='code.success', data={'total': total,
                                                   'bankcards': data})


@admin_permission('normal')
def record_list(r):
    start, num = get_paginator(r)
    condition = make_conditions(r, user_id='user_id',
                                start_time='start_time',
                                end_time='end_time')
    if 'start_time' in condition:
        condition['create_time__gte'] = get_stamp_by_date(condition['start_time'])
    if 'end_time' in condition:
        condition['create_time__lte'] = get_stamp_by_date(condition['end_time'])
    total = Record.objects.filter(**sub_dict(condition, 'user_id',
                                             'create_time__lte',
                                             'create_time__gte')).count()
    records = Record.objects.filter(**sub_dict(condition, 'user_id',
                                               'create_time__lte',
                                               'create_time__gte'))[start:start + num]
    return JsonResponse(code=Const['code.success'], data={'total': total,
                                                          'records': [re.to_dict() for re in records]})


@admin_permission('normal')
@mutex_lock
def user_verify(r, uid):
    user = User.objects.get(pk=uid)
    if obj_verify(r, user):
        user.notice_set(Const['model.remind.idc_verify'], True)  # 身份验证信息变更的通知
        # user.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
@mutex_lock
def bankcard_verify(r, bid):
    bankcard = Bankcard.objects.get(pk=bid)
    if obj_verify(r, bankcard):
        bankcard.user.notice_set(Const['model.remind.bankcard_verify'], True)  # 银行卡验证信息变更的通知
        # bankcard.user.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@admin_permission('normal')
@mutex_lock
def tbaccount_verify(r, tid):
    tb = TBAccount.objects.get(pk=tid)
    if obj_verify(r, tb, 'verify_status', 'status'):
        tb.user.notice_set(Const['model.remind.tb_verify'], True)
        # tb.user.save()
        return JsonResponse(code=Const['code.success'])
    else:
        return JsonResponse(code=Const['code.request_error'])


@app_check
@rest_permission
def tbaccount_modify(r, tid):
    conditions = make_conditions(r, wangwang='wangwang', name='name',phone='phone', city='city', address='address',
                                 pic_paths='pic_paths', register_time='register_time', gender='gender',
                                 age='age', is_credit_card_open='is_credit_card_open',
                                 wangwang_level='wangwang_level', is_huabei_open='is_huabei_open')
    tbs = TBAccount.objects.filter(wangwang=conditions['wangwang'])
    if len(tbs) > 0 and tbs[0].id != tid:
        return JsonResponse(code=Const['code.tbaccount.exist'])
    tbaccount = TBAccount.objects.get(pk=tid)
    for key in conditions:
        setattr(tbaccount, key, conditions[key])
    tbaccount.status = Const['model.verify.need_check']
    tbaccount.save()
    return JsonResponse(code=Const['code.success'])

@app_check
@rest_permission
def bankcard_modify(r, bid):
    conditions = make_conditions(r, bank_name='bank_name', bank_city='bank_city', bank_province='bank_province',
                                 bank_district='bank_district', owner_name='owner_name', account_id='account_id',
                                 account_name='account_name')
    bks = Bankcard.objects.filter(account_id=conditions['account_id'])
    if len(bks) > 0 and bks[0].id != bid:
        return JsonResponse(code=Const['code.bankcard.repeat'])
    bankcard = Bankcard.objects.get(pk=bid)
    for key in conditions:
        setattr(bankcard, key, conditions[key])
    bankcard.verify_status = Const['model.verify.need_check']
    bankcard.save()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_startprivatechat(r, uid):
    buyer_id = r.REQUEST['buyer_id']
    return render(r, 'messages.html', locals())


@admin_permission('normal')
def user_setbuyerlevel(r, uid):
    u = User.objects.get(pk=uid)
    level = int(r.REQUEST['level'])
    if level < 1 or level > 6:
        return JsonResponse(code=Const['code.request_error'])
    u.buyer_level = level
    u.save()
    return JsonResponse(code=Const['code.success'])


@admin_permission('normal')
def user_list(r):
    start, num = get_paginator(r)
    conditions = make_conditions(r, pk='user_id', phone='phone', qq='qq', buyer_level='buyer_level',
                                 register_time='register_time')
    if 'register_time' in conditions:
        conditions['register_time'] = get_stamp_by_date(conditions['register_time'])
    total = User.objects.filter(**conditions).count()
    users = User.objects.filter(**conditions)[start:start + num]
    data = []
    for u in users:
        try:
            idcphotos = json.loads(u.idc_photo)
        except Exception:
            idcphotos = [None, None]
        data.append({
            'id': u.id,
            'register_time': u.register_time,
            'user_name': u.idc_name,
            'phone': u.phone,
            'qq': u.qq,
            'buyer_level': u.buyer_level,
            'seller_level': u.seller_level,
            'idc_photo1': idcphotos[0],
            'idc_photo2': idcphotos[1],
            'verify_status': u.verify_status,
            'principal': u.principal,
            'commission': u.commission,
            'flags': u.flag_dump(),
        })
    return JsonResponse(code=Const['code.success'], data={'total': total, 'users': data})


@admin_permission('normal')
def user_updateflag(r, uid):
    index = int(r.REQUEST['index'])
    value = True if int(r.REQUEST['value']) == 1 else False
    user = User.objects.get(pk=uid)
    user.flag_set(index, value)
    user.save()
    return JsonResponse(code=Const['code.success'])


@rest_permission
def user_exportorders(r, uid):
    conditions = make_conditions(r, task__store_id='store_id', tb__wangwang='buyer_wangwang', task_id='task_id',
                                 tb__user_id='buyer_id', order_type='order_type')
    params = r.REQUEST
    conditions['task__store__user_id'] = uid
    if 'receive_start' in params:
        conditions['receive_time__gte'] = get_stamp_by_date(params['receive_start'])
    if 'receive_end' in params:
        conditions['receive_time__lte'] = get_stamp_by_date(params['receive_end'])
    if 'order_status' in params:
        if params['order_status'] == '1':
            conditions['status__in'] = [
                Const['model.order.status.received'],
                Const['model.order.status.step1'],
                Const['model.order.status.step2'],
                Const['model.order.status.step9']]
        elif params['order_status'] == '2':
            conditions['status__in'] = [Const['model.order.status.step3'], Const['model.order.status.returnmoney']]
        elif params['order_status'] == '3':
            conditions['status'] = Const['model.order.status.deliver']
        elif params['order_status'] == '4':
            conditions['status'] = Const['model.order.status.comment']
        elif params['order_status'] == '5':
            conditions['status'] = Const['model.order.status.completed']

    if 'o_type' in params:
        if params['o_type'] == 'flow':
            conditions['order_type__in'] = [
                Const['model.order.type.flow'],
                Const['model.order.type.collect']
            ]
        elif params['o_type'] == 'buy_order':
            conditions['order_type__in'] = [
                0, 1, 2, 5, 6
            ]

    orders = Order.objects.exclude(
        status__in=[Const['model.order.status.init'], Const['model.order.status.cancel']]).filter(**conditions)
    logger.debug(orders.query)
    data = []
    for o in orders:
        t = o.task
        bk = o.bankcard
        commodities = json.loads(t.commodities)
        search_entry = json.loads(t.search_entries)[o.search_entry_index] if o.search_entry_index >= 0 else None
        bc = o.get_buyer_commit()
        sc = o.get_seller_commit()
        data.append({
            'order_id': o.id,
            'receive_time': get_datetime_by_stamp(o.receive_time),
            'buyer_id': o.tb.user_id,
            'buyer_wangwang': o.tb.wangwang,
            'task_type': o.get_display_type(),
            'order_status': o.get_display_status(),
            'total_price': t.total_price,
            'buyer_commit': bc if bc else '',
            'seller_commit': sc if sc else '',
            'store_name': t.store.name,
            'commodity_name': commodities[0]['name'],
            'search_keyword': search_entry['keyword'] if search_entry else '',
            'bk_name': bk.owner_name if bk else '',
            'bk_bank': bk.bank_name if bk else '',
            'bk_account': bk.account_id if bk else '',
            'bk_city': bk.bank_city if bk else '',
            'bk_zh': bk.account_name if bk else '',
            'order_all_pay': o.seller_payment,
        })
    return CsvResponse({
        'order_id': u'订单ID',
        'receive_time': u'接单时间',
        'buyer_id': u'买手ID',
        'buyer_wangwang': u'买手旺旺',
        'task_type': u'订单类型',
        'order_status': u'订单状态',
        'total_price': u'商家要求垫付金额',
        'buyer_commit': u'买手实际垫付金额',
        'seller_commit': u'商家实际返款金额',
        'store_name': u'店铺名',
        'commodity_name': u'商品名',
        'search_keyword': u'搜索关键词',
        'bk_name': u'返款人姓名',
        'bk_bank': u'返款银行名',
        'bk_account': u'返款账户',
        'bk_city': u'返款银行所在地',
        'bk_zh': u'返款银行支行',
        'order_all_pay': u'商家支付总额（包括佣金）',
    }, data)


@rest_permission
def user_capitalrecordexport(r, uid):
    conditions = make_conditions(r)
    conditions['user_id'] = uid
    params = r.REQUEST
    if 'create_time_start' in params or 'create_time_end' in params:
        if 'create_time_start' in params:
            conditions['create_time__gte'] = get_stamp_by_date(params['create_time_start'])
        if 'create_time_end' in params:
            conditions['create_time__lte'] = get_stamp_by_date(params['create_time_end'])
    else:
        conditions['create_time__gte'] = 0

    if 'capital_type' in params:
        if int(params['capital_type']) == 0:
            conditions['amount__lte'] = 0.0
        elif int(params['capital_type']) == 1:
            conditions['amount__gte'] = 0.0
    query = Record.objects.filter(**conditions)
    data = []
    for o in query:
        data.append({
            'time': get_datetime_by_stamp(o.create_time),
            'type': u'收入' if o.is_income() else u'支出',
            'content': o.description,
            'amount': o.amount,
        })
    return CsvResponse({
        'time': u'时间',
        'type': u'收支类型',
        'content': u'描述',
        'amount': u'金额',
    }, data)
