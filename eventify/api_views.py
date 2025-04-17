# views_api.py
from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Event, Ticket, Category
from .serializers import EventSerializer, TicketSerializer, UserSerializer

# ----------- AUTH -----------
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

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


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({'message': 'Logged in successfully!'})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully!'})


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ----------- EVENT -----------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


# ----------- TICKET -----------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('id')
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
