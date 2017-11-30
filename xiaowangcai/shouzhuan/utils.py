# encoding: utf-8
import logging
import cStringIO
import codecs
import csv
import datetime
import hashlib
import json
from random import randint
import time
from django.utils.timezone import now, timedelta
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse

from shouzhuan.const import Const
from shouzhuan import version

logger = logging.getLogger(__name__)


def md5_32(a):
    m = hashlib.md5()   
    m.update(a)
    return m.hexdigest()


def md5_16(a):
    return md5_32(a)[8:-8]


def JsonResponse(**kwarg):
    kwarg['version'] = version.RestVersion
    return HttpResponse(json.dumps(kwarg, cls=DjangoJSONEncoder), content_type="application/json")


def make_conditions(request, **kwargs):
    conditions = {}
    for k, v in kwargs.items():
        if v in request.REQUEST and request.REQUEST[v]:
            conditions[k] = request.REQUEST[v]
    return conditions


def get_paginator(request):
    start = 0
    if 'start' in request.REQUEST and request.REQUEST['start']:
        start = int(request.REQUEST['start'])
    start = 0 if start < 0 else start
    num = Const['paginator.num']
    if 'num' in request.REQUEST and request.REQUEST['num']:
        num = int(request.REQUEST['num'])
    num = 0 if num < 0 else num
    if not ('format' in request.REQUEST):
        num = 100 if num > 100 else num
    return start, num


def sub_dict(d, *keys):  
    return dict([(k, d.get(k)) for k in keys if ((k in d) and d[k])])


def sub_dict2(d, *keys):  
    return dict([(k, d.get(k)) for k in keys if k in d])


def del_dict_keys(d, *keys):
    nd = d.copy()
    [nd.pop(k) for k in keys if k in nd]
    return nd


def add_dict_key(d, **args):
    nd = d.copy()
    for k, v in args.items():
        if k in nd:
            raise Exception('key duplicated')
        else:
            nd[k] = v
    return nd


def msec_time():
    return int(time.time()*1000)


def get_date_by_stamp(timestamp):
    return time.strftime('%Y-%m-%d', time.localtime(timestamp/1000))


def get_datetime_by_stamp(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp/1000))


def get_stamp_by_date(datestr):
    return int(time.mktime(datetime.datetime(*[int(x) for x in datestr.split('-')]).timetuple())*1000)


def get_stamp_by_datetime(dt):
    return int(time.mktime(dt.timetuple()) * 1000)


def get_commision_level(money):
    if money < 0:
        return -1
    elif money < 50:
        return 0
    elif money < 100:
        return 1
    elif money < 150:
        return 2
    elif money < 300:
        return 3
    elif money < 500:
        return 4
    elif money < 800:
        return 5
    elif money < 1000:
        return 6
    elif money < 1200:
        return 7
    elif money < 1500:
        return 8
    elif money < 2000:
        return 9
    elif money < 2500:
        return 10
    elif money < 3000:
        return 11
    elif money < 3500:
        return 12
    elif money < 4000:
        return 13
    elif money < 4500:
        return 14
    elif money < 5000:
        return 15
    elif money < 6000:
        return 16
    elif money < 7000:
        return 17
    elif money < 8000:
        return 18
    else:
        return -1


def fix_length_random_int(fixlength):
    return randint(10**(fixlength-1), 10**fixlength-1)


def obj_to_dict(o, *lkeys, **dkeys):
    res = {}
    for key in lkeys:
        if callable(getattr(o, key)):
            res[key] = getattr(o, key)()
        else:
            res[key] = getattr(o, key)
    for key in dkeys:
        okey = dkeys[key]
        if callable(getattr(o, okey)):
            res[key] = getattr(o, okey)()
        else:
            res[key] = getattr(o, okey)
    return res


def obj_verify(r, obj, args_name='verify_status', verify_status='verify_status',
               verify_admin_id='verify_admin_id', verify_time='verify_time', **others):
    # if getattr(obj, verify_status)==Const['model.verify.need_check']:
    if True:
        setattr(obj, verify_status, r.REQUEST[args_name])
        if hasattr(obj, verify_admin_id):
            setattr(obj, verify_admin_id, r.admin_id)
        if hasattr(obj, verify_time):
            setattr(obj, verify_time, msec_time())
        for k in others:
            if hasattr(obj, k):
                setattr(obj, k, others[k])
        obj.save()
        return True
    return False


def obj_verify_strict(r, obj, args_name='verify_status', verify_status='verify_status',
                      verify_admin_id='verify_admin_id', verify_time='verify_time', **others):
    if getattr(obj, verify_status) == Const['model.verify.need_check']:
        setattr(obj, verify_status, r.REQUEST[args_name])
        if hasattr(obj, verify_admin_id):
            setattr(obj, verify_admin_id, r.admin_id)
        if hasattr(obj, verify_time):
            setattr(obj, verify_time, msec_time())
        for k in others:
            if hasattr(obj, k):
                setattr(obj, k, others[k])
        obj.save()
        return True
    return False


def obj_modify(obj, dic):
    for key in dic:
        if hasattr(obj, key):
            setattr(obj, key, dic[key])


def mapred(collection, map_func, red_func):
    reduce(red_func, map(map_func, collection))


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def CsvResponse(metas, datas, fname='output.csv'):
    response = HttpResponse(content_type='text/csv')
    response.write(codecs.BOM_UTF8)
    response['Content-Disposition'] = 'attachment; filename="%s"' % fname
    writer = UnicodeWriter(response)
    (labels, cells) = meta_format(metas)
    writer.writerow(labels)
    for row in datas:
        writer.writerow(data_format(cells, row))
    return response


def meta_format(metas):
    labels = []
    cells = []
    for m in metas:
        cells.append(m)
        labels.append(metas[m])
    return labels, cells


def data_format(cells, row):
    result = []
    for c in cells:
        result.append(unicode(row.get(c, '')))
    return result


def protect_storename(rawname):
    if rawname is None or len(rawname) == 0:
        return rawname
    if len(rawname) <= 3:
        return rawname[0:1]+u"**"
    else:
        # mask=u"********************************"
        return '*' + rawname[1:len(rawname) - 1] + '*'
    # return rawname


def bitflag_has(raw, index):
    return bool((raw >> index) & 1)


def bitflag_set(raw, index, value):
    if value is True:
        return raw | (1 << index)
    return raw & (~(1 << index))


def bitflag_dump(raw):
    data = {}
    for x in range(0, 62):
        data['f_' + str(x)] = bitflag_has(raw, x)
    return data

def before15(day):
    before = now().date() + timedelta(days=-day)
    return int(time.mktime(before.timetuple())*1000)   # 15天前的时间戳

# 本金、佣金奖励
def reward(amount, type):
    if type == 0:
        if amount < 200:
#             reward = amount - 3 原来是提现手续费
            reward = amount - 0 #现在不收取了
            return reward
        else:
            reward = amount
            return reward
    else:
        if amount == 50:
            reward = 50 #原来是48的，现在改为50，不再收取2元的手续费
        elif amount == 100:
            reward = 100
        else:
            reward = amount #amount + amount/100 去掉原来的奖励
        return reward

#把资金全部转化为角，小数点一位的规范
def to1point(val):
    intVal =  val*10
    tempVal = int(intVal)
    frontVal = tempVal - tempVal%10
    afterVal = (tempVal%10)*0.1
    return frontVal/10 + afterVal
