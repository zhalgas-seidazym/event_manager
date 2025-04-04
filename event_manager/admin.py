from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


class EventifyAdmin(admin.AdminSite):
      site_header = "Eventify Administration Portal"
      site_title = "Eventify Administration Portal"
      index_title = "Eventify Administration"

      def profile_view(self, request):
          user = request.user

          if user.is_authenticated:
              profile_info = f"""
                  Username: {user.username}
                  Email: {user.email}
                  First Name: {user.first_name}
                  Last Name: {user.last_name}
                  Date Joined: {user.date_joined}
                  Last Login: {user.last_login}
                  """
              return HttpResponse(profile_info, content_type="text/plain")
          else:
              return HttpResponse("You must be logged in to view your profile.", content_type="text/plain")

      def get_urls(self):
            urls = super().get_urls()
            url_patterns = [
                path("admin_profile", self.admin_view(self.profile_view))
            ]
            return url_patterns + urls
