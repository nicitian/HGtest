# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('time', models.BigIntegerField(default=shouzhuan.utils.msec_time)),
                ('url', models.URLField(null=True, blank=True)),
                ('c_type', models.SmallIntegerField(blank=True, null=True, choices=[(0, b'model.device.unknown'), (2, b'model.device.ios'), (1, b'model.device.android'), (3, b'model.device.pc')])),
                ('c_version', models.CharField(max_length=20)),
                ('c_versioncode', models.IntegerField(default=0)),
                ('useragent', models.CharField(max_length=200)),
            ],
        ),
    ]
