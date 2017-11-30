# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_user_flags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='free_verify',
        ),
        migrations.RemoveField(
            model_name='user',
            name='support_seller_rebate',
        ),
    ]
