# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0044_auto_20151206_0815'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='flow',
            field=models.BooleanField(default=False),
        ),
    ]