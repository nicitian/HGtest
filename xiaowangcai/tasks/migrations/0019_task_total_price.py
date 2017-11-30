# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0018_storerecentbuyer_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='total_price',
            field=models.DecimalField(default=-1, max_digits=11, decimal_places=2),
        ),
    ]
