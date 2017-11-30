# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20150906_2249'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='join_award',
            field=models.BooleanField(default=False),
        ),
    ]
