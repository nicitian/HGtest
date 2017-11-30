# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Administrator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('loginname', models.CharField(unique=True, max_length=45)),
                ('password', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=11)),
                ('normal_permission', models.BooleanField()),
                ('notice_permission', models.BooleanField()),
                ('finance_permission', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.SmallIntegerField()),
                ('content', models.TextField()),
                ('create_time', models.BigIntegerField(default=time.time)),
                ('publish_admin', models.ForeignKey(to='management.Administrator')),
            ],
        ),
        migrations.CreateModel(
            name='Recharge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('bank_name', models.CharField(max_length=45)),
                ('account_name', models.CharField(max_length=255)),
                ('verify_status', models.SmallIntegerField(default=0)),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('verify_admin', models.ForeignKey(blank=True, to='management.Administrator', null=True)),
            ],
            options={
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('verify_status', models.SmallIntegerField(default=0)),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('verify_admin', models.ForeignKey(blank=True, to='management.Administrator', null=True)),
            ],
            options={
                'ordering': ['-create_time'],
            },
        ),
    ]
