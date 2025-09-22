from apps.common.models import BaseModel
from django.db import models
from apps.users.models import User

class AuditLog(BaseModel):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('warning', 'Warning'),
    ]
    
    MODULE_CHOICES = [
        ('users', 'Users'),
        # Add your project-specific modules here:
        # ('products', 'Products'),
        # ('orders', 'Orders'),
        # ('payments', 'Payments'),
    ]
    
    ACTION_CHOICES = [
        # User Management
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),

        # Add new action keys as needed, following the pattern: module_action_result
        # Example:
        # ('product_created', 'Product Created'),
        # ('order_placed', 'Order Placed'),
    ]
    
    # Machine-readable action key for querying and analytics
    action = models.CharField(max_length=200, choices=ACTION_CHOICES)
    action_details = models.TextField(blank=True)
    
    # USER column - User + Role
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    performed_by_role = models.CharField(max_length=50, blank=True)
    
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    
    # Project-specific fields (optional)
    from_status = models.CharField(max_length=100, blank=True)
    to_status = models.CharField(max_length=100, blank=True)
    changed_fields = models.JSONField(default=dict, blank=True)
    
    # Future extensibility field
    related_object_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="For future purposes - not currently used"
    )
    
    class Meta:
        ordering = ['-created_at']
        
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['module', 'created_at']),
            models.Index(fields=['performed_by', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.created_at.strftime('%d/%m/%Y %H:%M')} - {self.action}" 