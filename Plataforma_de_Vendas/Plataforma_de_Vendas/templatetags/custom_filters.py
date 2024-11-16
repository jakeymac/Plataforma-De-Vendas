from django import template
from django.utils.text import slugify
register = template.Library()

@register.filter(name='none_to_empty')
def none_to_empty(value):
    """
    Returns an empty string if the value is None or 'None'.
    """
    if value is None or value == 'None':
        return ""
    return value

@register.filter(name='no_data_provided')
def no_data_provided(value, field_name):
    """
    Returns a field-specific message if the value is None or an empty string.
    Example: "No city provided", "No address provided", etc.
    """
    if value is None or value == 'None' or value.strip() == '':
        return f"No {field_name} provided."
    return value

@register.filter(name='valid_value')
def valid_value(value):
    """
    Returns True if the value is not None, 'None', or an empty string.
    """
    return value is not None and value != 'None' and value.strip() != ''

@register.filter(name='slugify_name')
def slugify_name(value):
    """
    Returns a slugified version of the value. (e.g. "Hello World" -> "hello-world")
    """
    return slugify(value)