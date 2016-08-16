# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-09 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0003_auto_20160809_0834'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dog',
            name='image',
        ),
        migrations.AddField(
            model_name='dog',
            name='image_filename',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
