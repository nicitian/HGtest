# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_appeal_pic_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appeal',
            name='order_status',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(104, b'model.order.status.deliver'), (2, b'model.order.status.cancel'), (100, b'model.order.status.step1'), (105, b'model.order.status.comment'), (103, b'model.order.status.returnmoney'), (10, b'model.order.status.completed'), (3, b'model.order.status.buyer_request_cancel'), (1, b'model.order.status.received'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (0, b'model.order.status.init'), (106, b'model.order.status.affirm'), (2, b'model.order.status.seller_request_cancel')]),
        ),
    ]
