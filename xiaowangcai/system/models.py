# encoding: utf-8
from django.db import models

from shouzhuan.const import device_constraint
from shouzhuan.utils import msec_time


class RequestLog(models.Model):
    time = models.BigIntegerField(default=msec_time)
    url = models.URLField(null=True, blank=True)
    c_type = models.SmallIntegerField(null=True, choices=device_constraint, blank=True)
    c_version = models.CharField(max_length=20)
    c_versioncode = models.IntegerField(default=0)
    useragent = models.CharField(max_length=200)
