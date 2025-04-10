from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Q


from .models import Event, Category, Ticket
from .serializers import EventSerializer, CategorySerializer, TicketSerializer, UserSerializer
from django.shortcuts import get_object_or_404


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Event.objects.all()

    def get_queryset(self):
        queryset = Event.objects.filter(status='approved', categories__status='approved').distinct()

        search = self.request.query_params.get('q')
        category = self.request.query_params.get('category')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )

        if category:
            queryset = queryset.filter(categories__name__icontains=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def perform_update(self, serializer):
        event = self.get_object()
        if event.organizer != self.request.user:
            raise PermissionDenied("You are not allowed to update this event.")
        serializer.save()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            user=self.request.user,
            event__status='approved',
            event__categories__status='approved'
        ).distinct()

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        ticket, created = Ticket.objects.get_or_create(user=request.user, event=event)
        serializer = self.get_serializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)



class AuthView(APIView):
    def post(self, request):
        action = request.data.get('action')
        username = request.data.get('username')
        password = request.data.get('password')

        if action == "login":
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return Response({'detail': 'Logged in'})
            return Response({'detail': 'Invalid credentials'}, status=400)

        elif action == "logout":
            logout(request)
            return Response({'detail': 'Logged out'})

        return Response({'detail': 'Invalid action'}, status=400)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        created_events = Event.objects.filter(organizer=user)
        tickets = Ticket.objects.filter(user=user, event__status='approved', event__categories__status='approved').distinct()

        return Response({
            'user': UserSerializer(user).data,
            'created_events': EventSerializer(created_events, many=True).data,
            'tickets': TicketSerializer(tickets, many=True).data
        })
