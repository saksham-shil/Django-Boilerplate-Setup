from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.db.models import Q
from django.core.files.uploadedfile import UploadedFile
from apps.common.permissions import HasRequiredPermissions
from apps.common.api_responses.mixins import StandardResponseMixin
from apps.common.api_responses.exception_handler import APIError
from apps.common.api_responses.constants import (
    ERROR_CANNOT_DEACTIVATE_REFERENCED_ITEM,
    SUCCESS_NO_DATA_FOUND,
    ERROR_INVALID_IMAGE_FORMAT,
    ERROR_INVALID_DOCUMENT_FORMAT,
    ERROR_MASTER_DATA_NOT_FOUND,
    ERROR_INPUT
)
from apps.common.pagination import apply_manual_pagination


class BaseMasterListCreateView(APIView, StandardResponseMixin):
    """
    Base class for master data list/create operations.
    
    Features:
    - Method-based permissions (different for GET vs POST)
    - Multiple value filtering for all fields
    - Optional file upload support
    - Search functionality
    - Pagination
    - Specific message codes
    """
    permission_classes = [IsAuthenticated, HasRequiredPermissions]
    
    # Must be overridden in child classes
    model = None
    serializer_class = None
    list_success_code = None
    create_success_code = None
    
    # Permission configuration (can be overridden per API)
    view_permissions = ['master_data.can_view_master_data']  # For GET requests
    manage_permissions = ['master_data.can_manage_master_data']  # For POST requests
    
    # Optional file upload support
    file_fields = []  # e.g., ['logo', 'document']
    file_validation = {}  # e.g., {'logo': 'image', 'document': 'document'}
    
    # Filtering and search configuration
    multiple_filter_fields = []  # ALL filterable fields go here (supports single + multiple)
    search_fields = []           # Fields for search (icontains)
    ordering = ['-created_at']   # Default ordering
    
    @property
    def required_permissions(self):
        """Dynamic permissions based on HTTP method"""
        if self.request.method == 'GET':
            return self.view_permissions
        elif self.request.method == 'POST':
            return self.manage_permissions
        return []
    
    def get_queryset(self):
        """Get base queryset - override for optimization"""
        if not self.model:
            raise NotImplementedError("model must be defined")
        return self.model.objects.all()
    
    def parse_multiple_values(self, request, field_name):
        """
        Parse multiple values from query parameters.
        
        Supports format: ?field=1&field=2&field=3
        
        Args:
            request: Django request object
            field_name: Field name to parse
            
        Returns:
            list: List of values or empty list
        """
        # Get all values for the field name
        if hasattr(request, 'query_params'):
            param_values = request.query_params.getlist(field_name)
        else:
            param_values = request.GET.getlist(field_name)
        
        # Convert to integers if possible (for ID fields)
        processed_values = []
        for value in param_values:
            if value:  # Skip empty values
                try:
                    processed_values.append(int(value))
                except (ValueError, TypeError):
                    processed_values.append(value)
        
        return processed_values
    
    def apply_filters(self, queryset, request):
        """Apply all filters to the queryset"""
        
        # Search functionality
        search = request.query_params.get('search')
        if search and self.search_fields:
            search_query = Q()
            for field in self.search_fields:
                search_query |= Q(**{f"{field}__icontains": search})
            queryset = queryset.filter(search_query)
        
        # All filters use multiple value logic (supports single + multiple)
        for field in self.multiple_filter_fields:
            values = self.parse_multiple_values(request, field)
            if values:
                queryset = queryset.filter(**{f"{field}__in": values})
        
        # Handle parameter mappings (e.g., ?sdg_goal=1 maps to goal field)
        if hasattr(self, 'filter_parameter_mapping'):
            for param_name, field_name in self.filter_parameter_mapping.items():
                values = self.parse_multiple_values(request, param_name)
                if values:
                    queryset = queryset.filter(**{f"{field_name}__in": values})
        
        return queryset
    
    def handle_file_uploads(self, request):
        """
        Handle file uploads with validation if file_fields is configured.
        
        Returns:
            dict: Dictionary of field_name -> file_path
            
        Raises:
            ValidationError: If file validation fails
        """
        if not self.file_fields:
            return {}
        
        file_data = {}
        for field_name in self.file_fields:
            uploaded_file = request.FILES.get(field_name)
            if uploaded_file:
                # Validate file if validation is configured
                if field_name in self.file_validation:
                    validation_type = self.file_validation[field_name]
                    self._validate_uploaded_file(uploaded_file, validation_type, field_name)
                
                # Use existing file upload utility
                from apps.common.utils.media import save_uploaded_file
                file_path = save_uploaded_file(uploaded_file, folder=self.model.__name__.lower())
                file_data[field_name] = file_path
        
        return file_data
    
    def _validate_uploaded_file(self, file, validation_type, field_name):
        """
        Validate uploaded file using central validation functions.
        
        Args:
            file: Uploaded file object
            validation_type: 'image' or 'document'
            field_name: Name of the field being validated
            
        Raises:
            APIError: If validation fails (with field-specific message)
        """
        from .file_validators import validate_single_image, validate_single_document
        
        try:
            if validation_type == 'image':
                validate_single_image(file, raise_api_error=False)
            elif validation_type == 'document':
                validate_single_document(file, raise_api_error=False)
            # If validation_type is not recognized, skip validation (backward compatibility)
        except Exception as e:
            # Use specific error messages for known validation types
            if validation_type == 'image':
                raise APIError(ERROR_INVALID_IMAGE_FORMAT)
            elif validation_type == 'document':
                raise APIError(ERROR_INVALID_DOCUMENT_FORMAT)
            else:
                # For other validation errors, use generic approach
                raise APIError(ERROR_INPUT, str(e))
    
    
    
    def get(self, request):
        """Handle GET requests - requires view_permissions"""
        # Get and filter queryset
        queryset = self.get_queryset()
        queryset = self.apply_filters(queryset, request)
        queryset = queryset.order_by(*self.ordering)
        
        # Apply pagination
        paginated_result = apply_manual_pagination(queryset, request)
        
        # Serialize data
        serializer = self.serializer_class(paginated_result['data'], many=True)
        
        # Create custom response with pagination info at root level
        from apps.common.api_responses.constants import get_message
        from rest_framework.response import Response
        
        # Check if no data found
        message_code = SUCCESS_NO_DATA_FOUND if paginated_result['total'] == 0 else self.list_success_code
        
        response_data = {
            "response": "success",
            "message_code": message_code,
            "message": get_message(message_code),
            "data": serializer.data,
            "total": paginated_result['total'],
            "next": paginated_result['next'],
            "previous": paginated_result['previous']
        }
        
        return Response(response_data, status=200)
    
    def post(self, request):
        """Handle POST requests - requires manage_permissions"""
        # Extract data from {"data": {...}} format with JSON parsing for form-data
        if 'data' in request.data:
            data = request.data['data']
            # If data is a string (from form-data), parse it as JSON
            if isinstance(data, str):
                try:
                    import json
                    data = json.loads(data)
                except json.JSONDecodeError:
                    raise APIError(ERROR_INPUT, "Invalid JSON in data field")
            else:
                # Filter out file objects to avoid pickle errors during copy
                data = {
                    key: value for key, value in data.items()
                    if not isinstance(value, UploadedFile)
                }
        else:
            # Filter out file objects to avoid pickle errors during copy
            data = {
                key: value for key, value in request.data.items()
                if not isinstance(value, UploadedFile)
            }
        
        # Handle file uploads (does nothing if no file_fields configured)
        file_data = self.handle_file_uploads(request)
        data.update(file_data)
        
        # Create and validate serializer
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message_code=self.create_success_code,
                data=serializer.data
            )
        else:
            # Validation errors are handled by global exception handler
            raise serializers.ValidationError(serializer.errors)


class BaseMasterDetailView(APIView, StandardResponseMixin):
    """
    Base class for master data detail operations (GET/PUT by ID).
    
    Features:
    - Method-based permissions (different for GET vs PUT)
    - Retrieve single record
    - Update with optional file upload
    - Specific message codes
    - Query optimization support
    - Custom not found error messages
    """
    permission_classes = [IsAuthenticated, HasRequiredPermissions]
    
    # Must be overridden in child classes
    model = None
    serializer_class = None
    retrieve_success_code = None
    update_success_code = None
    
    # Permission configuration (can be overridden per API)
    view_permissions = ['master_data.can_view_master_data']  # For GET requests
    manage_permissions = ['master_data.can_manage_master_data']  # For PUT requests
    
    # Optional file upload support
    file_fields = []  # e.g., ['logo', 'document']
    file_validation = {}  # e.g., {'logo': 'image', 'document': 'document'}
    
    # Model name to error code mapping - Override in subclasses for specific models
    # Example: MODEL_NOT_FOUND_ERRORS = {'User': ERROR_USER_NOT_FOUND, 'Profile': ERROR_PROFILE_NOT_FOUND}
    MODEL_NOT_FOUND_ERRORS = {}
    
    @property
    def required_permissions(self):
        """Dynamic permissions based on HTTP method"""
        if self.request.method == 'GET':
            return self.view_permissions
        elif self.request.method == 'PUT':
            return self.manage_permissions
        return []
    
    def get_queryset(self):
        """Get base queryset - override for optimization with select_related"""
        if not self.model:
            raise NotImplementedError("model must be defined")
        return self.model.objects.all()
    
    def get_object(self, id):
        """Get object by ID with custom not found error messages"""
        try:
            return self.get_queryset().get(id=id)
        except self.model.DoesNotExist:
            # Get the model name and find corresponding error code
            model_name = self.model.__name__
            error_code = self.MODEL_NOT_FOUND_ERRORS.get(model_name)
            
            if error_code:
                raise APIError(error_code)
            else:
                # Fallback for models not in mapping
                raise APIError(ERROR_MASTER_DATA_NOT_FOUND)
    
    def handle_file_uploads(self, request):
        """
        Handle file uploads if file_fields is configured.
        
        Returns:
            dict: Dictionary of field_name -> file_path
        """
        if not self.file_fields:
            return {}
        
        file_data = {}
        for field_name in self.file_fields:
            uploaded_file = request.FILES.get(field_name)
            if uploaded_file:
                from apps.common.utils.media import save_uploaded_file
                file_path = save_uploaded_file(uploaded_file, folder=self.model.__name__.lower())
                file_data[field_name] = file_path
        
        return file_data
    
    def get(self, request, id):
        """Handle GET requests - requires view_permissions"""
        id = int(id)  # ValueError handled by global exception handler
        obj = self.get_object(id)
        
        serializer = self.serializer_class(obj)
        return self.success_response(
            message_code=self.retrieve_success_code,
            data=serializer.data
        )
    
    # Operational models that should block master data deactivation
    OPERATIONAL_MODELS = [
        # Core Business Objects
        'Project',                    # Main business objects
        'ProjectPhase',              # Project phases
        'PhaseContribution',         # Financial operations
        
        # User Profiles & Authentication
        'User',                      # Active users
        'CorporateProfile',          # Corporate user profiles  
        'GovtProfile',              # Government user profiles
        
        # Active Processes
        'ProjectInterestDetail',     # Interest expressions
        'ProjectReview',            # Review processes
        'ProjectClosureRequest',    # Closure processes  
        'PhaseAdditionRequest',     # Phase addition requests
        
        # Adoption System
        'AdoptionRequest',          # Adoption requests
        'ActiveAdoption',           # Active adoptions
        
        # Master Data Hierarchy Protection
        'Block',                     # Don't deactivate District if has active Blocks
        'Village',                   # Don't deactivate Block if has active Villages
        'SdgIndicator',             # Don't deactivate SdgGoal if has active Indicators
        'Department',               # Don't deactivate ThematicArea if has active Departments
        'FocalPoint',               # Don't deactivate Department if has active FocalPoints
        'CsrDimension',             # Don't deactivate CsrAvenue if has active Dimensions
        'ResourceDocument',         # Don't deactivate ResourceCategory if has active Documents
        
        # Master Data Models (referenced by Projects and other entities)
        'District', 'SdgGoal', 'ThematicArea', 'CsrAvenue', 'Department', 'FinancialYear', 'ResourceCategory'
    ]
    
    def has_active_references(self, instance):
        """Check if any operational objects reference this instance"""
        
        for field in instance._meta.get_fields():
            if field.is_relation and (field.one_to_many or field.many_to_many):
                related_model = field.related_model
                model_name = related_model.__name__
                
                # Only check operational models
                if model_name in self.OPERATIONAL_MODELS:
                    # Get the correct field name for the reverse relationship
                    field_name = field.get_accessor_name()
                    
                    # For all operational models, check if any objects exist
                    filter_kwargs = {field.remote_field.name: instance}
                    if related_model.objects.filter(**filter_kwargs).exists():
                        return True, model_name
        
        return False, None
    
    def put(self, request, id):
        """Handle PUT requests with deactivation protection"""
        id = int(id)  # ValueError handled by global exception handler
        obj = self.get_object(id)
        
        # Extract data from {"data": {...}} format with JSON parsing for form-data
        if 'data' in request.data:
            data = request.data['data']
            # If data is a string (from form-data), parse it as JSON
            if isinstance(data, str):
                try:
                    import json
                    data = json.loads(data)
                except json.JSONDecodeError:
                    raise APIError(ERROR_INPUT, "Invalid JSON in data field")
            else:
                # Filter out file objects to avoid pickle errors during copy
                data = {
                    key: value for key, value in data.items()
                    if not isinstance(value, UploadedFile)
                }
        else:
            # Filter out file objects to avoid pickle errors during copy
            data = {
                key: value for key, value in request.data.items()
                if not isinstance(value, UploadedFile)
            }
        
        new_status = data.get('status')
        
        # Check if trying to deactivate
        if (hasattr(obj, 'status') and 
            obj.status == 'active' and 
            new_status == 'inactive'):
            
            has_refs, blocking_model = self.has_active_references(obj)
            if has_refs:
                raise APIError(ERROR_CANNOT_DEACTIVATE_REFERENCED_ITEM)
        
        # Handle file uploads (does nothing if no file_fields configured)
        file_data = self.handle_file_uploads(request)
        data.update(file_data)
        
        # Create and validate serializer
        serializer = self.serializer_class(obj, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                message_code=self.update_success_code,
                data=serializer.data
            )
        else:
            # Validation errors are handled by global exception handler
            raise serializers.ValidationError(serializer.errors)