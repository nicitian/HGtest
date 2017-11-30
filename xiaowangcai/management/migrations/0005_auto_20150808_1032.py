# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_auto_20150806_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='important',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notice',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
    ]
