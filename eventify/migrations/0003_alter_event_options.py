# Generated by Django 5.1.6 on 2025-03-13 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventify', '0002_category_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'permissions': [('can_edit_event', 'Can edit events')]},
        ),
    ]
