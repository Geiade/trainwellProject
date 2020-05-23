from django.core.exceptions import PermissionDenied

from trainWellApp.models import Planner


def staff_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                planner = Planner.objects.get(user=request.user)
                if planner.is_staff is True:
                    return function(request, *args, **kwargs)
                else:
                    raise PermissionDenied

            except Planner.DoesNotExist:
                raise PermissionDenied
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def gerent_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                planner = Planner.objects.get(user=request.user)
                if planner.is_gerent is True:
                    return function(request, *args, **kwargs)
                else:
                    raise PermissionDenied

            except Planner.DoesNotExist:
                raise PermissionDenied
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



