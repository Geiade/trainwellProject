# Generated by Django 3.0.6 on 2020-05-25 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0024_auto_20200523_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='price_hour',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]