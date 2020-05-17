import json
from datetime import datetime, timedelta
import pytz
from celery.task import task
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from trainWellApp.models import Booking, Notification, Invoice

notpaid_manager = {}
events_done_manager = {}
invoices_manager = {}


def setup_task_ispaid(booking):
    global notpaid_manager
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
        task='trainWellApp.tasks.booking_notpaid',
        args=json.dumps([booking.id]),
    )

    notpaid_manager[booking.id] = task.id
    task.kwargs = json.dumps({'id': task.id})
    task.save()


@task
def booking_notpaid(*args, **kwargs):
    booking_id = int(args[0])
    task_id = int(kwargs.get('id'))
    qs = Booking.objects.filter(id=booking_id)

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
    cancel_task(task=task_id)


def setup_task_event_done(booking):
    global events_done_manager

    event_date = booking.selection_set.all().last()
    task_date = event_date.datetime_init + timedelta(hours=1)

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
        name="Booking " + str(booking.id) + " happened",
        task='trainWellApp.tasks.event_done',
        args=json.dumps([booking.id]),
    )

    events_done_manager[booking.id] = task.id
    task.kwargs = json.dumps({'id': task.id})
    task.save()


@task
def event_done(*args, **kwargs):
    booking_id = int(args[0])
    task_id = int(kwargs.get('id'))
    qs = Booking.objects.filter(id=booking_id)

    if qs.exists():
        booking = qs.first()
        booking.is_deleted = True
        booking.save()

    cancel_task(task=task_id)


def setup_task_invoice(invoice):
    global invoices_manager

    curr_year = datetime.now().year
    task_date = datetime.now().replace(year=curr_year + 2)  # By law 2 years.

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
        name="Invoice " + str(invoice.id) + " deleted",
        task='trainWellApp.tasks.invoice_timeout',
        args=json.dumps([invoice.id]),
    )

    invoices_manager[invoice.id] = task.id
    task.kwargs = json.dumps({'id': task.id})
    task.save()


@task
def invoice_timeout(*args, **kwargs):
    invoice_id = args[0]
    task_id = int(kwargs.get('id'))
    qs = Invoice.objects.filter(id=int(invoice_id))

    if qs.exists(): qs.first().delete()

    cancel_task(task=task_id)


def cancel_task(task_manager=None, booking_id=None, task=None):
    task_id = task if task else task_manager.get(booking_id)

    if task_id:
        qs = PeriodicTask.objects.filter(id=task_id)

        if qs.exists():
            task = qs.first()
            qs_cron = CrontabSchedule.objects.filter(id=task.crontab.id)

            if qs_cron.exists():
                crontab = qs_cron.first()
                crontab.delete()

            task.delete()


def get_cron_weekday(day):
    return {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
            'Thursday': 4, 'Friday': 5, 'Saturday': 6}.get(day)
