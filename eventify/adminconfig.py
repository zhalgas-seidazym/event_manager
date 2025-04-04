from django.contrib.admin.apps import AdminConfig

class EventifyAdminConfig(AdminConfig):
    default_site = 'event_manager.admin.EventifyAdmin'