# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-05 22:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(max_length=20)),
                ('state', models.CharField(choices=[('brwed', 'borrowed'), ('free', 'free')], default='free', max_length=20)),
                ('borrow_id', models.IntegerField(default=None, null=True)),
            ],
        ),
    ]
