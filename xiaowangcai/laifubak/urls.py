"""laifu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import sys

from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.db import models
from django.conf import settings
from laifu.views import generic, generic_2, generic_web, generic_web_2
import views

reload(sys)
sys.setdefaultencoding('utf-8')

urlpatterns = [
    #rest api
    url(r'^rest/(?P<app>[a-z0-9]+)/(?P<model>[a-z0-9]+)/(?P<action>[a-z0-9]+)/(?P<id>[0-9]+)$', generic),
    url(r'^rest/(?P<app>[a-z0-9]+)/(?P<model>[a-z0-9]+)/(?P<action>[a-z0-9]+)$', generic_2),
    url(r'^rest_web/(?P<app>[a-z0-9]+)/(?P<model>[a-z0-9]+)/(?P<action>[a-z0-9]+)/(?P<id>[0-9]+)$', generic_web),
    url(r'^rest_web/(?P<app>[a-z0-9]+)/(?P<model>[a-z0-9]+)/(?P<action>[a-z0-9]+)$', generic_web_2),

    #web
    url(r'^$', views.home_notice),
    url(r'^messages$', views.messages),
    url(r'^startprivate_chat/(?P<uid>[0-9]+)', views.startprivate_chat),
    url(r'^login$', views.static_html,{'template_name':'login.html'}),
    url(r'^welcome$', views.static_html,{'template_name':'welcome.html'}),
    url(r'^register$', views.static_html,{'template_name':'register.html'}),
    url(r'^protocol$', views.static_html,{'template_name':'protocol.html'}),
    url(r'^reset_pwd$', views.static_html,{'template_name':'reset_pwd.html'}),
    url(r'^add_store$', views.static_html,{'template_name':'add_store.html'}),
    url(r'^to_tutorial$', views.static_html,{'template_name':'to_tutorial.html'}),
    url(r'^seller_introduce$', views.static_html,{'template_name':'seller_introduce.html'}),
    url(r'^help$', views.static_html,{'template_name':'help.html'}),
    url(r'^help_detail$', views.static_html,{'template_name':'help_detail.html'}),
    url(r'^pic_requirement$', views.static_html,{'template_name':'pic_requirement.html'}),
    url(r'^home/notice$', views.home_notice),
    url(r'^home/notice/detail$', views.home_notice_detail),
    url(r'^home/publish/post$', views.home_publish_post),
    url(r'^home/publish/pay$', views.home_publish_pay),
    url(r'^home/task/tasks$', views.home_task_tasks),
    url(r'^home/task/flow$', views.home_task_flows),
    url(r'^home/user$', views.home_user),
    url(r'^home/capital$', views.home_capital),
    url(r'^home/capital/recharge$', views.home_capital_recharge),
    url(r'^home/appeal$', views.home_appeal),
    url(r'^home/promote', views.home_promote),
    url(r'^home/blicklist$', views.home_blicklist),
    url(r'^task/task/detail$', views.task_task_detail),
    url(r'^modify_store$', views.modify_store),
    url(r'^task/flow/detail$', views.task_flow_detail),
    url(r'^task/order/detail$', views.task_order_detail),
    url(r'^task/order/manage$', views.task_order_manage),
    url(r'^task/flow/manage$', views.task_flow_manage),
    url(r'^task/return/manage$', views.task_return_manage),
    url(r'^task/order/appeal/(?P<oid>[0-9]+)$', views.task_order_appeal),
    
    #image
    url(r'^image/(?P<fname>.+)$',views.image),
    #notice
    url(r'^notice/(?P<nid>.+)$',views.notice),
    #tutorial
    url(r'^home/tutorial$',views.home_tutorial),
]

if settings.DEBUG:
    # import debug_toolbar
    urlpatterns += patterns(
        '',
        # url(r'^__debug__/', include(debug_toolbar.urls)),
        url(r'^admin/', include(admin.site.urls)),
    )

models.Model.to_dict = lambda self: {f.column: getattr(self, f.column, None) for f in self.__class__._meta.fields}
models.Model.to_sub_dict = lambda self,*arg: {f.column: getattr(self, f.column, None) for f in self.__class__._meta.fields if f.column in arg}
models.Model.to_exc_dict = lambda self,*arg: {f.column: getattr(self, f.column, None) for f in self.__class__._meta.fields if not f.column in arg}
