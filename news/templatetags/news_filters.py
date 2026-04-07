from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter
def is_less_than_one_day_old(publish_date):
    """Check if a datetime is less than 1 day old."""
    if not publish_date:
        return False
    now = timezone.now()
    return (now - publish_date) < timedelta(days=1)
