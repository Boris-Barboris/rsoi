# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user_portal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrow',
            name='book_id',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
