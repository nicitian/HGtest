# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0019_task_total_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='total_price',
            field=models.DecimalField(max_digits=11, decimal_places=2),
        ),
    ]
