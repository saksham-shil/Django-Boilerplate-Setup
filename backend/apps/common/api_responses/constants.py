# Success message codes (1000-1999)
# Core System (1000-1099)
SUCCESS_GENERIC = 1000
SUCCESS_USER_REGISTERED = 1001
SUCCESS_USER_LOGIN = 1002
SUCCESS_ACCESS_TOKEN_RETRIEVED = 1003
SUCCESS_LOGOUT = 1004
SUCCESS_USER_INFO_FETCHED = 1007
SUCCESS_USER_PROFILE_FETCHED = 1011
SUCCESS_USER_PROFILE_UPDATED = 1012
SUCCESS_PASSWORD_RESET_EMAIL_SENT = 1008
SUCCESS_PASSWORD_RESET = 1009
SUCCESS_PASSWORD_CHANGED = 1010

# User Management & Audit (1400-1499)
SUCCESS_USERS_RETRIEVED = 1400
SUCCESS_USER_RETRIEVED = 1401
SUCCESS_USER_CREATED = 1402
SUCCESS_USER_UPDATED = 1403
SUCCESS_AUDIT_LOGS_RETRIEVED = 1404

# Generic Data Operations (1500-1599)
SUCCESS_NO_DATA_FOUND = 1905

# Input error codes (2000-2999)
ERROR_GENERIC = 2000
ERROR_INPUT = 2001
ERROR_VALIDATION = 2002

# Authentication error codes (3000-3999)
ERROR_AUTH_CREDENTIALS_NOT_PROVIDED = 3001
ERROR_INVALID_CREDENTIALS = 3002
ERROR_INVALID_EXPIRED_REFRESH_TOKEN = 3003
ERROR_USER_ACCOUNT_INACTIVE = 3004
ERROR_PERMISSION_DENIED = 3005

# User error codes (4000-4999)
ERROR_USER_EMAIL_EXISTS = 4001
ERROR_USER_NOT_FOUND = 4003
ERROR_PROFILE_NOT_FOUND = 4076

# File handling errors
ERROR_INVALID_FILE_FORMAT = 4013
ERROR_FILE_SIZE_TOO_LARGE = 4014

# Master Data errors - Generic fallbacks for template extensibility
ERROR_INVALID_IMAGE_FORMAT = 4060
ERROR_INVALID_DOCUMENT_FORMAT = 4061
ERROR_MASTER_DATA_NOT_FOUND = 4058  # Generic fallback for any master data not found
ERROR_CANNOT_DEACTIVATE_REFERENCED_ITEM = 4047


# Server error codes (5000-5999)
ERROR_INTERNAL_SERVER = 5001
ERROR_RATE_LIMIT_EXCEEDED = 5002

# Validation Errors (Serializers)
VALIDATION_FULL_NAME_NUMERIC = "Full name cannot contain numeric characters"
VALIDATION_CONTACT_NUMBER_INVALID = "Contact number must be numeric and of 10 digits"
VALIDATION_INVALID_THEMATIC_AREAS = "Invalid thematic area IDs: {invalid_ids}"
VALIDATION_IMAGE_SIZE_TOO_LARGE = "Image size must be less than {max_size}MB"
VALIDATION_INVALID_IMAGE_FORMAT = "Only PNG and JPG formats are allowed"
VALIDATION_INVALID_DOCUMENT_FORMAT = "Only PDF, DOC, Excel, PPT, and CSV formats are supported"
VALIDATION_INVALID_IDS = "Invalid {entity} IDs: {invalid_ids}"

# Message mappings
MESSAGES = {
    # Success Messages - Core System
    SUCCESS_GENERIC: "Operation completed successfully",
    SUCCESS_USER_REGISTERED: "User registered successfully",
    SUCCESS_USER_LOGIN: "User login successful",
    SUCCESS_ACCESS_TOKEN_RETRIEVED: "Access token retrieved successfully",
    SUCCESS_LOGOUT: "Successfully logged out",
    SUCCESS_USER_INFO_FETCHED: "User information fetched successfully",
    SUCCESS_USER_PROFILE_FETCHED: "User profile fetched successfully",
    SUCCESS_USER_PROFILE_UPDATED: "Profile updated successfully",
    SUCCESS_PASSWORD_RESET_EMAIL_SENT: "Password reset email sent successfully",
    SUCCESS_PASSWORD_RESET: "Password reset successfully",
    SUCCESS_PASSWORD_CHANGED: "Password changed successfully",

    # User Management & Audit
    SUCCESS_USERS_RETRIEVED: "Users retrieved successfully",
    SUCCESS_USER_RETRIEVED: "User retrieved successfully",
    SUCCESS_USER_CREATED: "User created successfully",
    SUCCESS_USER_UPDATED: "User updated successfully",
    SUCCESS_AUDIT_LOGS_RETRIEVED: "Audit logs retrieved successfully",

    # Generic Data Operations
    SUCCESS_NO_DATA_FOUND: "No data found",

    # Input Error Messages
    ERROR_GENERIC: "An error occurred",
    ERROR_INPUT: "Input error",
    ERROR_VALIDATION: "Validation error occurred",

    # Authentication Error Messages
    ERROR_AUTH_CREDENTIALS_NOT_PROVIDED: "Authentication credentials were not provided or are invalid",
    ERROR_INVALID_CREDENTIALS: "Invalid credentials provided",
    ERROR_INVALID_EXPIRED_REFRESH_TOKEN: "Invalid or expired refresh token",
    ERROR_USER_ACCOUNT_INACTIVE: "User account is inactive",
    ERROR_PERMISSION_DENIED: "You do not have permission to perform this action",

    # User Error Messages
    ERROR_USER_EMAIL_EXISTS: "User with email already exists",
    ERROR_USER_NOT_FOUND: "User not found",
    ERROR_PROFILE_NOT_FOUND: "Profile not found",

    # File Error Messages
    ERROR_INVALID_FILE_FORMAT: "This file format is not supported",
    ERROR_FILE_SIZE_TOO_LARGE: "File size is more than the maximum size",

    # Master Data Error Messages
    ERROR_INVALID_IMAGE_FORMAT: "For images, only JPG, JPEG, PNG, WEBP formats are supported",
    ERROR_INVALID_DOCUMENT_FORMAT: "For documents, only PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, CSV, TXT formats are supported",
    ERROR_MASTER_DATA_NOT_FOUND: "Master data not found",
    ERROR_CANNOT_DEACTIVATE_REFERENCED_ITEM: "Cannot set as inactive, active object(s) references this item",

    # Add your project-specific error messages here:
    # Example:
    # ERROR_PRODUCT_NOT_FOUND: "Product not found",
    # ERROR_CATEGORY_NOT_FOUND: "Category not found",
    # ERROR_ORDER_NOT_FOUND: "Order not found",


    # Server Error Messages
    ERROR_INTERNAL_SERVER: "Internal Server error",
    ERROR_RATE_LIMIT_EXCEEDED: "Rate limit exceeded. Please try again later",
}


def get_message(message_code):
    """Get message text for a given message code."""
    return MESSAGES.get(message_code, f"Unknown message code: {message_code}")


def is_success_code(message_code):
    """Check if message code represents success."""
    return 1000 <= message_code < 2000