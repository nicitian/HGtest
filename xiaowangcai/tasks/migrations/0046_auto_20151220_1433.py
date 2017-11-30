# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0045_auto_20151220_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='difference',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2, db_index=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='publish_time',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
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
            name='verify_status',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
    ]
