# Generated by Django 2.2.12 on 2020-05-23 11:43

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('trainWellApp', '0023_auto_20200520_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='map',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='map',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
