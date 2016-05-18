# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-16 10:36
from __future__ import unicode_literals

import ditto.flickr.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flickr', '0015_auto_20160514_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='video_original_file',
            field=models.FileField(blank=True, default='', help_text='Only present for Videos.', upload_to=ditto.flickr.models.Photo.upload_path),
        ),
    ]