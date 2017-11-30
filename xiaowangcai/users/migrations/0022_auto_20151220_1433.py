# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import shouzhuan.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_user_notice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='amount',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2, db_index=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='balance',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2, db_index=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='category',
            field=models.SmallIntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.SmallIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='create_time',
            field=models.BigIntegerField(default=shouzhuan.utils.msec_time, db_index=True),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='name',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='phone',
            field=models.CharField(max_length=11, db_index=True),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='status',
            field=models.SmallIntegerField(default=0, db_index=True, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='verify_time',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tbaccount',
            name='wangwang',
            field=models.CharField(unique=True, max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='buyer_level',
            field=models.SmallIntegerField(default=1, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='buyer_orders',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='flags',
            field=models.BigIntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(unique=True, max_length=11, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='seller_level',
            field=models.SmallIntegerField(default=1, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='seller_orders',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(unique=True, max_length=45, db_index=True),
        ),
    ]
