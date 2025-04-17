from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Ticket, Category

# ---------- USER ----------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# ---------- CATEGORY ----------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# ---------- EVENT ----------
class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    categories = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location', 'organizer',
            'categories', 'cover', 'created_at'
        ]


# ---------- TICKET ----------
class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'user', 'booked_at']
