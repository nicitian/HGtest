# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_auto_20150811_2248'),
        ('users', '0009_record_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='idc_number',
        ),
        migrations.AddField(
            model_name='bankcard',
            name='verify_admin',
            field=models.ForeignKey(blank=True, to='management.Administrator', null=True),
        ),
        migrations.AddField(
            model_name='bankcard',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')]),
        ),
        migrations.AddField(
            model_name='bankcard',
            name='verify_time',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='idc_photo',
            field=models.CharField(max_length=600, blank=True),
        ),
    ]
