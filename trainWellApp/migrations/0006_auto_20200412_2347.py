# Generated by Django 3.0.4 on 2020-04-12 21:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0005_selection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='datetime_end',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='datetime_init',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='place',
        ),
        migrations.AlterField(
            model_name='selection',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trainWellApp.Booking'),
        ),
        migrations.AlterField(
            model_name='selection',
            name='place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trainWellApp.Place'),
        ),
    ]
