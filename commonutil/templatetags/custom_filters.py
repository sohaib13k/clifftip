from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def time_elapsed(value):
    if not value:
        return ""
    
    delta = now() - value

    if delta.days >= 1:
        return f"{delta.days} days ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hours ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "just now"
