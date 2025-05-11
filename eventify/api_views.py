# views_api.py
from rest_framework import viewsets, permissions, generics, status
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.contrib.auth import authenticate, login, logout

from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer, UserSerializer
from .permissions import IsAdminOrReadOnly


# ----------- AUTH -----------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserSerializer,  # You can customize request schema if necessary
        responses={201: OpenApiResponse('User successfully registered'),
                   400: OpenApiResponse('Error in registration')}
    )
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data.get('email', ''),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
            )
            return Response({'message': 'Registered successfully!'}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ProfileAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        responses={200: UserSerializer}  # Here you describe the response schema
    )
    def get_object(self):
        # Return the current user (the authenticated user)
        return self.request.user

# ----------- EVENT -----------
class EventListCreateAPIView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        request=EventSerializer,  # Describe the request schema for POST
        responses={200: EventSerializer, 201: EventSerializer},  # Possible responses
    )
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        responses={200: EventSerializer, 404: OpenApiResponse('Event not found')}
    )
    def get_object(self):
        # Get event by ID
        return super().get_object()

# ----------- TICKET -----------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('id')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TicketSerializer,  # Describe the request schema for POST
        responses={200: TicketSerializer, 201: TicketSerializer},
    )
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
