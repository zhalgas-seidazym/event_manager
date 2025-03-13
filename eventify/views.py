from datetime import datetime
from io import BytesIO
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MyUserCreationForm, EventForm
from .models import *


def loginController(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            User.objects.get(username = username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    context = {'page': page}
    return render(request, 'eventify/login_register.html', context)

@login_required(login_url='login')
def logoutController(request):
    logout(request)
    return redirect('home')

def registerController(request):
    if request.user.is_authenticated:
        return redirect('home')

    page = 'register'

    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {'form': form}
    return render(request, 'eventify/login_register.html', context)


@login_required(login_url='login')
def profile(request):
    user = request.user

    created_events = Event.objects.filter(organizer=user)

    user_tickets = Ticket.objects.filter(
        user=user,
        event__status="approved",
        event__categories__status="approved"
    ).distinct()

    context = {
        "created_events": created_events,
        "user_tickets": user_tickets,
    }
    return render(request, "eventify/profile.html", context)

def event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    has_ticket = None
    if event.status != 'approved' and event.organizer != request.user:
        return HttpResponse('Access denied')

    if request.method == "POST":
        Ticket.objects.get_or_create(user=request.user, event=event)
        return redirect('event_detail', pk=pk)

    if request.user.is_authenticated:
        has_ticket = Ticket.objects.filter(user=request.user, event = event)

    return render(request, 'eventify/event.html', {'event': event, 'has_ticket': has_ticket})

@permission_required(['eventify.can_change_event', 'eventify.can_add_event'])
@login_required(login_url='login')
def eventCreateUpdate(request, pk = None):
    if pk is not None:
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            return HttpResponse("Access Denied")
    else:
        event = None

    method = request.method

    if method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            categories = []
            for category in form.cleaned_data['categories']:
                topic, created_at = Category.objects.get_or_create(name = category)
                categories.append(topic)
            for category in [c.strip() for c in request.POST.get('new_categories').split(",") if c.strip()]:
                topic, created_at = Category.objects.get_or_create(name=category)
                categories.append(topic)

            cover = form.cleaned_data.get("cover")

            updated_event = form.save(commit=False)
            updated_event.organizer = request.user
            updated_event.status = 'pending'

            if cover and not hasattr(cover, "path"):
                image = Image.open(cover)
                image.thumbnail((300, 300))
                image_data = BytesIO()
                image.save(fp=image_data, format=cover.image.format)
                image_file = ImageFile(image_data)
                updated_event.cover.save(cover.name, image_file)

            updated_event.save()
            updated_event.categories.set(categories)
            if event is not None:
                messages.success(
                    request, 'Event "{}" was created.'.format(updated_event)
                )
            else:
                messages.success(
                    request, 'Event "{}" was updated.'.format(updated_event)
                )

            return redirect('event_detail', updated_event.pk)
    else:
        form = EventForm(instance=event)

    return render(
        request,
        'eventify/event_form.html',
        {
            'form': form,
            'instance': event,
        }
    )

@permission_required('eventify.can_delete_event')
@login_required(login_url='login')
def eventDelete(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.user != event.organizer:
        return HttpResponse("Access Denied")

    if request.method == 'POST':
        event.delete()
        return redirect('home')
    return render(request, 'eventify/delete_event.html')

def home(request):
    q = request.GET.get('q', request.session.get('q', ''))
    categ = request.GET.get('category', request.session.get('category', ''))

    request.session['q'] = q
    request.session['category'] = categ

    categories = Category.objects.filter(status='approved')

    query = Q(status='approved') & Q(date__gt=datetime.now()) & Q(categories__status='approved')

    if q:
        query &= Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)

    if categ:
        query &= Q(categories__name__icontains=categ)

    events = Event.objects.filter(query).distinct()

    return render(request, 'eventify/home.html', {
        'categories': categories,
        'events': events,
    })
