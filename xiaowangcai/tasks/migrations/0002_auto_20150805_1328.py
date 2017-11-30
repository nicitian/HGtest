# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150805_1328'),
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appeal',
            name='user',
        ),
        migrations.AlterField(
            model_name='appealtype',
            name='description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(104, b'model.order.status.deliver'), (100, b'model.order.status.step1'), (105, b'model.order.status.comment'), (103, b'model.order.status.returnmoney'), (10, b'model.order.status.completed'), (1, b'model.order.status.received'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (0, b'model.order.status.init'), (106, b'model.order.status.affirm')]),
        ),
    ]
