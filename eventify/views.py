from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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

def event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.status != 'approved':
        return HttpResponse('Access denied')

    if request.method == "POST":
        Ticket.objects.create(
            user = request.user,
            event = event,
        )
        return redirect('event_detail', pk=pk)

    return render(request, 'eventify/event.html')

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
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            categories = []
            for category in form.cleaned_data['categories']:
                topic, created_at = Category.objects.get_or_create(name = category)
                categories.append(topic)
            for category in [c.strip() for c in request.POST.get('new_categories').split(",") if c.strip()]:
                topic, created_at = Category.objects.get_or_create(name=category)
                categories.append(topic)
            updated_event = form.save(commit=False)
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
