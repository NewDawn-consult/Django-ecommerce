import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter
def bulletize(value):
    if not value:
        return ''
    lines = value.split('\n')
    result = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        match = re.match(r'^[-*•]\s+(.*)', stripped)
        if match:
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{escape(match.group(1))}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            if stripped:
                result.append(f'<p>{escape(stripped)}</p>')
            else:
                result.append('<br>')

    if in_list:
        result.append('</ul>')

    return mark_safe(''.join(result))


@register.filter
def get_item(d, key):
    return d.get(key, '') if isinstance(d, dict) else ''
