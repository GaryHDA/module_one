from django import template

register = template.Library()

@register.filter(name='get_item')
def dic_value(dictionary, arg):
    return dictionary.get(arg)
