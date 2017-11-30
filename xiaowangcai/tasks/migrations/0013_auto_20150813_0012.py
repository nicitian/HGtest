# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_record_category'),
        ('tasks', '0012_auto_20150810_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreRecentBuyer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('store', models.ForeignKey(to='tasks.Store')),
                ('tb', models.ForeignKey(to='users.TBAccount')),
            ],
        ),
        migrations.AddField(
            model_name='store',
            name='recent_buyers',
            field=models.ManyToManyField(to='users.TBAccount', through='tasks.StoreRecentBuyer'),
        ),
    ]
