# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_auto_20150824_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='notice',
            name='update_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
    ]
