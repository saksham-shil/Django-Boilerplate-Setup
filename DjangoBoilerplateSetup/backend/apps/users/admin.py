from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "full_name", "get_role_display", "is_active", "created_at")
    list_filter = ("is_active", "is_staff", "groups", "created_at")
    search_fields = ("email", "full_name")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    
    def get_role_display(self, obj):
        """Display user's role from group membership"""
        return obj.role or "No Role"
    get_role_display.short_description = "Role"

    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return self.model.all_objects.all()
    

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
            "fields": (
                "full_name",
                "contact_number",
            )
        }),
        

        (_("Important dates"), {
            "fields": (
                "last_login",
                "created_at",
                "updated_at",
                "deleted_at",
            )
        }),

        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
    )
    
    # Field layout when creating a new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "full_name",
                "contact_number",
                "groups",
                "password1",
                "password2",
            ),
        }),
    )

admin.site.register(Permission)