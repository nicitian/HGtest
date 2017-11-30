# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0040_order_difference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='difference',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
    ]
