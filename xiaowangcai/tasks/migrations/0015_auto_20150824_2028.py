# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_task_others'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='buyer_principal',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.SmallIntegerField(default=0, choices=[(3, b'model.task.type.special'), (1, b'model.task.type.pc_taobao'), (0, b'model.task.type.mobile_taobao'), (2, b'model.task.type.flow')]),
        ),
    ]
