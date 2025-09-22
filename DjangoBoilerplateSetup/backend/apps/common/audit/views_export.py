from typing import ClassVar

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.common.audit.services import (
    apply_audit_log_filters,
    generate_csv_response,
    get_audit_logs_for_export,
)
from apps.common.permissions import HasRequiredPermissions


class AuditLogCSVExportView(APIView):
    """
    CSV export view for audit logs with filtering support.
    Returns a direct CSV file download with specific field order and formatting.
    """
    permission_classes: ClassVar = [IsAuthenticated, HasRequiredPermissions]
    required_permissions: ClassVar = ['users.can_view_audit_logs']
    
    def get(self, request):
        """Export audit logs as CSV with applied filters"""
        
        # Get optimized queryset
        queryset = get_audit_logs_for_export()
        
        # Apply filters
        queryset = apply_audit_log_filters(request, queryset)
        
        # Generate and return CSV response
        return generate_csv_response(queryset)