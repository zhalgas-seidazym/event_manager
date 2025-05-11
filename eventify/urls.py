from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views
from .api_views import *

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')


urlpatterns = [
    path('api/', include(router.urls)),
    # Аутентификация
    path('api/auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # логин
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление токена
    path('api/auth/profile/', ProfileAPIView.as_view(), name='api-profile'),

    # Events
    path('api/events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('api/events/<int:pk>/', EventDetailAPIView.as_view(), name='event-detail'),

    # Add the schema view
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI to view the API documentation
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

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

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),  # <-- This line
    ] + urlpatterns
