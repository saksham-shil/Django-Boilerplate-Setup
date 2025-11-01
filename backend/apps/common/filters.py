"""
Common filtering utilities for list views

Provides reusable filtering, searching, and sorting functionality
to reduce code duplication across the project.

Design: Standalone functions that accept request and queryset as parameters.
This is more flexible and testable than mixins.
"""

from django.db.models import Q, QuerySet
from django.http import HttpRequest
from typing import List, Optional


def apply_search_filter(
    request: HttpRequest,
    queryset: QuerySet,
    search_fields: List[str]
) -> QuerySet:
    """
    Apply case-insensitive search across multiple fields

    Args:
        request: Django request object
        queryset: The queryset to filter
        search_fields: List of field names to search in

    Returns:
        Filtered queryset (unchanged if no search term or invalid input)

    Example:
        queryset = apply_search_filter(request, queryset, ['name', 'description'])
        # Searches for query param 'search' in name OR description

    Edge Cases:
        - Empty/whitespace search terms are ignored
        - SQL injection is prevented by Django ORM
        - Unicode characters are handled correctly
    """
    try:
        search_term = request.query_params.get('search', '').strip()
    except AttributeError:
        # Handle edge case where query_params doesn't exist
        return queryset

    if not search_term or not search_fields:
        return queryset

    # Build OR query across all search fields
    query = Q()
    for field in search_fields:
        query |= Q(**{f'{field}__icontains': search_term})

    return queryset.filter(query)


def apply_exact_filters(
    request: HttpRequest,
    queryset: QuerySet,
    filter_fields: List[str]
) -> QuerySet:
    """
    Apply exact match filters for specified fields with multi-select support

    All filters support both single and multiple values using repeated params:
    - Single: ?status=active
    - Multiple: ?status=active&status=inactive

    Args:
        request: Django request object
        queryset: The queryset to filter
        filter_fields: List of field names to filter on

    Returns:
        Filtered queryset (silently ignores invalid values)

    Examples:
        queryset = apply_exact_filters(request, queryset, ['status', 'category'])
        # Single: ?status=active → field=active
        # Multi: ?status=active&status=inactive → field__in=['active', 'inactive']

    Edge Cases:
        - Invalid values are silently ignored (no error, no filtering)
        - Boolean fields: accepts true/false/1/0 (case-insensitive)
        - Negative values like -1 are handled safely
        - SQL injection is prevented by Django ORM
        - ChoiceField validation: only applies filter if value is in choices
        - Empty values are ignored
    """
    if not filter_fields:
        return queryset

    try:
        model = queryset.model

        for field in filter_fields:
            # Get all values for this field using getlist
            # ?status=active → ['active']
            # ?status=active&status=inactive → ['active', 'inactive']
            values = request.query_params.getlist(field)

            if not values:
                continue

            # Filter out empty values
            values = [v.strip() for v in values if v and v.strip()]

            if not values:
                continue

            # Get the model field to check for choices
            try:
                model_field = model._meta.get_field(field)
            except Exception:
                # Field doesn't exist, skip it
                continue

            # Handle boolean fields with edge case protection
            if model_field.get_internal_type() == 'BooleanField':
                converted_values = []
                for val in values:
                    if val.lower() in ('true', 'false', '1', '0'):
                        try:
                            converted_values.append(val.lower() in ('true', '1'))
                        except (AttributeError, ValueError):
                            # Silently ignore invalid boolean values
                            continue
                    # Ignore non-boolean values

                if not converted_values:
                    continue

                values = converted_values

            # Handle ChoiceField validation
            if hasattr(model_field, 'choices') and model_field.choices:
                valid_choices = [choice[0] for choice in model_field.choices]
                # Filter out invalid choices
                values = [v for v in values if v in valid_choices]

                if not values:
                    # No valid values, skip this filter
                    continue

            # Apply filter (Django ORM handles SQL injection)
            try:
                if len(values) == 1:
                    # Single value: exact match
                    queryset = queryset.filter(**{field: values[0]})
                else:
                    # Multiple values: use __in lookup
                    queryset = queryset.filter(**{f'{field}__in': values})
            except (ValueError, TypeError, Exception):
                # Silently ignore if filter causes any error
                continue

    except AttributeError:
        # Handle edge case where query_params doesn't exist
        pass

    return queryset


def apply_sorting(
    request: HttpRequest,
    queryset: QuerySet,
    allowed_fields: List[str],
    default: str = '-created_at'
) -> QuerySet:
    """
    Apply sorting with validation of allowed fields

    Args:
        request: Django request object
        queryset: The queryset to sort
        allowed_fields: List of field names that are allowed for sorting
        default: Default sort field (with optional '-' prefix for descending)

    Returns:
        Sorted queryset (uses default if invalid field provided)

    Example:
        queryset = apply_sorting(
            request,
            queryset,
            ['created_at', 'name', 'status'],
            default='-created_at'
        )
        # Supports ?sort_by=name or ?sort_by=-name (descending)

    Edge Cases:
        - Invalid sort fields fallback to default (silent)
        - SQL injection is prevented by field validation
        - Edge values like -1, 'null', etc. are safely ignored
    """
    try:
        sort_by = request.query_params.get('sort_by', default)
    except AttributeError:
        # Handle edge case where query_params doesn't exist
        sort_by = default

    # Validate that the field (without '-' prefix) is allowed
    field_name = sort_by.lstrip('-')
    if field_name in allowed_fields:
        try:
            return queryset.order_by(sort_by)
        except (ValueError, TypeError):
            # Silently fallback to default if order_by fails
            pass

    # Fall back to default if invalid field provided
    return queryset.order_by(default)


def apply_all_filters(
    request: HttpRequest,
    queryset: QuerySet,
    search_fields: Optional[List[str]] = None,
    filter_fields: Optional[List[str]] = None,
    sort_fields: Optional[List[str]] = None,
    default_sort: str = '-created_at'
) -> QuerySet:
    """
    Convenience function to apply all filters at once

    Args:
        request: Django request object
        queryset: The queryset to filter and sort
        search_fields: Fields to search in (optional)
        filter_fields: Fields to filter on (optional)
        sort_fields: Fields allowed for sorting (optional)
        default_sort: Default sort field

    Returns:
        Filtered and sorted queryset

    Example:
        queryset = apply_all_filters(
            request,
            queryset,
            search_fields=['name'],
            filter_fields=['status', 'category'],
            sort_fields=['created_at', 'name']
        )

    Edge Cases:
        - All invalid values are silently ignored
        - No errors are raised for bad input
        - SQL injection is prevented throughout
    """
    if search_fields:
        queryset = apply_search_filter(request, queryset, search_fields)

    if filter_fields:
        queryset = apply_exact_filters(request, queryset, filter_fields)

    if sort_fields:
        queryset = apply_sorting(request, queryset, sort_fields, default_sort)

    return queryset
