from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from trainWellApp.forms import BookingForm
from trainWellApp.models import Planner


@login_required(login_url="/login/")
def booking_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            user = get_object_or_404(Planner, Q(id=request.user.id))
            book.user = user
            book.save()
            return redirect('trainwell:index')
    else:
        form = BookingForm()
    return render(request, 'trainWellApp/add_book.html', context={'form': form})
