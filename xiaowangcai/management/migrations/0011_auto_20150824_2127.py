# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_auto_20150824_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdraw',
            name='admin_submit',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AddField(
            model_name='withdraw',
            name='type',
            field=models.SmallIntegerField(default=1, choices=[(1, b'model.withdraw.type.commission'), (0, b'model.withdraw.type.principal')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recharge',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='verify_status',
            field=models.SmallIntegerField(default=0, choices=[(0, b'model.verify.need_check'), (2, b'model.verify.check_deny'), (1, b'model.verify.check_pass')]),
        ),
    ]
