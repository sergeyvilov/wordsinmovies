from django import template

register=template.Library()

@register.filter
def clear(value):
    return list()
