from django.core.exceptions import PermissionDenied

from trainWellApp.models import Planner


class StaffRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                planner = Planner.objects.get(user=request.user)
                if planner.is_staff is True:
                    return super().dispatch(request, *args, **kwargs)
                else:
                    raise PermissionDenied

            except Planner.DoesNotExist:
                raise PermissionDenied
        else:
            raise PermissionDenied


class GerentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                planner = Planner.objects.get(user=request.user)
                if planner.is_gerent is True:
                    return super().dispatch(request, *args, **kwargs)
                else:
                    raise PermissionDenied

            except Planner.DoesNotExist:
                raise PermissionDenied
        else:
            raise PermissionDenied


class BothStaffGerentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                planner = Planner.objects.get(user=request.user)
                if planner.is_gerent is True and planner.is_staff is True:
                    return super().dispatch(request, *args, **kwargs)
                else:
                    raise PermissionDenied

            except Planner.DoesNotExist:
                raise PermissionDenied
        else:
            raise PermissionDenied
