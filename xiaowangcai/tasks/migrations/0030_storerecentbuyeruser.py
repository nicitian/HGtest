# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_user_support_seller_rebate'),
        ('tasks', '0029_order_weights'),
    ]

    operations = [
        migrations.CreateModel(
            name='StoreRecentBuyerUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('type', models.SmallIntegerField()),
                ('store', models.ForeignKey(to='tasks.Store')),
                ('user', models.ForeignKey(to='users.User')),
            ],
        ),
    ]
