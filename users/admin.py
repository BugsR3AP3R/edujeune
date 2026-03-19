from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil EduJeunes', {'fields': ('role', 'bio', 'avatar', 'country', 'points')}),
    )
    list_display  = ['username', 'email', 'first_name', 'last_name', 'role', 'points', 'date_joined']
    list_filter   = ['role', 'is_active', 'country']
    search_fields = ['username', 'email', 'first_name', 'last_name']
