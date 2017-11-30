# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0052_auto_20160106_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='frozen',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
