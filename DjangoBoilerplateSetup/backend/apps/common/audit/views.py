from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime
from apps.common.permissions import HasRequiredPermissions
from apps.common.api_responses.responses import success_response
from apps.common.audit.models import AuditLog
from apps.common.audit.serializers import AuditLogSerializer
from apps.common.api_responses.constants import SUCCESS_AUDIT_LOGS_RETRIEVED
from apps.common.pagination import apply_manual_pagination
from apps.common.audit.constants import ACTION_DESCRIPTIONS


class AuditLogList(APIView):
    permission_classes = [IsAuthenticated, HasRequiredPermissions]
    required_permissions = ['users.can_view_audit_logs']

    def get(self, request):
        # Start with all audit logs
        queryset = AuditLog.objects.select_related('performed_by').all()
        
        # Apply filters
        queryset = self._apply_filters(request, queryset)
        
        # Apply pagination
        pagination_result = apply_manual_pagination(queryset, request)
        
        # Serialize the data
        serializer = AuditLogSerializer(pagination_result['data'], many=True)
        
        return success_response(
            message_code=SUCCESS_AUDIT_LOGS_RETRIEVED,
            data={
                'audit_logs': serializer.data,
                'total': pagination_result['total'],
                'next': pagination_result['next'],
                'previous': pagination_result['previous']
            }
        )
    
    def _apply_filters(self, request, queryset):
        """Apply search and filter parameters to the queryset"""

        # Search filter - searches on action (both raw and human-readable) and action details
        search = request.GET.get('search')
        if search:
            search = search.strip()
        if search:
            # Create Q objects for searching human-readable descriptions
            description_filters = Q()
            for raw_action, description in ACTION_DESCRIPTIONS.items():
                if search.lower() in description.lower():
                    description_filters |= Q(action=raw_action)

            queryset = queryset.filter(
                Q(action__icontains=search) |  # Raw action search
                Q(action_details__icontains=search) |  # Action details search
                description_filters  # Human-readable action description search
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