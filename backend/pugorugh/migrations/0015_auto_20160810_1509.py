# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-10 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0014_auto_20160810_1431'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dog',
            name='description',
        ),
        migrations.AddField(
            model_name='dog',
            name='size',
            field=models.CharField(choices=[('s', 'Small'), ('m', 'Medium'), ('l', 'Large'), ('xl', 'Extra Large')], default='m', max_length=8),
        ),
    ]
