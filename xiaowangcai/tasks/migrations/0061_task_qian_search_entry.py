# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0060_task_is_qian'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='qian_search_entry',
            field=models.TextField(max_length=255, null=True),
        ),
    ]
