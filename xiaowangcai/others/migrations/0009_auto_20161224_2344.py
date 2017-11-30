# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0008_auto_20161114_2241'),
    ]

    operations = [
        migrations.CreateModel(
            name='TkAd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cid', models.IntegerField()),
                ('pic', models.CharField(max_length=255, null=True)),
                ('link', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='c_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='dtk_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='goods_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tkgoods',
            name='quan_goods_link',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='tkgoods',
            name='seller_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
