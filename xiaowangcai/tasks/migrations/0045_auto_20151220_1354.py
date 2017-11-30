# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0044_auto_20151206_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='flags',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='id',
            field=models.BigIntegerField(serialize=False, primary_key=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.SmallIntegerField(db_index=True, choices=[(4, b'model.order.type.collect'), (1, b'model.order.type.keyword'), (0, b'model.order.type.normal'), (3, b'model.order.type.flow'), (5, b'model.order.type.direct'), (2, b'model.order.type.image'), (6, b'model.order.type.advance')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='receive_time',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(104, b'model.order.status.deliver'), (2, b'model.order.status.cancel'), (105, b'model.order.status.comment'), (10, b'model.order.status.completed'), (102, b'model.order.status.step3'), (101, b'model.order.status.step2'), (100, b'model.order.status.step1'), (107, b'model.order.status.step9'), (106, b'model.order.status.affirm'), (2, b'model.order.status.seller_request_cancel'), (1, b'model.order.status.received'), (0, b'model.order.status.init'), (103, b'model.order.status.returnmoney'), (3, b'model.order.status.buyer_request_cancel')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='update_time',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='weights',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='return_type',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(1, b'model.task.return_type.seller'), (0, b'model.task.return_type.platform')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(1, b'model.task.status.in_progress'), (0, b'model.task.status.need_payment'), (2, b'model.task.status.closed'), (3, b'model.task.status.cancel')]),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(3, b'model.task.type.special'), (1, b'model.task.type.pc_taobao'), (0, b'model.task.type.mobile_taobao'), (2, b'model.task.type.flow')]),
        ),
    ]
