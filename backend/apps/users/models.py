from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.db import models
from apps.common.models import BaseModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    contact_number = models.CharField(max_length=10)

    # REVIEW_STATUS_CHOICES = [
    #     ('pending', 'Pending'),
    #     ('reviewed', 'Reviewed'),
    # ]

    # review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending')
    # reviewed_at = models.DateTimeField(blank=True, null=True)
    # reviewed_by = models.ForeignKey(
    #     'self',
    #     on_delete=models.RESTRICT,
    #     null=True,
    #     blank=True,
    #     related_name='reviewed_users',
    # )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        permissions = [
            ("can_access_corporate_dashboard", "Can access corporate dashboard"),
            ("can_access_common_dashboard", "Can access common dashboard"),
            ("can_view_users", "Can view users"),
            ("can_manage_users", "Can manage users"),
            ("can_view_audit_logs", "Can view audit logs"),
            ("can_manage_profile", "Can manage profile"),
        ]
        indexes = [
            models.Index(fields=["email"], name="user_email_idx"),
        ]

    @property
    def role(self):
        """Backward compatibility - get role from primary group"""
        primary_group = self.groups.first()
        return primary_group.name if primary_group else None

    def set_role(self, role_name):
        """Helper method to set user's role via group"""
        try:
            group = Group.objects.get(name=role_name)
            self.groups.clear()
            self.groups.add(group)
        except Group.DoesNotExist:
            raise ValueError(f"Group {role_name} does not exist")

    def __str__(self):
        return f"{self.id}. {self.email} - ({self.role})"


