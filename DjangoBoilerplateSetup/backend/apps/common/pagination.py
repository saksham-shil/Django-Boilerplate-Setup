from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from django.core.paginator import Paginator


def get_pagination_params(request):
    """
    Extract and validate pagination parameters from request.
    
    Implements the standard pagination behavior:
    - If neither page nor limit provided: return all data (no pagination)
    - If only one provided: use defaults for missing parameter
    - If both provided: use provided values
    
    Args:
        request: Django or DRF request object
        
    Returns:
        dict: {
            'should_paginate': bool,
            'page': int,
            'limit': int
        }
    """
    # Get parameters from request (handle both DRF and Django requests)
    if hasattr(request, 'query_params'):
        page_param = request.query_params.get('page')
        limit_param = request.query_params.get('limit')
    else:
        page_param = request.GET.get('page')
        limit_param = request.GET.get('limit')
    
    # Apply pagination logic
    if page_param is None and limit_param is None:
        # No pagination parameters - return all data
        return {
            'should_paginate': False,
            'page': 1,
            'limit': 10  # Won't be used
        }
    else:
        # At least one parameter provided - apply pagination
        # Validate page parameter
        try:
            page = int(page_param) if page_param else 1
            page = max(1, page)  # Ensure page is at least 1
        except (ValueError, TypeError):
            page = 1  # Default to page 1 for invalid values
        
        # Validate limit parameter
        try:
            limit = int(limit_param) if limit_param else 10
            limit = max(1, min(limit, 100))  # Ensure limit is between 1 and 100
        except (ValueError, TypeError):
            limit = 10  # Default to 10 for invalid values
        
        return {
            'should_paginate': True,
            'page': page,
            'limit': limit
        }


def apply_manual_pagination(queryset, request):

    
    """
    Apply manual pagination to a queryset using Django's Paginator.
    
    Args:
        queryset: Django QuerySet to paginate
        request: Django request object
        
    Returns:
        dict: {
            'data': QuerySet (consistent type),
            'total': int,
            'next': str or None,
            'previous': str or None
        }
    """
    # Get pagination parameters internally
    pagination_params = get_pagination_params(request)
    if not pagination_params['should_paginate']:
        # Return all data without pagination
        return {
            'data': queryset,
            'total': queryset.count(),
            'next': None,
            'previous': None
        }
    
    # Apply pagination
    page = pagination_params['page']
    limit = pagination_params['limit']
    
    paginator = Paginator(queryset, limit)
    page_obj = paginator.get_page(page)
    
    # Build next/previous URLs preserving existing query parameters
    next_url = None
    previous_url = None
    
    try:
        from django.conf import settings
        base_url = f"{settings.BASE_URL}{request.path}"
    except:
        # Fallback for environments without BASE_URL
        try:
            base_url = request.build_absolute_uri(request.path)
        except:
            # Final fallback for test environments
            base_url = request.path
    
    def build_pagination_url(page_number):
        """Build URL preserving existing query parameters."""
        if hasattr(request, 'query_params'):
            query_params = request.query_params.copy()
        else:
            query_params = request.GET.copy()
        
        query_params['page'] = page_number
        query_params['limit'] = limit
        
        return f"{base_url}?{query_params.urlencode()}"
    
    if page_obj.has_next():
        next_url = build_pagination_url(page_obj.next_page_number())
    
    if page_obj.has_previous():
        previous_url = build_pagination_url(page_obj.previous_page_number())
    
    return {
        'data': page_obj.object_list,  # Return QuerySet for consistency
        'total': paginator.count,
        'next': next_url,
        'previous': previous_url
    }


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class for the project.
    
    Provides consistent pagination format across all list APIs.
    Compatible with both DRF requests (query_params) and Django requests (GET).
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_page_size(self, request):
        """Override to handle both DRF and Django request objects"""
        if hasattr(request, 'query_params'):
            # DRF request
            page_size = request.query_params.get(self.page_size_query_param)
        else:
            # Django request
            page_size = request.GET.get(self.page_size_query_param)
            
        if page_size:
            try:
                return min(int(page_size), self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size
    
    def get_page_number(self, request, paginator):
        """Override to handle both DRF and Django request objects"""
        if hasattr(request, 'query_params'):
            # DRF request
            page_number = request.query_params.get(self.page_query_param, 1)
        else:
            # Django request
            page_number = request.GET.get(self.page_query_param, 1)
            
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        try:
            return int(page_number)
        except (KeyError, ValueError):
            return 1
    
    def get_paginated_response(self, data):
        """
        Return paginated response in our standard format.
        
        Format:
        {
            "projects": [...],  # or other data key
            "total": 100,
            "next": "http://api/endpoint?page=2&limit=10",
            "previous": "http://api/endpoint?page=1&limit=10"
        }
        """
        return Response({
            'total': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data  # This will be renamed by the view
        })
    
    def get_next_link(self):
        """Get next page URL."""
        if not self.page.has_next():
            return None
        return self._get_link_for_page(self.page.next_page_number())
    
    def get_previous_link(self):
        """Get previous page URL."""
        if not self.page.has_previous():
            return None
        return self._get_link_for_page(self.page.previous_page_number())
    
    def _get_link_for_page(self, page_number):
        """
        Build URL for a specific page number using BASE_URL.
        
        Maintains all existing query parameters.
        """
        try:
            from django.conf import settings
            base_url = f"{settings.BASE_URL}{self.request.path}"
        except:
            # Fallback to request-based URL generation
            base_url = self.request.build_absolute_uri(self.request.path)
        
        # Get current query params
        if hasattr(self.request, 'query_params'):
            query_params = self.request.query_params.copy()
        else:
            query_params = self.request.GET.copy()
        
        # Update page parameter
        query_params[self.page_query_param] = str(page_number)
        
        # Ensure limit parameter is included
        if self.page_size_query_param not in query_params:
            query_params[self.page_size_query_param] = str(self.get_page_size(self.request))
        
        return f"{base_url}?{query_params.urlencode()}"