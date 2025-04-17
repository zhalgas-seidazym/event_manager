from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .api_views import *

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tickets', TicketViewSet, basename='ticket')

urlpatterns = [
    path('api/', include(router.urls)),
    # Аутентификация
    path('api/auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('api/auth/profile/', ProfileAPIView.as_view(), name='api-profile'),

    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Главная страница
    path('', views.HomeView.as_view(), name='home'),

    # Детали ивента
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    # Создание/редактирование ивента (одна вьюха для обоих случаев)
    path('event/new/', views.EventFormView.as_view(), name='event_new'),
    path('event/<int:pk>/update/', views.EventFormView.as_view(), name='event_update'),

    # Удаление ивента
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
]
