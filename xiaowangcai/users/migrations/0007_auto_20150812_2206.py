# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_imei'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_award_time',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='promote_num',
            field=models.IntegerField(default=0),
        ),
    ]
