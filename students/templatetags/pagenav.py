from django import template
from django.template.loader import get_template


register = template.Library()


@register.inclusion_tag('students/pagination.html')
def pagenav(object_list, is_paginated, paginator):
    # Usage: {% pagenav students is_paginated paginator %}
    return {
            'object_list': object_list,
            'is_paginated': is_paginated,
            'paginator': paginator
        }
