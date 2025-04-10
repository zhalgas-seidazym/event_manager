from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Category, Ticket


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'status']


class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(status='approved'),
        many=True,
        write_only=True,
        required=False
    )
    new_categories = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location', 'organizer',
            'categories', 'category_ids', 'new_categories', 'cover', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'organizer', 'created_at']

    def create(self, validated_data):
        request = self.context['request']
        category_ids = validated_data.pop('category_ids', [])
        new_cats = validated_data.pop('new_categories', [])

        event = Event.objects.create(
            organizer=request.user,
            status='pending',
            **validated_data
        )

        categories = list(category_ids)

        for name in new_cats:
            name = name.strip()
            if name:
                cat, _ = Category.objects.get_or_create(name=name)
                if cat not in categories:
                    categories.append(cat)

        event.categories.set(categories)
        return event

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        new_cats = validated_data.pop('new_categories', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.status = 'pending'  # Reset status on update
        instance.save()

        categories = list(category_ids)
        for name in new_cats:
            name = name.strip()
            if name:
                cat, _ = Category.objects.get_or_create(name=name)
                if cat not in categories:
                    categories.append(cat)

        instance.categories.set(categories)
        return instance



class TicketSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'user', 'event', 'booked_at']
        read_only_fields = ['booked_at']
