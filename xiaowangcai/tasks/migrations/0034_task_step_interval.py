# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0033_auto_20151101_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='step_interval',
            field=models.IntegerField(default=0),
        ),
    ]
