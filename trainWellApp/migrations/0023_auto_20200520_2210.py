# Generated by Django 2.2.12 on 2020-05-20 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0022_place_shape'),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('image', models.ImageField(blank=True, default='place_images/default.png', null=True, upload_to='maps/')),
            ],
        ),
        migrations.RemoveField(
            model_name='place',
            name='shape',
        ),
    ]
