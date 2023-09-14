from django import template

register = template.Library()


@register.filter(name='split_string')
def split_string(value, key):
    """ 
    Returns the value turned into a list.
    """
    try:
        return value.split(key)
    except:
        return [value]  # return the original string in a list if there's any error
