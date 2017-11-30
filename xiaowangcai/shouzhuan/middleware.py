# encoding: utf-8
import logging
import traceback

from shouzhuan.utils import JsonResponse

from shouzhuan.const import Const, device_constraint
from system.models import RequestLog

logger=logging.getLogger(__name__)

class ExceptionLogging():
    def process_exception(self,r,e):
        logging.exception('url:%s'%r.path)

class WsgiLogErrors(object):
    def process_exception(self, request, exception):
        tb_text = traceback.format_exc()
        url = request.build_absolute_uri()
        request.META['wsgi.errors'].write(url + '\n' + str(tb_text) + '\n')


class SetRequestDevice():
    def process_request(self, request):
        request.c_version = ''
        request.c_versioncode = 0
        request.c_type = Const['model.device.unknown']
        request.c_userid = 0
        if request.path.startswith('/rest'):
            useragent=''
            try:
                useragent=request.META['HTTP_USER_AGENT']
            except KeyError:
                pass
            try:
                if request.path.startswith('/rest_web/'):
                    request.c_type = Const['model.device.pc']
                    request.c_versioncode=1;
                else:
                    clienttype=request.META['HTTP_X_REQUEST_CLIENT']
                    #logger.info('client(%s) url:%s'%(clienttype,request.path))
                    arr = clienttype.split(';')
                    request.c_version = arr[2]
                    request.c_versioncode = int(arr[1])
                    if arr[0] == 'Android':
                        request.c_type = Const['model.device.android']
                    elif arr[0] == 'iOS':
                        request.c_type = Const['model.device.ios']
            except KeyError, e:
                #print e
                pass
            except Exception, e1:
                logger.error('process_request exception %s'%e1)
                pass
            # 这个日志太多了也没啥用
            # RequestLog.objects.create(url=request.path, c_type=request.c_type,\
            #     c_version=request.c_version, c_versioncode=request.c_versioncode, useragent=useragent)
            if request.c_type==0:
                # 个人任务列表+签到奖励+可接任务列表 屏蔽 低版本
                if (useragent == None or useragent == '' \
                    or (useragent != None and useragent != '' and not useragent.startswith('tbTasker/'))) \
                and (request.path.startswith('/rest/tasks/order/listavaliable') \
                or request.path.startswith('/rest/users/user/award/') \
                or request.path.startswith('/rest/users/user/listbuyerorder/')) :
                    return JsonResponse(code=Const['code.global.client_unsupport'])
                # ios 低版本屏蔽所有接口
                if useragent != None and useragent != '' and useragent.startswith('tbTasker/'):
                    return JsonResponse(code=Const['code.global.client_unsupport'])
            elif request.c_type==1 and request.c_versioncode < 28\
            and (request.path.startswith('/rest/tasks/order/listavaliable') \
                or request.path.startswith('/rest/users/user/award/') \
                or request.path.startswith('/rest/users/user/listbuyerorder/') \
                or request.path.startswith('/rest/users/user/login')):
            #低于28的版本+屏蔽登录接口
                return JsonResponse(code=Const['code.global.client_unsupport'])
        return None
