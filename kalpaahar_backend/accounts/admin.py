from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Columns shown in the list view
    list_display   = ["email", "name", "phone", "is_active", "email_verified", "is_staff", "created_at"]
    list_filter    = ["is_active", "email_verified", "is_staff"]
    search_fields  = ["email", "name", "phone"]
    ordering       = ["-created_at"]
    readonly_fields = ["created_at", "last_login", "date_joined"]

    # Override fieldsets so email is prominent
    fieldsets = (
        ("Login",       {"fields": ("email", "password")}),
        ("Profile",     {"fields": ("name", "phone", "email_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps",  {"fields": ("created_at", "last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "name", "phone", "password1", "password2", "is_active", "is_staff"),
        }),
    )
