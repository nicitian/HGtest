# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0014_withdraw_notr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withdraw',
            name='notr',
        ),
        migrations.AddField(
            model_name='withdraw',
            name='reward',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
    ]
