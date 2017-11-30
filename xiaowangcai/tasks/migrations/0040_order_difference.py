# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0039_order_flags'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='difference',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
    ]
