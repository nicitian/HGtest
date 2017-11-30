# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0035_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='step_number',
        ),
    ]
