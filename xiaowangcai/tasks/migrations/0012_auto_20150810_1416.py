# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20150809_1642'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='publish_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='istm',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='comment_image',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='comment_keyword',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='commodity_address',
            field=models.CharField(max_length=45, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='order_comment',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_remark',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
