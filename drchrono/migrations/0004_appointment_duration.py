# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-21 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drchrono', '0003_remove_appointment_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='duration',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
