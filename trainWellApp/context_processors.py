from django.contrib.auth.decorators import login_required

from trainWellApp.models import Notification


def notifications(request):
    user = request.user
    kwargs = {}

    if not user.is_anonymous:
        if user.planner.is_gerent:
            qs = Notification.objects.filter(level=2, is_read=False, is_deleted=False)
            kwargs['notifications'] = qs


        elif not user.planner.is_gerent and not user.planneris_staff:
            qs = Notification.objects.filter(booking__planner__user_id=user.id,
                                             level=1, is_read=False, is_deleted=False)
            kwargs['notifications'] = qs

    return kwargs
