# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreport',
            name='amount',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='dailyreport',
            name='value',
            field=models.IntegerField(default=0),
        ),
    ]
