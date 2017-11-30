# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_auto_20151005_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdraw',
            name='notr',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
    ]
