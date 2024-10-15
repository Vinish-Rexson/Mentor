from django import template

register = template.Library()

@register.filter
def readable_username(value):
    # Replace underscores with spaces and capitalize each word
    return value.replace('_', ' ').title()
