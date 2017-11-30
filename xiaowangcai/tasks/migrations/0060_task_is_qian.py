# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0059_task_wangwang_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_qian',
            field=models.SmallIntegerField(default=0),
        ),
    ]
