from rest_framework import serializers
from apps.common.audit.models import AuditLog
from apps.common.audit.constants import ACTION_DESCRIPTIONS


class AuditLogSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField()
    performed_by = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'action',
            'action_details',
            'performed_by',
            'module',
            'from_status',
            'to_status',
            'changed_fields',
            'created_at'
        ]
    
    def get_action(self, obj):
        """Get the human-readable action description from our dictionary."""
        if not obj.action:
            return obj.action
        return ACTION_DESCRIPTIONS.get(obj.action, obj.get_action_display())
    
    def get_performed_by(self, obj):
        """Get user details for performed_by field"""
        if not obj.performed_by:
            return None
            
        user = obj.performed_by
        return {
            'user_id': user.id,
            'user_full_name': user.full_name,
            'user_role': user.role,
            'user_email': user.email,
            'user_contact_number': user.contact_number
        }