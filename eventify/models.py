from django.core.files.storage import default_storage
from django.db import models
from django.contrib.auth.models import User
from enum import Enum

class EventStatusEnum(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    @classmethod
    def choices(cls):
        return [(member.value, member.name.title().replace("_", " ")) for member in cls]

class Event(models.Model):
    # STATUS_CHOICES = [
    #     ('pending', 'Pending Approval'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected'),
    # ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    categories = models.ManyToManyField('Category', related_name="events")
    cover = models.ImageField(null=True, blank=True, storage=default_storage)
    status = models.CharField(
        max_length=10,
        choices=EventStatusEnum.choices(),
        default=EventStatusEnum.PENDING.value
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status_display(self):
        return self.get_status_display()

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket: {self.user.username} -> {self.event.title}"

class Category(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Default: needs approval

    def __str__(self):
        return self.name
