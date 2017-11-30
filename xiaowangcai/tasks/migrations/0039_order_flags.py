# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0038_auto_20151116_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='flags',
            field=models.BigIntegerField(default=0),
        ),
    ]
