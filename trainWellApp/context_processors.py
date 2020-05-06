from trainWellApp.models import Notification


def notifications(request):
    qs = Notification.objects.filter(booking__planner__user_id=request.user.id, is_deleted=False)
    kwargs = {'notifications': qs}
    return kwargs
