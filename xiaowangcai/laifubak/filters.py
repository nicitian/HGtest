# encoding: utf-8
import functools
import logging
import threading

from django.shortcuts import redirect

from laifu.const import Const
from laifu.utils import JsonResponse
from tasks.models import Store, Task, Order, Appeal
from users.models import TBAccount, Bankcard
from management.models import Administrator
from laifu.settings import DEBUG
from users.models import User

logger=logging.getLogger(__name__)

#登陆验证器
def need_login(f):
    @functools.wraps(f)
    def inner(request,*args,**kwarg):
        if 'user_id' in request.session:
            return f(request,*args,**kwarg)
        else:
            if request.path.startswith('/rest'):
                return JsonResponse(code=Const['code.permission_deny'])
            else:
                return redirect('/login')
    return inner


#user_id验证
def userid_check(f):
    
    @functools.wraps(f)
    def inner(request,*args,**kwarg):
        logger.debug('request user_id verify: uid=%s  s_uid=%s'%(request.REQUEST['user_id'],\
                                                                   request.session['user_id']))
        if int(request.REQUEST['user_id']) == request.session['user_id']:
            return f(request,*args,**kwarg)
        else:
            if request.path.startswith('/rest'):
                return JsonResponse(code=Const['code.permission_deny'])
            else:
                return redirect('/login')
    return inner

def get_store_user_id(store_id):
    return Store.objects.get(pk=store_id).user_id

def get_tb_user_id(tb_id):
    return TBAccount.objects.get(pk=tb_id).user_id

def get_task_store_id(task_id):
    return Task.objects.get(pk=task_id).store_id

def get_order_seller_id(order_id):
    return Order.objects.get(pk=order_id).task.store.user_id

def get_order_buyer_id(order_id):
    return Order.objects.get(pk=order_id).tb.user_id

def get_in_request(request,key):
    return request.REQUEST[key] if key in request.REQUEST else ''
    
def user_permission_check(request,action,mid,s_uid,s_aid):
    if mid==s_uid:
        return True
    return False

def bankcard_permission_check(request,action,mid,s_uid,s_aid):
    if Bankcard.objects.get(pk=mid).user_id==s_uid:
        return True
    return False

def tbaccount_permission_check(request,action,mid,s_uid,s_aid):
    if TBAccount.objects.get(pk=mid).user_id==s_uid:
        return True
    return False

def store_permission_check(request,action,mid,s_uid,s_aid):
    if mid>0:
        if get_store_user_id(mid)==s_uid:
            return True
    else:
        if get_in_request(request,'user_id') and int(get_in_request(request,'user_id'))==s_uid:
            return True
    return False

def task_permission_check(request,action,mid,s_uid,s_aid):
    if mid>0:
        if(get_store_user_id(get_task_store_id(mid))==s_uid):
            return True
    else:
        if get_in_request(request,'store_id'):
            sid=int(get_in_request(request,'store_id'))
            tid=get_in_request(request,'id')
            if tid:
                if  Task.objects.get(pk=tid).store_id!=sid:
                    return False
            if get_store_user_id(sid)==s_uid and Store.objects.get(pk=sid).verify_status==Const['model.verify.check_pass']:
                return True
    return False

def order_permission_check(request,action,mid,s_uid,s_aid):
    if mid>0:
        if action in ('get','detailbyapp','applyappeal','cancel'): #公共操作
            if get_order_seller_id(mid)==s_uid or get_order_buyer_id(mid)==s_uid :
                return True
        elif action in ('receive','operate', 'operategroup','comment'): #买手操作
            order=Order.objects.get(pk=mid)
            if order.tb :
                #已接单
                if order.tb.user_id==s_uid:
                    return True
            else :
                #未接单
                if get_tb_user_id(request.REQUEST['tb_id'])==s_uid:
                    return True
        else:  #商家操作
            if get_order_seller_id(mid)==s_uid :
                return True
    else:
        if get_in_request(request,'user_id') and int(get_in_request(request,'user_id'))==s_uid:
            return True
        if get_in_request(request,'tb_id') :
            tid=int(get_in_request(request,'tb_id'))
            if get_tb_user_id(tid)==s_uid :
                return True
    return False

def appeal_permission_check(request,action,mid,s_uid,s_aid):
    if mid>0:
        if action in ('finish',): #申诉人
            if Appeal.objects.get(pk=mid).complainant_id==s_uid:
                return True
        else: #公共
            if s_aid > 0:
                return True
            appeal=Appeal.objects.get(pk=mid)
            if appeal.complainant_id==s_uid or \
                appeal.respondent_id==s_uid:
                return True
    return False

#异步接口权限控制
def rest_permission(f):
    
    @functools.wraps(f)
    def inner(request,*args,**kwarg):
        url=request.path
        request.c_userid = int(request.session['user_id']) if 'user_id' in request.session else -1
#         if not ('user_id' in request.session):
#             return JsonResponse(code=Const['code.permission_deny'])
        s_uid=int(request.session['user_id']) if 'user_id' in request.session else -1
        s_aid=int(request.session['admin_id']) if 'admin_id' in request.session else -1
        user = User.objects.get(pk=s_uid)
        if user.is_freezed():
            return JsonResponse(code=Const['code.permission_deny'])
        parts=url.split('/')
        model=parts[3]
        action=parts[4]
        mid=int(parts[5]) if len(parts)==6 else -1
        logger.debug('session user:%d, model:%s, action:%s, mid:%d '%(s_uid,model,action,mid))
        if eval('%s_permission_check(request,action,mid,s_uid,s_aid)' % model):
            return f(request,*args,**kwarg)
        else:
            return JsonResponse(code=Const['code.permission_deny'])

    return inner

#web权限控制
def web_permission(model,action):
     
    def _deco(f):
        
        @functools.wraps(f) 
        def inner(request,*args,**kwarg):
            if not ('user_id' in request.session):
                return redirect('/')
            s_uid=int(request.session['user_id'])
            s_aid=int(request.session['admin_id']) if 'admin_id' in \
                    request.session else -1
            user = User.objects.get(pk=s_uid)
            if user.is_freezed():
                return redirect('/login')
            mid_key=model+'_id'
            mid=int(request.REQUEST[mid_key]) if mid_key in request.REQUEST else -1
            ok=False
            logger.debug('session user:%d, model:%s, action:%s, mid:%d , s_aid:%d'%(s_uid,model,action,mid,s_aid))
            if eval('%s_permission_check(request,action,mid,s_uid,s_aid)' % model):
                return f(request,*args,**kwarg)
            else:
                return redirect('/login')
        return inner
    return _deco

mutex_locks=[]
for i in range(Const['total.lock.number']):
    mutex_locks.append(threading.Lock())

def mutex_lock(*names):
    def _deco(f):
        @functools.wraps(f) 
        def inner(request,*args,**kwarg):
            mutex_sign_list=[request.path[::-1],]
            if not (len(names)==1 and callable(names[0])):
                for name in names:
                    mutex_sign_list.append(request.REQUEST[name])
            mutex_sign='@'.join(mutex_sign_list)
            lock_number=hash(mutex_sign)%Const['total.lock.number']
            logger.debug('mutex_sign : %s ; lock number : %d'%(mutex_sign,lock_number))
            with mutex_locks[lock_number]:
                return f(request,*args,**kwarg)
        return inner
    if len(names)==1 and callable(names[0]):
        return _deco(names[0])
    else:
        return _deco
    
def admin_permission(ptype):
    def _deco(f):
        @functools.wraps(f) 
        def inner(request,*args,**kwarg):
            if not 'admin_id' in request.session:
                return JsonResponse(code=Const['code.permission_deny'])
            aid=int(request.session['admin_id'])
            admin=Administrator.objects.get(pk=aid)
            if getattr(admin, ptype+'_permission'):
                request.admin_id=aid
                return f(request,*args,**kwarg)
            else:
                return JsonResponse(code=Const['code.permission_deny'])
        return inner
    return _deco
