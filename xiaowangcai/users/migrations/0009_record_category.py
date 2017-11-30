# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_buyer_invitee_award'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='category',
            field=models.SmallIntegerField(default=0),
        ),
    ]
