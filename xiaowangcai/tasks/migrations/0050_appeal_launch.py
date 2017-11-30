# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0049_task_appealnum'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='launch',
            field=models.SmallIntegerField(default=0),
        ),
    ]
