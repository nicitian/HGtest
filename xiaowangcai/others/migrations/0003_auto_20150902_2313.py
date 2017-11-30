# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0002_auto_20150902_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreport',
            name='amount',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='dailyreport',
            name='value',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
