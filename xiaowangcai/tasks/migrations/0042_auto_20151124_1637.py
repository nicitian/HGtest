# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0041_auto_20151123_1648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='difference',
        ),
        migrations.AlterField(
            model_name='order',
            name='flags',
            field=models.SmallIntegerField(default=0),
        ),
    ]
