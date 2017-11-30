# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20150812_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='buyer_invitee_award',
            field=models.BooleanField(default=True),
        ),
    ]
