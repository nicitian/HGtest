# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0031_auto_20151028_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='upgraded',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_type',
            field=models.SmallIntegerField(choices=[(4, b'model.order.type.collect'), (1, b'model.order.type.keyword'), (0, b'model.order.type.normal'), (3, b'model.order.type.flow'), (5, b'model.order.type.direct'), (2, b'model.order.type.image'), (6, b'model.order.type.advance')]),
        ),
        migrations.AlterField(
            model_name='order',
            name='step_detail',
            field=models.TextField(default=b'{}'),
        ),
    ]
