# Generated by Django 2.2.12 on 2020-05-14 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0018_auto_20200512_1941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='booking_states',
        ),
        migrations.AddField(
            model_name='invoice',
            name='booking_state',
            field=models.PositiveIntegerField(choices=[(1, 'Pagada'), (2, 'Impagada'), (3, 'Cancelada pagada'), (4, 'Cancelada impagada'), (5, 'Cancelada fora de termini')], default=2),
        ),
        migrations.AddField(
            model_name='notification',
            name='level',
            field=models.PositiveIntegerField(choices=[(1, 'USER'), (2, 'ADMIN')], default=1),
        ),
        migrations.AddField(
            model_name='selection',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
