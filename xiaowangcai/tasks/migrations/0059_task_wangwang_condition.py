# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0058_auto_20160906_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='wangwang_condition',
            field=models.TextField(max_length=255, null=True),
        ),
    ]
