# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0015_auto_20150824_2028'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['-create_time']},
        ),
        migrations.AddField(
            model_name='store',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time),
        ),
        migrations.AlterField(
            model_name='appeal',
            name='status',
            field=models.SmallIntegerField(default=1, choices=[(2, b'model.appeal.status.closed'), (1, b'model.appeal.status.in_progress')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='device',
            field=models.SmallIntegerField(blank=True, null=True, choices=[(2, b'model.device.ios'), (1, b'model.device.android'), (0, b'model.device.pc')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.SmallIntegerField(choices=[(4, b'model.order.type.collect'), (1, b'model.order.type.keyword'), (0, b'model.order.type.normal'), (3, b'model.order.type.flow'), (5, b'model.order.type.direct'), (2, b'model.order.type.image')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(104, b'model.order.status.deliver'), (2, b'model.order.status.cancel'), (105, b'model.order.status.comment'), (10, b'model.order.status.completed'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (100, b'model.order.status.step1'), (106, b'model.order.status.affirm'), (2, b'model.order.status.seller_request_cancel'), (1, b'model.order.status.received'), (0, b'model.order.status.init'), (103, b'model.order.status.returnmoney'), (3, b'model.order.status.buyer_request_cancel')]),
        ),
        migrations.AlterField(
            model_name='store',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.SmallIntegerField(default=0, choices=[(1, b'model.task.status.in_progress'), (0, b'model.task.status.need_payment'), (2, b'model.task.status.closed'), (3, b'model.task.status.cancel')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
    ]
