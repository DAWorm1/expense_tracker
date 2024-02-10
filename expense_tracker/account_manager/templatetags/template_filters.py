from django import template

register = template.Library()

@register.filter()
def humanize_underscore_string(val: str):
    s = val.replace("_", " ")
    s = s.capitalize()
    return s