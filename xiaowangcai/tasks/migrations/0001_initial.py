# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('management', '__first__'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appeal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason', models.TextField()),
                ('pic_path', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='AppealType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('order_type', models.SmallIntegerField(choices=[(4, b'model.order.type.collect'), (1, b'model.order.type.keyword'), (2, b'model.order.type.image'), (0, b'model.order.type.normal'), (3, b'model.order.type.flow'), (5, b'model.order.type.direct')])),
                ('search_entry_index', models.SmallIntegerField()),
                ('status', models.SmallIntegerField(default=0, choices=[(104, b'model.order.status.deliver'), (105, b'model.order.status.comment'), (100, b'model.order.status.step1'), (103, b'model.order.status.returnmoney'), (10, b'model.order.status.completed'), (1, b'model.order.status.received'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (0, b'model.order.status.init'), (106, b'model.order.status.affirm')])),
                ('receive_time', models.BigIntegerField(null=True, blank=True)),
                ('device', models.SmallIntegerField(blank=True, null=True, choices=[(0, b'model.device.pc'), (1, b'model.device.android'), (2, b'model.device.ios')])),
                ('step_detail', models.CharField(default=b'[]', max_length=1000)),
                ('step_number', models.SmallIntegerField(default=0)),
                ('bankcard', models.ForeignKey(blank=True, to='users.Bankcard', null=True)),
            ],
            options={
                'ordering': ['-receive_time'],
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.SmallIntegerField(default=0, choices=[(0, b'model.platform.taobao')])),
                ('name', models.CharField(unique=True, max_length=255)),
                ('wangwang', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('verify_status', models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')])),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('user', models.ForeignKey(to='users.User')),
                ('verify_admin', models.ForeignKey(blank=True, to='management.Administrator', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('platform', models.SmallIntegerField(default=0, choices=[(0, b'model.platform.taobao')])),
                ('task_type', models.SmallIntegerField(default=0, choices=[(0, b'model.task.type.mobile_taobao')])),
                ('commodities', models.TextField()),
                ('search_entries', models.CharField(max_length=255)),
                ('low_price', models.DecimalField(default=-1, max_digits=11, decimal_places=2)),
                ('up_price', models.DecimalField(default=-1, max_digits=11, decimal_places=2)),
                ('commodity_address', models.CharField(max_length=45)),
                ('order_types', models.CharField(max_length=255)),
                ('comment_keyword', models.CharField(max_length=60, null=True)),
                ('comment_image', models.CharField(max_length=1000, null=True)),
                ('return_type', models.SmallIntegerField(default=0, choices=[(1, b'model.task.return_type.seller'), (0, b'model.task.return_type.platform')])),
                ('bonus', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('order_comment', models.CharField(max_length=255)),
                ('publish_start_date', models.DateField(null=True, blank=True)),
                ('publish_start_time', models.TimeField(null=True, blank=True)),
                ('publish_end_time', models.TimeField(null=True, blank=True)),
                ('publish_num', models.IntegerField(null=True, blank=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(2, b'model.task.status.closed'), (3, b'model.task.status.cancel'), (1, b'model.task.status.in_progress'), (0, b'model.task.status.need_payment')])),
                ('verify_status', models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')])),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('task_remark', models.CharField(max_length=255, null=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('store', models.ForeignKey(to='tasks.Store')),
                ('verify_admin', models.ForeignKey(blank=True, to='management.Administrator', null=True)),
            ],
            options={
                'ordering': ['-create_time'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='task',
            field=models.ForeignKey(to='tasks.Task'),
        ),
        migrations.AddField(
            model_name='order',
            name='tb',
            field=models.ForeignKey(blank=True, to='users.TBAccount', null=True),
        ),
        migrations.AddField(
            model_name='appeal',
            name='order',
            field=models.ForeignKey(to='tasks.Order'),
        ),
        migrations.AddField(
            model_name='appeal',
            name='type',
            field=models.ForeignKey(to='tasks.AppealType'),
        ),
        migrations.AddField(
            model_name='appeal',
            name='user',
            field=models.ForeignKey(to='users.User'),
        ),
    ]
