# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0015_auto_20151220_0303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdraw',
            name='reward',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
    ]
