# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0004_auto_20151005_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='TkGoods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('d_title', models.CharField(max_length=255, null=True)),
                ('pic', models.CharField(max_length=255, null=True)),
                ('price', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('dsr', models.CharField(max_length=10, null=True)),
                ('sales_num', models.IntegerField(default=0)),
                ('seller_id', models.IntegerField(null=True)),
                ('quan_price', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('quan_time', models.DateTimeField(null=True)),
                ('quan_surplus', models.IntegerField(default=0)),
                ('quan_receive', models.IntegerField(default=0)),
                ('quan_condition', models.CharField(max_length=255, null=True)),
                ('quan_link', models.CharField(max_length=255)),
                ('quan_d_link', models.CharField(max_length=255, null=True)),
                ('link', models.CharField(max_length=255)),
            ],
        ),
    ]
