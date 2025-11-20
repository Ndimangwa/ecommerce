from django import template

register = template.Library()

@register.filter 
def truncate_custom(value, length=30, trailing_char='.', no_of_trailing_chars=3):
    """Truncate a string to a specific length and add ... or trailing_char"""
    value = str(value)
    trailing_char = str(trailing_char)
    try:
        length = int(length)
        no_of_trailing_chars = int(no_of_trailing_chars)
    except:
        length=30
        no_of_trailing_chars = 3
    trailing_string = trailing_char * no_of_trailing_chars
    return value[:length-no_of_trailing_chars] + trailing_string if len(value) > length else value