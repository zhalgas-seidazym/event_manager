from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginController.as_view(), name='login'),
    path('logout/', views.LogoutController.as_view(), name='logout'),
    path('register/', views.RegisterController.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    path('', views.HomeView.as_view(), name='home'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('event/new/', views.EventCreateUpdateView.as_view(), name='event_new'),
    path('event/<int:pk>/update/', views.EventCreateUpdateView.as_view(), name='event_update'),
]
