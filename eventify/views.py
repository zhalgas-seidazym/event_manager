from datetime import datetime
from io import BytesIO
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, DetailView, DeleteView, TemplateView

from .forms import MyUserCreationForm, EventForm
from .models import *


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'eventify/login_register.html', {'page': 'login'})

    def post(self, request):
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

        return render(request, 'eventify/login_register.html', {'page': 'login'})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('home')


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = MyUserCreationForm()
        return render(request, 'eventify/login_register.html', {'form': form})

    def post(self, request):
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
        return render(request, 'eventify/login_register.html', {'form': form})


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'eventify/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['created_events'] = Event.objects.filter(organizer=user)
        context['user_tickets'] = Ticket.objects.filter(
            user=user,
            event__status="approved",
            event__categories__status="approved"
        ).distinct()
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'eventify/event.html'
    context_object_name = 'event'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.status != 'approved' and event.organizer != request.user:
            return HttpResponse('Access denied')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        event = self.get_object()
        Ticket.objects.get_or_create(user=request.user, event=event)
        return redirect('event_detail', pk=event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['has_ticket'] = Ticket.objects.filter(user=self.request.user, event=self.object)
        return context


class EventFormView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['eventify.can_change_event', 'eventify.can_add_event']

    def get(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk) if pk else None
        form = EventForm(instance=event)
        return render(request, 'eventify/event_form.html', {'form': form, 'instance': event})

    def post(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk) if pk else None

        if event and event.organizer != request.user:
            return HttpResponse("Access Denied")

        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            categories = []
            for category in form.cleaned_data['categories']:
                topic, _ = Category.objects.get_or_create(name=category)
                categories.append(topic)

            for category in [c.strip() for c in request.POST.get('new_categories', '').split(",") if c.strip()]:
                topic, _ = Category.objects.get_or_create(name=category)
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

            messages.success(
                request,
                f'Event "{updated_event}" was {"updated" if event else "created"}.'
            )
            return redirect('event_detail', pk=updated_event.pk)

        return render(request, 'eventify/event_form.html', {'form': form, 'instance': event})


class EventDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Event
    template_name = 'eventify/delete_event.html'
    success_url = reverse_lazy('home')
    permission_required = 'eventify.can_delete_event'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if request.user != event.organizer:
            return HttpResponse("Access Denied")
        return super().dispatch(request, *args, **kwargs)


class HomeView(View):
    def get(self, request):
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
