# Generated by Django 3.0.4 on 2020-05-06 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0013_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='planner',
            name='is_gerent',
            field=models.BooleanField(default=False),
        ),
    ]
