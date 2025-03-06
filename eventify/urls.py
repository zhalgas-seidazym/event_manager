from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginController, name = 'login'),
    path('logout/', views.logoutController, name = 'logout'),
    path('register/', views.registerController, name = 'register'),


]
