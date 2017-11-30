# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0032_auto_20151101_0127'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='step_interval',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(104, b'model.order.status.deliver'), (2, b'model.order.status.cancel'), (105, b'model.order.status.comment'), (10, b'model.order.status.completed'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (100, b'model.order.status.step1'), (107, b'model.order.status.step9'), (106, b'model.order.status.affirm'), (2, b'model.order.status.seller_request_cancel'), (1, b'model.order.status.received'), (0, b'model.order.status.init'), (103, b'model.order.status.returnmoney'), (3, b'model.order.status.buyer_request_cancel')]),
        ),
    ]
