# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0044_auto_20151206_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='finish',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appeal',
            name='forced',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appeal',
            name='order_cancel',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='frozen',
            field=models.BooleanField(default=False),
        ),
    ]
