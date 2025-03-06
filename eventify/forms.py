from datetime import date

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import Event, Category


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'categories']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'datepicker',
                    'id': 'datepicker',
                    'min': date.today().isoformat()
                }
            ),
        }

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(status='approved'),  # Фильтруем только approved
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),  # Отображение в виде чекбоксов
    )