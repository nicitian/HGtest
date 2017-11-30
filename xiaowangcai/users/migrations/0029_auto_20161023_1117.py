# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_auto_20160908_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbaccount',
            name='frozen_days',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='frozen_start_datetime',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='tbaccount',
            name='is_frozen',
            field=models.SmallIntegerField(default=0),
        ),
    ]
