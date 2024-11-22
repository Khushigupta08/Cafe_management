from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies value by arg."""
    return value * arg