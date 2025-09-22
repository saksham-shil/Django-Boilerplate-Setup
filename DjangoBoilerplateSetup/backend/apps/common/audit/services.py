import csv
from datetime import datetime
from typing import Any

from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse

from .constants import ACTION_DESCRIPTIONS
from .models import AuditLog


def log_audit_event(action, module, user=None, user_role=None, status='success', action_details='',
                   from_status='', to_status='', changed_fields=None, related_object_id=None):
    """
    Log audit event for tracking user actions and system changes

    Args:
        action: Action key that corresponds to ACTION_CHOICES (e.g., "user_created")
        module: Module name from MODULE_CHOICES (e.g., "users")
        user: User who performed the action
        user_role: User role - auto-detected if not provided
        status: 'success', 'failure', or 'warning'
        action_details: Additional details (e.g., "Created user 'john@example.com'")
        from_status: Previous status (for status changes)
        to_status: New status (for status changes)
        changed_fields: Dictionary of changed fields
        related_object_id: ID of related object for future extensibility
    """
    
    # Auto-detect user role if not provided
    if user and not user_role:
        user_role = getattr(user, 'role', '')
    
    audit_entry = AuditLog.objects.create(
        action=action,
        action_details=action_details,
        performed_by=user,
        performed_by_role=user_role,
        module=module,
        status=status,
        from_status=from_status,
        to_status=to_status,
        changed_fields=changed_fields or {},
        related_object_id=related_object_id
    )
    
    return audit_entry


def apply_audit_log_filters(request: HttpRequest, queryset: QuerySet) -> QuerySet:
    """
    Apply search and filter parameters to the audit log queryset.
    
    Supported filters:
    - search: Search in action and user full name
    - user: Filter by user ID
    - start_date: Filter from date (YYYY-MM-DD)
    - end_date: Filter to date (YYYY-MM-DD)
    """
    # Search filter - searches on action and user's full name
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(action__icontains=search) |
            Q(performed_by__full_name__icontains=search)
        )
    
    # User filter - filter by user_id
    user_id = request.GET.get('user')
    if user_id:
        try:
            queryset = queryset.filter(performed_by_id=int(user_id))
        except (ValueError, TypeError):
            pass
    
    # Date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__gte=start_datetime.date())
        except ValueError:
            pass
    
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__lte=end_datetime.date())
        except ValueError:
            pass
    
    return queryset


def format_audit_log_for_csv(audit_log: AuditLog) -> list[Any]:
    """
    Format a single audit log record for CSV output.

    Returns list with fields in order:
    [Timestamp, Action, Action Details, User Role, User Full Name, Module, Status, Object ID]
    """
    # Format timestamp as YYYY-MM-DD HH:MM:SS
    timestamp = audit_log.created_at.strftime('%Y-%m-%d %H:%M:%S')

    # Get human-readable action description from ACTION_DESCRIPTIONS
    action_display = ACTION_DESCRIPTIONS.get(
        audit_log.action,
        audit_log.get_action_display()
    )

    # Action details (empty string if null)
    action_details = audit_log.action_details or ''

    # User information (empty string if null)
    user_role = audit_log.performed_by_role or ''
    user_name = audit_log.performed_by.full_name if audit_log.performed_by else ''

    # Module display name
    module_display = audit_log.get_module_display()

    # Status and related object info
    status = audit_log.get_status_display()
    object_id = audit_log.related_object_id or ''

    return [
        timestamp,
        action_display,
        action_details,
        user_role,
        user_name,
        module_display,
        status,
        object_id
    ]


def generate_csv_response(queryset: QuerySet) -> HttpResponse:
    """
    Generate CSV response with exact header order and field mapping.
    
    Args:
        queryset: Filtered audit log queryset
        
    Returns:
        HttpResponse with CSV content
    """
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'audit_logs_export_{timestamp}.csv'
    
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Write CSV headers
    headers = [
        'Timestamp',
        'Action',
        'Action Details',
        'User Role',
        'User Full Name',
        'Module',
        'Status',
        'Object ID'
    ]
    writer.writerow(headers)
    
    # Write data rows
    for audit_log in queryset:
        row = format_audit_log_for_csv(audit_log)
        writer.writerow(row)
    
    return response


def get_audit_logs_for_export() -> QuerySet:
    """
    Get optimized audit logs queryset for export with related objects.

    Returns:
        QuerySet with select_related optimization for foreign keys
    """
    return AuditLog.objects.select_related('performed_by').all() 