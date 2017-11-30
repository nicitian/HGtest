# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20150805_1328'),
        ('tasks', '0002_auto_20150805_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='appeal',
            name='complainant',
            field=models.ForeignKey(related_name='complainant_appeals', to='users.User', null=True),
        ),
        migrations.AddField(
            model_name='appeal',
            name='order_status',
            field=models.SmallIntegerField(default=0, choices=[(1, b'model.appeal.order.status.buyer_request'), (3, b'model.appeal.order.status.ordercancel'), (2, b'model.appeal.order.status.seller_request'), (0, b'model.appeal.order.status.none')]),
        ),
        migrations.AddField(
            model_name='appeal',
            name='platform_involve',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appeal',
            name='progress',
            field=models.TextField(default=b'[]'),
        ),
        migrations.AddField(
            model_name='appeal',
            name='respondent',
            field=models.ForeignKey(related_name='respondent_appeals', to='users.User', null=True),
        ),
        migrations.AddField(
            model_name='appeal',
            name='status',
            field=models.SmallIntegerField(default=1, choices=[(1, b'model.appeal.status.in_progress'), (2, b'model.appeal.status.closed')]),
        ),
    ]
