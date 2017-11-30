# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150805_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blacklist',
            name='buyer',
            field=models.ForeignKey(related_name='buyer_blacklist', to='users.User'),
        ),
        migrations.AlterField(
            model_name='blacklist',
            name='seller',
            field=models.ForeignKey(related_name='seller_blacklist', to='users.User'),
        ),
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.SmallIntegerField(choices=[(1, b'model.record.commission'), (0, b'model.record.pricipal')]),
        ),
    ]
