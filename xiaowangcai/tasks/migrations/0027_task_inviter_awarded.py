# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0026_auto_20151007_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='inviter_awarded',
            field=models.BooleanField(default=False),
        ),
    ]
