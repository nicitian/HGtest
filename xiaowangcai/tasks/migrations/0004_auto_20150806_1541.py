# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_auto_20150805_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
        migrations.AddField(
            model_name='order',
            name='buyer_gain',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AddField(
            model_name='order',
            name='seller_payment',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
    ]
