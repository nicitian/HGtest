# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='promote_award',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AddField(
            model_name='user',
            name='today_commission',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
    ]
