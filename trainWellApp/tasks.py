from datetime import datetime
from celery.task import task
task_manager = {}


@task(bind=True)
def is_invoice_paid_at_time(self, booking_id):
    global task_manager

    task_manager[booking_id] = self.request.id
    print(task_manager)


