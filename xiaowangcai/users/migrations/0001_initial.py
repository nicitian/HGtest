# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('management', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bankcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bank_name', models.CharField(max_length=45)),
                ('bank_city', models.CharField(max_length=45)),
                ('owner_name', models.CharField(max_length=20)),
                ('account_id', models.CharField(unique=True, max_length=20)),
                ('account_name', models.CharField(max_length=45, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Blacklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('reason', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('amount', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('balance', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('type', models.SmallIntegerField(choices=[(1, b'model.record.out'), (0, b'model.record.in')])),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Smscaptcha',
            fields=[
                ('phone', models.CharField(max_length=11, serialize=False, primary_key=True)),
                ('captcha', models.CharField(max_length=6)),
                ('create_time', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TBAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wangwang', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=11)),
                ('city', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('pic_paths', models.CharField(max_length=255)),
                ('status', models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')])),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('today_receive_orders', models.SmallIntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=45)),
                ('password', models.CharField(max_length=32)),
                ('phone', models.CharField(unique=True, max_length=11)),
                ('buyer_level', models.SmallIntegerField(default=1)),
                ('seller_level', models.SmallIntegerField(default=1)),
                ('buyer_orders', models.IntegerField(default=0)),
                ('seller_orders', models.IntegerField(default=0)),
                ('idc_name', models.CharField(default=b'', max_length=20, blank=True)),
                ('idc_number', models.CharField(max_length=20, null=True, blank=True)),
                ('idc_photo', models.CharField(max_length=255, blank=True)),
                ('qq', models.CharField(max_length=20, blank=True)),
                ('photo', models.CharField(max_length=255, blank=True)),
                ('principal', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('commission', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('register_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('verify_status', models.SmallIntegerField(default=0, choices=[(1, b'model.verify.check_pass'), (2, b'model.verify.check_deny'), (0, b'model.verify.need_check')])),
                ('verify_time', models.BigIntegerField(null=True, blank=True)),
                ('free_verify', models.BooleanField(default=False)),
                ('blacklist_buyer', models.ManyToManyField(related_name='in_blacklist', through='users.Blacklist', to='users.User')),
                ('inviter', models.ForeignKey(related_name='invitee', blank=True, to='users.User', null=True)),
                ('verify_admin', models.ForeignKey(blank=True, to='management.Administrator', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='user',
            field=models.ForeignKey(to='users.User'),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='verify_admin',
            field=models.ForeignKey(blank=True, to='management.Administrator', null=True),
        ),
        migrations.AddField(
            model_name='record',
            name='user',
            field=models.ForeignKey(to='users.User'),
        ),
        migrations.AddField(
            model_name='blacklist',
            name='buyer',
            field=models.ForeignKey(related_name='bl_buyer', to='users.User'),
        ),
        migrations.AddField(
            model_name='blacklist',
            name='seller',
            field=models.ForeignKey(related_name='bl_seller', to='users.User'),
        ),
        migrations.AddField(
            model_name='bankcard',
            name='user',
            field=models.ForeignKey(to='users.User'),
        ),
    ]
