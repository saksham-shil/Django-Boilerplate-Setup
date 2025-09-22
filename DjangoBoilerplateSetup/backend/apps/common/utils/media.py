"""
Central media utilities for consistent file handling and URL generation.

This module provides unified functions for:
- Building absolute media URLs using BASE_URL
- Saving files with relative paths to database
- Deleting files from storage
- Handling both legacy and new file path formats
"""

import os
import uuid
from pathlib import Path
from django.conf import settings
from django.core.files.storage import default_storage


def build_media_url(file_path):
    """
    Build absolute media URL from file path using BASE_URL.
    
    Handles multiple input formats for backward compatibility:
    - Relative paths: "projects/57/documents/file.png" EI
    - Legacy /media/ paths: "/media/projects/57/documents/file.png"
    - Full URLs: "https://domain.com/media/projects/57/documents/file.png"
    
    Args:
        file_path (str): File path in any supported format
        
    Returns:
        str: Absolute URL ready for API responses
        None: If file_path is empty/None
        
    Examples:
        >>> build_media_url("projects/57/documents/file.png")
        "https://api-dev-csrmm.veldev.com/media/projects/57/documents/file.png"
        
        >>> build_media_url("/media/projects/57/documents/file.png") 
        "https://api-dev-csrmm.veldev.com/media/projects/57/documents/file.png"
    """
    if not file_path:
        return None
        
    # Already a full URL - return as-is
    if file_path.startswith('http'):
        return file_path
        
    # Get BASE_URL from settings
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    
    # Handle /media/ prefixed paths (legacy format)
    if file_path.startswith('/media/'):
        return f"{base_url}{file_path}"
        
    # Handle relative paths (new format)
    return f"{base_url}/media/{file_path}"


def save_file_and_get_path(file, directory):
    """
    Save uploaded file to storage and return relative path for database storage.
    
    Generates UUID-based filename and saves to specified directory.
    Returns relative path (without /media/ prefix) for database storage.
    
    Args:
        file: Django UploadedFile object
        directory (str): Target directory (e.g., "projects/57/documents")
        
    Returns:
        tuple: (relative_path, original_filename, file_size, mime_type)
        
    Examples:
        >>> save_file_and_get_path(file, "projects/57/documents")
        ("projects/57/documents/uuid.png", "original.png", 1024, "image/png")
    """
    # Generate UUID-based filename
    file_ext = Path(file.name).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # Build relative file path
    relative_path = os.path.join(directory, unique_filename).replace('\\', '/')
    
    # Ensure directory exists in filesystem
    full_dir_path = os.path.join(settings.MEDIA_ROOT, directory)
    os.makedirs(full_dir_path, exist_ok=True)
    
    # Save file to storage
    saved_path = default_storage.save(relative_path, file)
    
    # Return relative path (for DB), original filename, size, and MIME type
    return saved_path, file.name, file.size, file.content_type


def delete_file(file_path):
    """
    Delete file from storage handling multiple path formats.
    
    Supports both relative paths and /media/ prefixed paths.
    
    Args:
        file_path (str): File path in any supported format
        
    Returns:
        bool: True if file was deleted successfully, False otherwise
        
    Examples:
        >>> delete_file("projects/57/documents/uuid.png")
        True
        >>> delete_file("/media/projects/57/documents/uuid.png") 
        True
    """
    if not file_path:
        return False
        
    try:
        # Convert to relative path for storage operations
        if file_path.startswith('/media/'):
            # Remove /media/ prefix
            storage_path = file_path[7:]
        elif file_path.startswith(settings.MEDIA_URL):
            # Remove MEDIA_URL prefix 
            storage_path = file_path[len(settings.MEDIA_URL):]
        elif file_path.startswith('http'):
            # Extract path from full URL
            # Example: https://domain.com/media/projects/... -> projects/...
            if '/media/' in file_path:
                storage_path = file_path.split('/media/', 1)[1]
            else:
                return False
        else:
            # Already a relative path
            storage_path = file_path
            
        # Delete from storage if exists
        if default_storage.exists(storage_path):
            default_storage.delete(storage_path)
            return True
            
    except Exception:
        # Log error in production, but don't raise
        pass
        
    return False


def normalize_file_path(file_path):
    """
    Normalize file path to relative format for database storage.
    
    Converts various file path formats to consistent relative paths.
    Used for data migration and cleanup operations.
    
    Args:
        file_path (str): File path in any format
        
    Returns:
        str: Normalized relative path
        None: If file_path is empty/None or invalid
        
    Examples:
        >>> normalize_file_path("/media/projects/57/documents/file.png")
        "projects/57/documents/file.png"
        
        >>> normalize_file_path("https://domain.com/media/projects/57/documents/file.png")
        "projects/57/documents/file.png"
    """
    if not file_path:
        return None
        
    # Already a relative path
    if not file_path.startswith(('/media/', 'http')):
        return file_path
        
    # Handle /media/ prefixed paths
    if file_path.startswith('/media/'):
        return file_path[7:]  # Remove '/media/' prefix
        
    # Handle full URLs
    if file_path.startswith('http') and '/media/' in file_path:
        return file_path.split('/media/', 1)[1]
        
    return None


def get_file_directory(file_type, entity_id):
    """
    Get standard directory path for different file types.
    
    Provides consistent directory structure across the application.
    
    Args:
        file_type (str): Type of file ('project_document', 'profile_image', etc.)
        entity_id (int/str): ID of the related entity
        
    Returns:
        str: Directory path without leading/trailing slashes
        
    Examples:
        >>> get_file_directory('project_document', 57)
        "projects/57/documents"
        
        >>> get_file_directory('profile_image', 123) 
        "profile_images/123"
    """
    directory_map = {
        'project_document': f"projects/{entity_id}/documents",
        'project_image': f"projects/{entity_id}/documents", 
        'phase_document': f"projects/{entity_id}/documents",
        'project_closure': f"projects/{entity_id}/closure_documents",
        'interest_review_document': f"interests/{entity_id}/review_documents",
        'profile_image': f"profile_images/{entity_id}",
    }
    
    return directory_map.get(file_type, f"uploads/{entity_id}")


def save_uploaded_file(uploaded_file, folder):
    """
    Save uploaded file using the existing save_file_and_get_path utility.
    
    This function is used by base_master_views for file upload handling.
    
    Args:
        uploaded_file: Django UploadedFile object
        folder (str): Folder name (e.g., "department")
        
    Returns:
        str: Relative file path for database storage
    """
    relative_path, original_filename, file_size, mime_type = save_file_and_get_path(uploaded_file, folder)
    return relative_path