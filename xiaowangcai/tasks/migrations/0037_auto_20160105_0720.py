# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0036_remove_order_step_number'),
    ]

    operations = [
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
            name='publish_time',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
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
            model_name='store',
            name='name',
            field=models.CharField(unique=True, max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='wangwang',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='storerecentbuyeruser',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='storerecentbuyeruser',
            name='type',
            field=models.SmallIntegerField(db_index=True),
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
        migrations.AlterField(
            model_name='task',
            name='verify_status',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
    ]
