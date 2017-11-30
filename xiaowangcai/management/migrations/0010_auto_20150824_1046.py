# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_administrator_statistic_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='administrator',
            name='finance_permission',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='administrator',
            name='normal_permission',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='administrator',
            name='notice_permission',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='administrator',
            name='statistic_permission',
            field=models.BooleanField(default=True),
        ),
    ]
