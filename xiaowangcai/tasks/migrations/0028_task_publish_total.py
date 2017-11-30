# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0027_task_inviter_awarded'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='publish_total',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
