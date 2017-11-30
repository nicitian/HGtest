# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recharge',
            name='user',
            field=models.ForeignKey(to='users.User', null=True),
        ),
        migrations.AddField(
            model_name='withdraw',
            name='bankcard',
            field=models.ForeignKey(to='users.Bankcard', null=True),
        ),
    ]
