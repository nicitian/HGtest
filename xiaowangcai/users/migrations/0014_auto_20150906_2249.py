# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20150905_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='imei',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
