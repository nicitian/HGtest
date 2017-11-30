# coding=utf-8
import urllib
import urlparse

from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

from shouzhuan.filters import admin_permission
from shouzhuan.utils import *
from others.models import *
from django.shortcuts import render
import urllib2
from bs4 import BeautifulSoup
import requests
# from django.http import JsonResponse

logger = logging.getLogger(__name__)


@admin_permission('normal')
def dailyreport_summary(r):
    params = r.REQUEST
    cursor = connection.cursor()
    cursor.execute('''select type,sum(value),sum(amount)
                    from others_dailyreport
                    where date>='%s' and date<='%s'
                    group by type'''
                   % (params['start_date'], params['end_date']))
    rows = cursor.fetchall()
    data = [{'type': r[0], 'value': r[1] if r[1] != None else r[2]} for r in rows]
    return JsonResponse(code=Const['code.success'], data=data)


# 后台管理
def tkgoods_manager(r):
    start, num = get_paginator(r)
    conditions = make_conditions(r, title__contains='title')
    total = TkGoods.objects.filter(**conditions).count()
    tkgoods = TkGoods.objects.filter(**conditions)[start:start + num]
    data = []
    if tkgoods and tkgoods.count() > 0:
        data.extend(trans_tkgoods_obj_to_dict(x) for x in tkgoods)
    return JsonResponse(code=Const['code.success'], data={'total': total, 'tkgoods': data})


def tk_edit(r):
    tkg_id = r.REQUEST.get('id')
    if tkg_id:
        tkg = TkGoods.objects.get(id=tkg_id)
        tkg = trans_tkgoods_obj_to_dict(tkg)
        return render(r, "admin/tk_edit.html", {'tkg': tkg})
    else:
        return render(r, "admin/tk_edit.html")


def tkgoods_save(r):
    try:
        tkg_id = r.REQUEST['id']
        if tkg_id:
            # 修改商品
            tkg = TkGoods.objects.get(id=tkg_id)
        else:
            # 新增商品
            tkg = TkGoods()
        tkg.c_id = r.REQUEST['cid']
        tkg.title = r.REQUEST['title']
        tkg.d_title = r.REQUEST['d_title']
        tkg.pic = r.REQUEST['pic']
        tkg.price = r.REQUEST['price']
        tkg.link = r.REQUEST['link']
        tkg.is_tmall = r.REQUEST['is_tmall']
        tkg.quan_price = r.REQUEST['quan_price']
        tkg.quan_time = r.REQUEST['quan_time']
        tkg.quan_link = r.REQUEST['quan_link']
        tkg.save()
        return JsonResponse(code=Const['code.success'])
    except Exception as ex:
        print str(ex)
        return JsonResponse(code=Const['code.system_error'], msg='系统错误')
#
# def goods_add(request):
#     print request.POST.get('goods_id', '')
#     print request.POST.get('title', '')
#     print request.POST.get('d_title', '')
#     print request.POST.get('pic', '')
#     print request.POST.get('price', '')
#     print request.POST.get('link', '')
#     print request.POST.get('is_tmall', '')
#     print request.POST.get('quan_price', '')
#     print request.POST.get('quan_time', '')
#     print request.POST.get('quan_link', '')
#     if request.method == 'POST':
#         try:
#             tkg = TkGoods()
#             tkg.goods_id = request.POST.get('goods_id', '')
#             tkg.title = request.POST.get('title', '')
#             tkg.d_title = request.POST.get('d_title', '')
#             tkg.pic = request.POST.get('pic', '')
#             tkg.price = request.POST.get('price', '')
#             tkg.link = request.POST.get('link', '')
#             tkg.is_tmall = request.POST.get('is_tmall', '')
#             tkg.quan_price = request.POST.get('quan_price', '')
#             tkg.quan_time = request.POST.get('quan_time', '')
#             tkg.quan_link = request.POST.get('quan_link', '')
#             tkg.save()
#             return JsonResponse(code=Const['code.success'])
#         except Exception as ex:
#             print str(ex)
#             return JsonResponse(code=Const['code.system_error'], msg='系统错误')
#     else:
#         return JsonResponse(code=Const['code.system_error'], msg='不支持的请求')

def tkgoods_delete(r):
    tkg_id = r.REQUEST['id']
    TkGoods.objects.get(id=tkg_id).delete()
    return JsonResponse(code=Const['code.success'])


# 淘客商品列表用于APP
def tkgoods_list(r):
    page = r.REQUEST.get('page', default=1)
    search = r.REQUEST.get('search', default='')
    cid = r.REQUEST.get('cid', default='')
    page_size = 10
    tkgoods = TkGoods.objects.all()
    if search:
        tkgoods = tkgoods.filter(title__contains=search)
    if cid:
        tkgoods = tkgoods.filter(c_id=cid)
    print tkgoods.query
    total_count, total_page, count, pages, query_result = fen_ye(int(page), page_size, tkgoods)
    data = []
    if tkgoods and tkgoods.count() > 0:
        data.extend(trans_tkgoods_obj_to_dict(x) for x in query_result)
    if cid:
        tkad = TkAd.objects.get(cid=cid)
    else:
        tkad = TkAd.objects.get(cid=0)
    tkad = trans_tkad_obj_to_dict(tkad)
    result = {'pages': pages, 'page_size': page_size, 'total_count': total_count, 'total_page': total_page,
              'page': int(page), 'tkgoods': data, 'search': search, 'tkad': tkad}

    return JsonResponse(code=Const['code.success'], data=result)


# 淘客商品h5页面 - 已弃用
def mb_tkgoods(r):
    page = r.REQUEST.get('page', default=1)
    search = r.REQUEST.get('search', default='')
    page_size = 100
    tkgoods = TkGoods.objects.all()
    if search:
        tkgoods = tkgoods.filter(title__contains=search)
    print tkgoods.query
    total_count, total_page, count, pages, query_result = fen_ye(int(page), page_size, tkgoods)
    data = []
    if tkgoods and tkgoods.count() > 0:
        data.extend(trans_tkgoods_obj_to_dict(x) for x in query_result)
    result = {'pages': pages, 'page_size': page_size, 'total_count': total_count, 'total_page': total_page,
              'page': int(page), 'tkgoods': data, 'search': search}
    return render(r, 'mobile/tkgoods.html', result)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Host': 'www.dataoke.com',
    'Origin': 'http://www.dataoke.com',
    'Referer': 'http://www.dataoke.com/qlist',
    'Pragma': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
}

# 将短链接转换成需要的pid
def get_pid_from_taobao(url):
    import requests
    _refer = requests.get(url).url
    headers = {'Referer': _refer}
    try:
        pid = requests.get(urllib.unquote(_refer.split('tu=')[1]), headers=headers).url.split('&ali_trackid=2:mm_44014112_4618069_22288428:')[1][0:25]
        print pid
        return pid
    except Exception as e:
        return 'mm_44014112_4618069_22288428'

# 大淘客定时任务添加商品
def dtk_addgoods(r):
    import time
    try:
        pid = 'mm_44014112_4618069_22288428'
        dtk_key = '2p1jfc2ytc'
        # 自动加入推广
        try:
            r = requests.get('http://www.dataoke.com/login')
            _cookies = r.cookies
            s = requests.session()
            login_url = "http://www.dataoke.com/loginApi"  # 大淘客登录地址
            status_url = "http://www.dataoke.com/userisfor"     # 获取商品已加入推广ID列表（调用失败）
            add_quan_url = 'http://www.dataoke.com/handle_popularize'   # 加入推广地址
            login_data = {"username": "262374276@qq.com", "password": "7758258O", "ref": ""}
            print '开始登录'
            login_res = s.post(login_url, data=login_data, headers=headers, cookies=_cookies)  # 发送登录信息，返回响应信息（包含cookie）
            print '登录返回信息： ' + login_res.content
            status_res = s.post(status_url, cookies=login_res.cookies, headers=headers)
            content = json.loads(status_res.content)
            print '获取已加入推广列表：'
            print content['msg']
            print status_res.content
            start_time = datetime.datetime.now()
            print '开始加入推广:' + str(start_time)
            for page in xrange(1, 21):
                print '开始加入第' + str(page) + '页'
                list_url = 'http://www.dataoke.com/qlist?page=' + str(page)
                list_response = s.get(list_url, cookies=login_res.cookies, headers=headers)
                soup = BeautifulSoup(list_response.content, 'html.parser')
                for tag in soup.find_all('span', class_='fl quan_add_u go_info'):
                    data_id = tag['data-gid']
                    if id:
                        add_quan_data = {
                            'act': 'add_quan',
                            'id': data_id,
                        }
                        add_quan_res = s.post(add_quan_url, data=add_quan_data, cookies=login_res.cookies, headers=headers)
                        # 如果返回结果为is_in,表示取消了加入推广，再次请求加入推广
                        if add_quan_res.content == 'is_in':
                            s.post(add_quan_url, data=add_quan_data, cookies=login_res.cookies, headers=headers)

            tuiguang_end_time = datetime.datetime.now()
            print '加入推广结束：' + str(tuiguang_end_time)
            print '加入推广花费时间：' + str(tuiguang_end_time - start_time)
        except Exception as e:
            print '添加推广商品异常'+ str(e)

        # 获取淘口令token
        token = '03c0cfee5256de1f4f2a14fd4d5a3dc6'
        req_url = 'http://niuluyang.51sql.cn/api/getkl.php'
        text = '活动多多，惊喜多多'
        # 将tkgoodstmp表的数据清空
        print '开始清空淘客商品临时表数据' + str(datetime.datetime.now())
        TkGoodsTmp.objects.all().delete()
        # 将tkgoods表的数据转移到tmp表中
        print '开始将淘客商品数据转移到临时表中' + str(datetime.datetime.now())
        for o in TkGoods.objects.all():
            tmp = TkGoodsTmp()
            tmp.goods_id = o.goods_id
            tmp.quan_link = o.quan_link
            tmp.quan_goods_link = o.quan_goods_link
            tmp.tkl = o.tkl
            tmp.save()

        # 删除tkgoods表的数据
        print '开始删除淘客商品表中来源于大淘客的商品' + str(datetime.datetime.now())
        TkGoods.objects.filter(fr=2).delete()
        trans_end_time = datetime.datetime.now()
        print '转移数据结束，花费时间：' + str(trans_end_time - tuiguang_end_time)
        # 重新从大淘客里拉取数据
        print '开始从大淘客拉取数据'
        for x in xrange(1, 101):
            time.sleep(0.2)
            dtk_url = 'http://api.dataoke.com/index.php?r=goodsLink/www&type=www_quan&appkey='+dtk_key+'&v=2'+'&page='+str(x)
            req = urllib2.Request(dtk_url)
            result = urllib2.urlopen(req).read()
            result = json.loads(result)
            goods = result['data']['result']
            if len(goods) == 0:
                break
            print '拉取大淘客第' + str(x) + '数据'
            for g in goods:
                goods_id = g['GoodsID']
                # try:
                #     tkgoods = TkGoods.objects.get(goods_id=goods_id)
                # except ObjectDoesNotExist:
                tkgoods = TkGoods()
                tkgoods.goods_id = g['GoodsID']
                # goods.dtk_id = g['Id']
                tkgoods.c_id = g['Cid']
                tkgoods.title = g['Title']
                tkgoods.d_title = g['D_title']
                tkgoods.pic = g['Pic']
                tkgoods.price = g['Org_Price']
                tkgoods.is_tmall = g['IsTmall']
                tkgoods.dsr = g['Dsr']
                tkgoods.sales_num = g['Sales_num']
                tkgoods.seller_id = g['SellerID']
                tkgoods.quan_price = g['Quan_price']
                tkgoods.quan_time = g['Quan_time']
                tkgoods.quan_surplus = g['Quan_surplus']
                tkgoods.quan_receive = g['Quan_receive']
                tkgoods.quan_condition = g['Quan_condition']
                tkgoods.quan_link = g['Quan_link']
                tkgoods.quan_d_link = g['Quan_m_link']
                tkgoods.link = g['ali_click']
                # 二合一链接
                result = urlparse.urlparse(tkgoods.quan_link)
                params = urlparse.parse_qs(result.query, True)
                active_id = params['activity_id'][0]
                # new_pid = get_pid_from_taobao(tkgoods.link)
                dx = '1'
                if float(g['Commission_queqiao']) > 0:
                    dx = '0'
                print float(g['Commission_queqiao'])
                print dx
                tkgoods.quan_goods_link = 'http://uland.taobao.com/coupon/edetail?activityId=' + active_id + '&pid=' + pid \
                                          + '&itemId=' + goods_id + '&src=tzcb_tzcbpc&dx=' + dx
                # 从tmp表中查看该商品是否存在
                try:
                    tkgoodstmp = TkGoodsTmp.objects.get(goods_id=goods_id)
                    tkgoods.tkl = tkgoodstmp.tkl
                except ObjectDoesNotExist:
                    # tmp表中不存在表示大淘客中新加入的推广,生成淘口令

                    # 生成淘口令
                    param = {
                        'token': token,
                        'url': tkgoods.quan_goods_link,
                        'text': text
                    }
                    param_encode = urllib.urlencode(param)
                    url = req_url + '?' + param_encode
                    req = urllib2.Request(url)

                    result = urllib2.urlopen(req).read()
                    result = json.loads(result)
                    if result['msg'] == 'success':
                        tkgoods.tkl = result['tkl']
                    else:
                        continue
                tkgoods.fr = 2
                tkgoods.save()
        print '拉取大淘客数据结束'
        end_time = datetime.datetime.now()
        print '拉取大淘客花费时间' + str(end_time - trans_end_time)
        print '总花费时间' + str(end_time - start_time)
    except Exception as ex:
        print '添加大淘客商品异常'+ str(ex)
        return JsonResponse(code=Const['code.system_error'], msg=str(ex))
    return JsonResponse(code=Const['code.success'])


def tkad_manager(r):
    tkad = TkAd.objects.all()
    tkad_list = []
    for o in tkad:
        ad = {
            'id': o.id,
            'cid': o.cid,
            'pic': o.pic,
            'link': o.link,
        }
        tkad_list.append(ad)
    return JsonResponse(code=Const['code.success'], data=tkad_list)


def tkad_edit(r):
    cid = r.REQUEST.get('cid')
    tkad = TkAd.objects.get(cid=cid)
    result = {
        'cid': tkad.cid,
        'pic': tkad.pic,
        'link': tkad.link,
    }
    return render(r, "admin/tkad_edit.html", {'tkad': result})


def tkad_save(r):
    cid = r.REQUEST['cid']
    pic = r.REQUEST['pic']
    link = r.REQUEST['link']
    tkad = TkAd.objects.get(cid=cid)
    tkad.pic = pic
    tkad.link = link
    tkad.save()
    return JsonResponse(code=Const['code.success'])
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


def trans_tkgoods_obj_to_dict(obj):
    if obj:
        return {
            'id': obj.id,
            'cid': obj.c_id,
            'title': obj.title if obj.title else '',
            'd_title': obj.d_title if obj.d_title else '',
            'pic': obj.pic if obj.pic else '',
            'price': obj.price,
            'dsr': obj.dsr,
            'sales_num': obj.sales_num,
            'seller_id': obj.seller_id,
            'quan_price': obj.quan_price,
            'quan_time': obj.quan_time.strftime('%Y-%m-%d %H:%M:%S') if obj.quan_time else '',
            'quan_surplus': obj.quan_surplus,
            'quan_receive': obj.quan_receive,
            'quan_condition': obj.quan_condition,
            'quan_link': obj.quan_link,
            'quan_d_link': obj.quan_d_link if obj.quan_d_link else '',
            'link': obj.link,
            'fr': obj.fr,
            'is_tmall': obj.is_tmall,
            'status': obj.status,
            'zhj': obj.price - obj.quan_price,
            'quan_goods_link': obj.quan_goods_link,
            'tkl':obj.tkl,
        }


def trans_tkad_obj_to_dict(obj):
    if obj:
        return{
            'id': obj.id,
            'cid': obj.cid,
            'pic': obj.pic,
            'link': obj.link,
        }


def fen_ye(page_no, page_size, query_result):
    start = (page_no - 1) * page_size
    end = start + page_size

    total_count = query_result.count()
    total_page = total_count / page_size if total_count % page_size == 0 else total_count / page_size + 1
    query_result = query_result[start: end]
    count = query_result.count()
    pages = []
    if total_page < 6:
        pages.extend((x + 1) for x in range(total_page))
    else:
        if page_no < 3:
            pages.extend((x + 1) for x in range(5))
        elif 3 <= page_no < total_page - 2:
            pages.extend(x for x in range(page_no - 2, page_no + 3))
        else:
            pages.extend((x + 1) for x in range(total_page - 5, total_page))
    # pages.extend((x+1) for x in range(total_page))
    return total_count, total_page, count, pages, query_result
