from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import json
from trainWellApp.forms import EventForm
from trainWellApp.models import Selection


def addEvent(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event_form.save()
            return redirect(reverse('trainwell:dashboard'))

    else:
        event_form = EventForm()

    args = {'event_form': event_form}
    return render(request, 'trainWellApp/add_event.html', args)


def _get_affected_bookings(request, init, end, places):
    print(init, end, places)
    selection = Selection.objects.filter(datetime_init__range=[init, end],
                                         booking__planner__user_id=request.user.id,
                                         place_id__in=places,
                                         booking__is_deleted=False)
    bookinglist = {}
    for s in selection:
        if s.booking in bookinglist:
            bookinglist[s.booking].append(s)
        else:
            bookinglist[s.booking] = [s]

    return bookinglist


def ajax_affected(request):
    list_places = []
    ajax_created = request.GET.get('created').split('-')
    ajax_limit_date = request.GET.get('limit_date').split('-')
    ajax_places = request.GET.get('places').split(',')
    init = datetime(int(ajax_created[0]), int(ajax_created[1]), int(ajax_created[2])).date()
    end = datetime(int(ajax_limit_date[0]), int(ajax_limit_date[1]), int(ajax_limit_date[2])).date()
    for place in ajax_places:
        if place:
            list_places.append(int(place))
    result = _get_affected_bookings(request, init, end, list_places)
    json_data = []

    for key, value in result.items():
        json_data.append([str(key.planner.user.first_name) , str(key.planner.user.last_name),str(key.event.name), str(key.phone_number), str(key.name)])

    return JsonResponse(json.dumps(json_data),safe=False)
