from datetime import datetime
from io import BytesIO
from PIL import Image
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.files.images import ImageFile
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .forms import MyUserCreationForm, EventForm
from .models import Event, Ticket, Category


# Login and Logout Views

class LoginController(View):
    template_name = 'eventify/login_register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name, {'page': 'login'})

    def post(self, request):
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            return render(request, self.template_name, {'page': 'login'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, self.template_name, {'page': 'login'})

# Logout View (Using Django's built-in LogoutView)
class LogoutController(LogoutView):
    next_page = '/'

# Register View

class RegisterController(View):
    template_name = 'eventify/login_register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = MyUserCreationForm()
        return render(request, self.template_name, {'form': form, 'page': 'register'})

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
            return render(request, self.template_name, {'form': form, 'page': 'register'})

# Profile View

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'eventify/profile.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        created_events = Event.objects.filter(organizer=user)
        user_tickets = Ticket.objects.filter(
            user=user,
            event__status="approved",
            event__categories__status="approved"
        ).distinct()

        return {
            'created_events': created_events,
            'user_tickets': user_tickets,
        }

# Event View (Detail)

class EventDetailView(DetailView):
    model = Event
    template_name = 'eventify/event.html'
    context_object_name = 'event'

    def get(self, request, *args, **kwargs):
        event = self.get_object()
        if event.status != 'approved' and event.organizer != request.user:
            return HttpResponse('Access denied')

        has_ticket = None
        if request.user.is_authenticated:
            has_ticket = Ticket.objects.filter(user=request.user, event=event)

        return self.render_to_response({'event': event, 'has_ticket': has_ticket})

    def post(self, request, *args, **kwargs):
        event = self.get_object()
        Ticket.objects.get_or_create(user=request.user, event=event)
        return redirect('event_detail', pk=event.pk)

# Event Create/Update View

# Event Create View (No UpdateView inheritance)
class EventCreateUpdateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'eventify/event_form.html'
    permission_required = ['eventify.can_change_event', 'eventify.can_add_event']

    def form_valid(self, form):
        event = form.save(commit=False)
        event.organizer = self.request.user
        event.status = 'pending'

        categories = []
        for category in form.cleaned_data['categories']:
            topic, created_at = Category.objects.get_or_create(name=category)
            categories.append(topic)

        new_categories = [c.strip() for c in self.request.POST.get('new_categories').split(",") if c.strip()]
        for category in new_categories:
            topic, created_at = Category.objects.get_or_create(name=category)
            categories.append(topic)

        cover = form.cleaned_data.get("cover")

        if cover and not hasattr(cover, "path"):
            image = Image.open(cover)
            image.thumbnail((300, 300))
            image_data = BytesIO()
            image.save(fp=image_data, format=cover.image.format)
            image_file = ImageFile(image_data)
            event.cover.save(cover.name, image_file)

        event.save()
        event.categories.set(categories)

        messages.success(self.request, f'Event "{event}" was created.')

        return redirect('event_detail', event.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['instance'] = self.object
        return context


# Event Delete View

class EventDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'eventify/delete_event.html'
    success_url = '/'

    permission_required = 'eventify.can_delete_event'

    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        if self.request.user != event.organizer:
            raise Http404("Access Denied")
        return event

# Home View

class HomeView(TemplateView):
    template_name = 'eventify/home.html'

    def get_context_data(self, **kwargs):
        q = self.request.GET.get('q', self.request.session.get('q', ''))
        categ = self.request.GET.get('category', self.request.session.get('category', ''))

        self.request.session['q'] = q
        self.request.session['category'] = categ

        categories = Category.objects.filter(status='approved')

        query = Q(status='approved') & Q(date__gt=datetime.now()) & Q(categories__status='approved')

        if q:
            query &= Q(title__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)

        if categ:
            query &= Q(categories__name__icontains=categ)

        events = Event.objects.filter(query).distinct()

        return {
            'categories': categories,
            'events': events,
        }
