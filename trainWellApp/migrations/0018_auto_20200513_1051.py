# Generated by Django 2.2.12 on 2020-05-13 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trainWellApp', '0017_invoice_booking_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='is_paid',
        ),
        migrations.AddField(
            model_name='selection',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='booking',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trainWellApp.Booking'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_method',
            field=models.PositiveIntegerField(choices=[(1, 'Credit card'), (2, 'Cash'), (3, 'Bank Transfer'), (4, 'Bank check')], default=2),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
