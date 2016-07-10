from django.contrib import admin

from .models import CommunityUser, UserProfile

# Register your models here.
admin.site.register(CommunityUser)
admin.site.register(UserProfile)
