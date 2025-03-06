from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginController, name = 'login'),
    path('logout/', views.logoutController, name = 'logout'),
    path('register/', views.registerController, name = 'register'),
    path('profile/', views.profile, name = 'profile'),

    path('', views.home, name = 'home'),
    path('event/<int:pk>/', views.event, name='event_detail'),
    path('event/<int:pk>/delete/', views.eventDelete, name='event_delete'),
    path('event/new/', views.eventCreateUpdate, name='event_new'),
    path('event/<int:pk>/update/', views.eventCreateUpdate, name='event_update'),
]
