# Generated by Django 3.0.4 on 2020-04-27 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0007_merge_20200413_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='planner',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]