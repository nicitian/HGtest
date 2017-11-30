# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0056_store_buy_time_limit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appeal',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['-id']},
        ),
    ]
