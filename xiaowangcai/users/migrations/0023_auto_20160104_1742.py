# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20151220_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankcard',
            name='bank_district',
            field=models.CharField(default=None, max_length=45),
        ),
        migrations.AddField(
            model_name='bankcard',
            name='bank_province',
            field=models.CharField(default=None, max_length=45),
        ),
    ]
