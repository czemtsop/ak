from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile, Announcement, Message, Minute


# Define an inline admin descriptor for Profile model
# which acts a bit like a singleton
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active') # Add is_active
    list_filter = ('is_staff', 'is_active') # Add is_active to filter
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Announcement)
admin.site.register(Message)
admin.site.register(Minute)