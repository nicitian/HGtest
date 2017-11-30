# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0031_auto_20151028_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='prepublish',
            field=models.BooleanField(default=False),
        ),
    ]
