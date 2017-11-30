# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0028_task_publish_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='weights',
            field=models.IntegerField(default=0),
        ),
    ]
