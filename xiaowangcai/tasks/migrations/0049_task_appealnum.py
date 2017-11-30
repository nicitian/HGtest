# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0048_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='appealnum',
            field=models.IntegerField(default=0),
        ),
    ]
