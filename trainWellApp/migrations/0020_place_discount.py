# Generated by Django 2.2.12 on 2020-05-15 17:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0019_auto_20200514_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='discount',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
