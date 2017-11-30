# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0050_appeal_launch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appeal',
            name='launch',
            field=models.IntegerField(default=0),
        ),
    ]
