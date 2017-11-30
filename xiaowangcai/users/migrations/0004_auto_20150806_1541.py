# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150805_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbaccount',
            name='wangwang',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
