from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def display_cgpa(value):
    if value is None or value == '' or (isinstance(value, (int, float, Decimal)) and value == 0):
        return ''
    return value