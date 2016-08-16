# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-10 13:11
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone


def change_to_date(apps, schema_editor):
    Dog = apps.get_model("pugorugh", "dog")
    today = timezone.now().date()
    for dog in Dog.objects.all():
        dog.date_of_birth = today - timezone.timedelta(days=30*dog.age)
        dog.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pugorugh', '0011_auto_20160810_0822'),
    ]

    operations = [
        migrations.AddField("Dog", "date_of_birth", models.DateField(
            default=timezone.now)),
        migrations.RunPython(change_to_date),
        migrations.RemoveField("Dog", "age"),
    ]