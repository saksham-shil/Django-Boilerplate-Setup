"""
Number utilities for formatting and rounding operations.
"""
from decimal import Decimal


def round_decimal_values(data):
    """
    Recursively round decimal/float values in dictionaries and lists to integers.

    Args:
        data: Dictionary, list, or any other data structure containing numeric values

    Returns:
        Same data structure with decimal values rounded to nearest integers
    """
    if isinstance(data, dict):
        return {key: round_decimal_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [round_decimal_values(item) for item in data]
    elif isinstance(data, (float, Decimal)):
        return round(float(data))
    else:
        return data