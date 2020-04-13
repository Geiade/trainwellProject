# Generated by Django 3.0.4 on 2020-04-11 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0004_merge_20200411_0023'),
    ]

    operations = [
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_init', models.DateTimeField()),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trainWellApp.Booking')),
                ('place', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trainWellApp.Place')),
            ],
        ),
    ]