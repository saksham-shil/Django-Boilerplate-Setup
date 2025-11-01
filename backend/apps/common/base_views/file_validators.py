"""
Central file validation functions for reuse across base views.

This module provides unified file validation functions for:
- Image files (logos, profile images, etc.)
- Document files (PDFs, Office documents, CSV, etc.)

All validation functions use consistent error formats and follow
the patterns established in existing APIs.
"""

from rest_framework import serializers
from apps.common.api_responses.exception_handler import APIError
from apps.common.api_responses.constants import (
    ERROR_INVALID_FILE_FORMAT,
    ERROR_FILE_SIZE_TOO_LARGE,
    ERROR_INPUT,
    MAX_DOCUMENT_SIZE,
    MAX_IMAGE_SIZE,
    MAX_DOCUMENT_SIZE_MB,
    MAX_IMAGE_SIZE_MB,
    MAX_FILES_PER_UPLOAD
)


# Supported file formats
ALLOWED_IMAGE_EXTENSIONS = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', 
    '.png': 'image/png',
    '.webp': 'image/webp'
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.csv': 'text/csv',
    '.txt': 'text/plain'
}


def validate_images(files, max_size=MAX_IMAGE_SIZE, max_files=MAX_FILES_PER_UPLOAD, 
                   raise_api_error=False):
    """
    Validate image files for consistency across the application.
    
    Args:
        files: Single file or list of files
        max_size: Maximum file size in bytes (default from constants)
        max_files: Maximum number of files allowed (default from constants)
        raise_api_error: If True, raise APIError; if False, raise ValidationError
        
    Returns:
        List of validated files (or single file if input was single)
        
    Raises:
        APIError or ValidationError: If validation fails
    """
    # Handle single file input
    single_file = not isinstance(files, list)
    if single_file:
        files = [files] if files else []
    
    if not files:
        error_msg = "At least one image file is required"
        if raise_api_error:
            raise APIError(ERROR_INPUT, error_msg)
        else:
            raise serializers.ValidationError(error_msg)
    
    # Check file count limit
    if len(files) > max_files:
        error_msg = f"Maximum {max_files} files allowed per upload"
        if raise_api_error:
            raise APIError(ERROR_FILE_SIZE_TOO_LARGE, error_msg)
        else:
            raise serializers.ValidationError(error_msg)
    
    max_size_mb = max_size / 1024 / 1024
    validated_files = []
    
    for file in files:
        if not file:
            continue
            
        # Check file size
        if file.size > max_size:
            error_msg = f"Image file size must not exceed {max_size_mb:.0f}MB"
            if raise_api_error:
                raise APIError(ERROR_FILE_SIZE_TOO_LARGE, error_msg)
            else:
                raise serializers.ValidationError(error_msg)
        
        # Get file extension
        file_extension = None
        if hasattr(file, 'name') and file.name:
            file_extension = '.' + file.name.lower().split('.')[-1] if '.' in file.name else None
        
        # Check file format by extension and MIME type
        valid_format = False
        
        if file_extension and file_extension in ALLOWED_IMAGE_EXTENSIONS:
            expected_mime = ALLOWED_IMAGE_EXTENSIONS[file_extension]
            if hasattr(file, 'content_type') and file.content_type:
                # Allow some flexibility in MIME type checking
                if (file.content_type == expected_mime or 
                    (file_extension == '.jpg' and file.content_type == 'image/jpeg') or
                    (file_extension == '.jpeg' and file.content_type == 'image/jpeg')):
                    valid_format = True
            else:
                # If no content_type, trust the extension
                valid_format = True
        
        if not valid_format:
            allowed_formats = ', '.join([ext.upper()[1:] for ext in ALLOWED_IMAGE_EXTENSIONS.keys()])
            error_msg = f"Only {allowed_formats} image formats are supported"
            if raise_api_error:
                raise APIError(ERROR_INVALID_FILE_FORMAT, error_msg)
            else:
                raise serializers.ValidationError(error_msg)
        
        validated_files.append(file)
    
    return validated_files[0] if single_file else validated_files


def validate_documents(files, max_size=MAX_DOCUMENT_SIZE, max_files=MAX_FILES_PER_UPLOAD,
                      raise_api_error=False):
    """
    Validate document files for consistency across the application.
    
    Args:
        files: Single file or list of files
        max_size: Maximum file size in bytes (default from constants)
        max_files: Maximum number of files allowed (default from constants)  
        raise_api_error: If True, raise APIError; if False, raise ValidationError
        
    Returns:
        List of validated files (or single file if input was single)
        
    Raises:
        APIError or ValidationError: If validation fails
    """
    # Handle single file input
    single_file = not isinstance(files, list)
    if single_file:
        files = [files] if files else []
    
    if not files:
        error_msg = "At least one document file is required"
        if raise_api_error:
            raise APIError(ERROR_INPUT, error_msg)
        else:
            raise serializers.ValidationError(error_msg)
    
    # Check file count limit
    if len(files) > max_files:
        error_msg = f"Maximum {max_files} files allowed per upload"
        if raise_api_error:
            raise APIError(ERROR_FILE_SIZE_TOO_LARGE, error_msg)
        else:
            raise serializers.ValidationError(error_msg)
    
    max_size_mb = max_size / 1024 / 1024
    validated_files = []
    
    for file in files:
        if not file:
            continue
            
        # Check file size
        if file.size > max_size:
            error_msg = f"Document file size must not exceed {max_size_mb:.0f}MB"
            if raise_api_error:
                raise APIError(ERROR_FILE_SIZE_TOO_LARGE, error_msg)
            else:
                raise serializers.ValidationError(error_msg)
        
        # Get file extension
        file_extension = None
        if hasattr(file, 'name') and file.name:
            file_extension = '.' + file.name.lower().split('.')[-1] if '.' in file.name else None
        
        # Check file format by extension
        if not file_extension or file_extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            allowed_formats = ', '.join([ext.upper()[1:] for ext in ALLOWED_DOCUMENT_EXTENSIONS.keys()])
            error_msg = f"Unsupported file format. Allowed: {allowed_formats}"
            if raise_api_error:
                raise APIError(ERROR_INVALID_FILE_FORMAT, error_msg)
            else:
                raise serializers.ValidationError(error_msg)
        
        validated_files.append(file)
    
    return validated_files[0] if single_file else validated_files


def validate_single_image(file, max_size=MAX_IMAGE_SIZE, raise_api_error=False):
    """
    Convenience function to validate a single image file.
    
    Args:
        file: Single file object
        max_size: Maximum file size in bytes
        raise_api_error: If True, raise APIError; if False, raise ValidationError
        
    Returns:
        Validated file object
    """
    if not file:
        return file
    
    return validate_images([file], max_size=max_size, max_files=1, 
                          raise_api_error=raise_api_error)[0]


def validate_single_document(file, max_size=MAX_DOCUMENT_SIZE, raise_api_error=False):
    """
    Convenience function to validate a single document file.
    
    Args:
        file: Single file object  
        max_size: Maximum file size in bytes
        raise_api_error: If True, raise APIError; if False, raise ValidationError
        
    Returns:
        Validated file object
    """
    if not file:
        return file
    
    return validate_documents([file], max_size=max_size, max_files=1, 
                             raise_api_error=raise_api_error)[0]