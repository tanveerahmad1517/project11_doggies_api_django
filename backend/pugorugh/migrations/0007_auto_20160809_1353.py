# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-09 13:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0006_auto_20160809_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dog',
            name='breed',
            field=models.CharField(default='Pure Mutt', max_length=100),
        ),
    ]
