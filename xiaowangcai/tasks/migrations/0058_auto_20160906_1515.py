# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0057_auto_20160629_2236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appeal',
            options={'ordering': ['-create_time']},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['-create_time']},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-create_time']},
        ),
        migrations.AlterField(
            model_name='order',
            name='difference',
            field=models.DecimalField(default=0, max_digits=20, decimal_places=2, db_index=True),
        ),
    ]
