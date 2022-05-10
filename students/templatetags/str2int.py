from django import template


register = template.Library()


@register.filter
def str2int(string):
    try:
        value = int(string)
    except ValueError:
        value = 0
    return value