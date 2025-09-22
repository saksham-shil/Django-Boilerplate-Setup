import json
import logging
import time
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django_guid import get_guid

api_logger = logging.getLogger('api_requests')
error_logger = logging.getLogger('api_errors')

# Password fields to filter out from logging
SENSITIVE_FIELDS = ['password', 'old_password', 'new_password', 'confirm_password']


class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses with correlation IDs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Called before Django decides which view to execute
        """
        # Store request start time
        request._logging_start_time = time.time()
        
        # Store correlation ID for consistent use across request lifecycle
        try:
            request._correlation_id = get_guid() or 'unknown'
        except Exception:
            request._correlation_id = 'unknown'
        
        # Log the incoming request
        self._log_request(request)
        
        return None
    
    def process_response(self, request, response):
        """
        Called after the view has been executed
        """
        # Calculate response time
        if hasattr(request, '_logging_start_time'):
            response_time = (time.time() - request._logging_start_time) * 1000
        else:
            response_time = 0
            
        # Log the response
        self._log_response(request, response, response_time)
        
        return response
    
    def process_exception(self, request, exception):
        """
        Called when a view raises an exception
        """
        # Calculate response time
        if hasattr(request, '_logging_start_time'):
            response_time = (time.time() - request._logging_start_time) * 1000
        else:
            response_time = 0
            
        # Log the exception
        self._log_exception(request, exception, response_time)
        
        return None
    
    def _get_user_info(self, request):
        """
        Extract user information from request
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            return {
                'user_id': str(request.user.id),
                'email': request.user.email,
                'full_name': request.user.full_name,
            }
        return {
            'user_id': 'Anonymous',
            'email': 'N/A',
            'full_name': 'N/A',
        }
    
    def _get_client_ip(self, request):
        """
        Get the real client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'Unknown'
    
    def _filter_headers(self, headers):
        """
        Filter out sensitive headers and handle non-serializable objects
        """
        filtered = {}
        sensitive_headers = [
            # 'HTTP_AUTHORIZATION',
            # 'HTTP_COOKIE',
            # 'HTTP_X_API_KEY',
            # 'HTTP_X_AUTH_TOKEN',
        ]
        
        # WSGI objects that can't be serialized
        skip_keys = [
            'wsgi.errors',
            'wsgi.file_wrapper', 
            'wsgi.input',
            'wsgi.multithread',
            'wsgi.multiprocess',
            'wsgi.run_once',
            'wsgi.url_scheme',
            'wsgi.version',
        ]
        
        for key, value in headers.items():
            if key.lower() in skip_keys:
                continue
                
            # Skip non-serializable objects
            try:
                json.dumps(value)  # Test if value is JSON serializable
            except (TypeError, ValueError):
                filtered[key] = f'[Non-serializable: {type(value).__name__}]'
                continue
                
            # Handle sensitive headers
            if key.upper() in sensitive_headers:
                filtered[key] = '[REDACTED]'
            elif key.startswith('HTTP_'):
                # Convert HTTP_CONTENT_TYPE to Content-Type
                header_name = key[5:].replace('_', '-').title()
                filtered[header_name] = value
            else:
                filtered[key] = value
                
        return filtered
    
    def _filter_sensitive_data(self, data, depth=0, max_depth=10):
        """
        Filter out sensitive password fields from data
        """
        if depth > max_depth:
            return '[MAX_DEPTH_EXCEEDED]'
            
        if isinstance(data, dict):
            filtered_data = {}
            for key, value in data.items():
                if key.lower() in SENSITIVE_FIELDS:
                    filtered_data[key] = '[REDACTED]'
                elif isinstance(value, (dict, list)):
                    filtered_data[key] = self._filter_sensitive_data(value, depth + 1, max_depth)
                else:
                    filtered_data[key] = value
            return filtered_data
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item, depth + 1, max_depth) for item in data]
        else:
            return data
    
    def _get_request_body(self, request):
        """
        Safely get request body
        """
        try:
            if hasattr(request, 'body') and request.body:
                # Try to parse as JSON for better formatting
                try:
                    body_data = json.loads(request.body.decode('utf-8'))
                    return self._filter_sensitive_data(body_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return request.body.decode('utf-8', errors='replace')
            return None 
        except Exception:
            return '[Could not read request body]'
    
    def _get_response_body(self, response):
        """
        Safely get response body
        """
        try:
            if hasattr(response, 'content') and response.content:
                # Try to parse as JSON for better formatting
                try:
                    body_data = json.loads(response.content.decode('utf-8'))
                    return self._filter_sensitive_data(body_data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return response.content.decode('utf-8', errors='replace')
            return None
        except Exception:
            return '[Could not read response body]'
    
    def _log_request(self, request):
        """
        Log the incoming request
        """
        correlation_id = request._correlation_id
        user_info = self._get_user_info(request)
        
        log_data = {
            'type': 'REQUEST',
            'correlation_id': correlation_id,
            'method': request.method,
            'path': request.path,
            'user_info': user_info,
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'N/A'),
            'headers': self._filter_headers(request.META),
            'query_params': dict(request.GET),
            'request_body': self._get_request_body(request),
        }
        
        # Format the log message
        log_message = self._format_request_log(log_data)
        
        # Log to api_requests
        api_logger.info(log_message)
    
    def _log_response(self, request, response, response_time):
        """
        Log the response
        """
        correlation_id = request._correlation_id
        
        log_data = {
            'type': 'RESPONSE',
            'correlation_id': correlation_id,
            'status_code': response.status_code,
            'response_time_ms': round(response_time, 2),
            'content_length': len(response.content) if hasattr(response, 'content') else 0,
            'response_headers': dict(response.items()) if hasattr(response, 'items') else {},
            'response_body': self._get_response_body(response),
        }
        
        # Format the log message
        log_message = self._format_response_log(log_data)
        
        # Log to appropriate logger based on status code
        if response.status_code >= 400:
            error_logger.error(log_message)
        
        api_logger.info(log_message)
    
    def _log_exception(self, request, exception, response_time):
        """
        Log exceptions
        """
        correlation_id = request._correlation_id
        user_info = self._get_user_info(request)
        
        log_data = {
            'type': 'EXCEPTION',
            'correlation_id': correlation_id,
            'method': request.method,
            'path': request.path,
            'user_info': user_info,
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'response_time_ms': round(response_time, 2),
        }
        
        # Format the log message
        log_message = self._format_exception_log(log_data)
        
        # Log to error logger
        error_logger.error(log_message)
    
    def _format_request_log(self, data):
        """
        Format request log message
        """

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f"""
================================================================================
[REQUEST] [{timestamp}] [{data['correlation_id']}]
================================================================================
Method: {data['method']}
Path: {data['path']}
User ID: {data['user_info']['user_id']}
User Email: {data['user_info']['email']}
User Name: {data['user_info']['full_name']}
IP Address: {data['ip_address']}
User Agent: {data['user_agent']}

Headers:
{json.dumps(data['headers'], indent=2)}

Query Parameters:
{json.dumps(data['query_params'], indent=2)}

Request Body:
{json.dumps(data['request_body'], indent=2) if data['request_body'] else 'N/A'}
"""
    
    def _format_response_log(self, data):
        """
        Format response log message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f"""
================================================================================
[RESPONSE] [{timestamp}] [{data['correlation_id']}]
================================================================================
Status Code: {data['status_code']}
Response Time: {data['response_time_ms']}ms
Content Length: {data['content_length']} bytes

Response Headers:
{json.dumps(data['response_headers'], indent=2)}

Response Body:
{json.dumps(data['response_body'], indent=2) if data['response_body'] else 'N/A'}

================================================================================
[END REQUEST] [{data['correlation_id']}]
================================================================================
"""
    
    def _format_exception_log(self, data):
        """
        Format exception log message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return f"""
================================================================================
[EXCEPTION] [{timestamp}] [{data['correlation_id']}]
================================================================================
Method: {data['method']}
Path: {data['path']}
User ID: {data['user_info']['user_id']}
User Email: {data['user_info']['email']}
Exception Type: {data['exception_type']}
Exception Message: {data['exception_message']}
Response Time: {data['response_time_ms']}ms

================================================================================
[END EXCEPTION] [{data['correlation_id']}]
================================================================================
""" 