# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-10 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0009_auto_20160809_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dog',
            name='breed',
            field=models.CharField(blank=True, default='Pure Mutt', max_length=100),
        ),
        migrations.AlterField(
            model_name='dog',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
