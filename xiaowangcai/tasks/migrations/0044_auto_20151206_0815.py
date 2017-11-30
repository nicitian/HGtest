# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0043_auto_20151125_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='difference',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='order',
            name='flags',
            field=models.IntegerField(default=0),
        ),
    ]
