# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_user_is_close_sellerreturn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=20)),
                ('tag_id', models.IntegerField()),
                ('tag_prop', models.CharField(max_length=20)),
                ('tag_prop_id', models.IntegerField()),
                ('price', models.DecimalField(default=0, max_digits=11, decimal_places=2)),
                ('user', models.ManyToManyField(to='users.User')),
            ],
        ),
    ]
