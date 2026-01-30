from django import template
from account.models import ConnectionRequest

register = template.Library()

@register.simple_tag
def get_pending_requests(user):
    """Get pending connection requests for a user"""
    return user.received_requests.filter(status='pending')
