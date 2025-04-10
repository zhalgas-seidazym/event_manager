from django.urls import path
from . import views

urlpatterns = [
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
