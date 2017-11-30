# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20150830_1004'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bankcard',
            options={'ordering': ['-create_time']},
        ),
        migrations.AlterModelOptions(
            name='tbaccount',
            options={'ordering': ['-create_time']},
        ),
        migrations.AddField(
            model_name='bankcard',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
    ]
