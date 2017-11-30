# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_user_support_seller_rebate'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='flags',
            field=models.BigIntegerField(default=0),
        ),
    ]
