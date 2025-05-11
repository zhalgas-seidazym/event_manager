from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Ticket, Category

# ---------- USER ----------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

    def validate_username(self, value):
        # check for username uniqueness
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        # check for correct email format
        if not value or "@" not in value:
            raise serializers.ValidationError("Invalid email address.")
        return value


# ---------- CATEGORY ----------
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)

    def validate_name(self, value):
        # check for name is not null
        if not value.strip():
            raise serializers.ValidationError("Category name cannot be empty.")
        # check for unique name
        if Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value


# ---------- EVENT ----------
class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    categories = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Category.objects.all()
    )
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location', 'organizer',
            'categories', 'cover', 'created_at', 'status_display'
        ]

    def get_status_display(self, obj):
        status_display = obj.status_display  # Get the computed value from the model

        if status_display == 'Pending':
            return 'This event is waiting for approval'
        elif status_display == 'Approved':
            return 'Event is confirmed'
        elif status_display == 'Rejected':
            return 'Event has been canceled'
        return status_display

    def validate_title(self, value):
        # check for unique title
        if Event.objects.filter(title=value).exists():
            raise serializers.ValidationError("Event with this title already exists.")
        return value

    def validate_date(self, value):
        # check for date is not in past
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value



# ---------- TICKET ----------
class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Ticket
        fields = ['id', 'event', 'user', 'booked_at']

    def validate_event(self, value):
        # check for past event
        if value.date < timezone.now():
            raise serializers.ValidationError("Cannot book tickets for past events.")
        return value
