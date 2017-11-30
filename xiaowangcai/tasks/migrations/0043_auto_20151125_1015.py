# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0042_auto_20151124_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='flags',
            field=models.BooleanField(default=False),
        ),
    ]
