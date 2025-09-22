from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Setup basic groups and permissions for the Django boilerplate'

    def handle(self, *args, **options):
        self.stdout.write('Creating groups and assigning permissions...')

        self.create_groups()
        self.assign_permissions()

        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and assigned permissions')
        )

    def create_groups(self):
        """Create basic required groups"""
        groups = ['user', 'admin']

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')
            else:
                self.stdout.write(f'Group already exists: {group_name}')

    def assign_permissions(self):
        """Assign permissions to each group"""

        # Admin - All permissions
        admin = Group.objects.get(name='admin')
        admin.permissions.set(Permission.objects.all())
        self.stdout.write('Assigned all permissions to admin')

        # User - Basic permissions for authenticated users
        user = Group.objects.get(name='user')
        user_perms = Permission.objects.filter(codename__in=[
            'can_view_audit_logs',
            'can_manage_profile',
        ])
        user.permissions.set(user_perms)
        self.stdout.write(f'Assigned {user_perms.count()} permissions to user')