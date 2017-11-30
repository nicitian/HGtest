# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20150808_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='imei',
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
    ]
