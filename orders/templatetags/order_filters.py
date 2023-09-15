from django import template
from orders.models import OrderMetaData

register = template.Library()

@register.filter
def get_metadata_value(order, key):
    try:
        return OrderMetaData.objects.get(order=order, key=key).value
    except OrderMetaData.DoesNotExist:
        return ''
    
@register.filter
def multiply(value, arg):
    return value * arg
    
