# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('others', '0006_auto_20161111_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='tkgoods',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
