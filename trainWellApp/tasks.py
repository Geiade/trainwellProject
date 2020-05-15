import json
from datetime import datetime, timedelta
import pytz
from celery.task import task
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from trainWellApp.models import Booking, Notification, Invoice

task_manager = {}


@task
def check_invoice_ispaid(*args):
    global task_manager
    booking_id = args[0]
    qs = Booking.objects.filter(id=int(booking_id))

    if qs.exists():
        booking = qs.first()
        booking.is_deleted = True
        booking.save()

        # Create a notification for manager and planner.
        title = "Canceled booking: " + booking.name
        description = "Booking was canceled because it was not paid within 24h."
        notification = Notification(name=title, description=description, booking=booking)
        notification.save()


        qs = Invoice.objects.filter(booking_id=booking.id)
        if qs.exists():
            invoice = qs.first()
            invoice.booking_state = 4   # State 'Cancelada impagada'
            invoice.save()

    # After completed cancel it.
    cancel_task(booking_id)


def setup_task(booking):
    global task_manager
    event_date = booking.selection_set.all().first().datetime_init
    diff = (event_date - datetime.now()).days
    task_date = (datetime.now() + timedelta(hours=24)) if diff >= 1 else (event_date - timedelta(hours=1))

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=task_date.minute,
        hour=task_date.hour,
        day_of_week=get_cron_weekday(task_date.strftime("%A")),
        day_of_month=task_date.day,
        month_of_year=task_date.month,
        timezone=pytz.timezone('Europe/Madrid')
    )

    task = PeriodicTask.objects.create(
        crontab=schedule,
        name="Check after 24h if " + str(booking.id) + " is_paid",
        task='trainWellApp.tasks.check_invoice_ispaid',
        args=json.dumps([booking.id]),
        expires=task_date + timedelta(minutes=5)
    )

    task_manager[booking.id] = task.id


def cancel_task(booking_id):
    global task_manager
    task_id = task_manager.get(booking_id)

    if task_id:
        qs = PeriodicTask.objects.filter(id=task_id)

        if qs.exists():
            task = qs.first()
            qs_cron = CrontabSchedule.objects.filter(id=task.crontab.id)

            if qs_cron.exists():
                crontab = qs_cron.first()
                crontab.delete()

            task.delete()
            del task_manager[booking_id]


def get_cron_weekday(day):
    return {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
            'Thursday': 4, 'Friday': 5, 'Saturday': 6}.get(day)
