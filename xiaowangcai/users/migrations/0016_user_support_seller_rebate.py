# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_user_join_award'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='support_seller_rebate',
            field=models.BooleanField(default=False),
        ),
    ]
