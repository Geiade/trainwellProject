from django import template
import json

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)


@register.filter
def get_item(data_as_json, args):
    dictionary = json.loads(data_as_json)
    key_substr, item = args.split(',')
    values = [value for key, value in dictionary.items() if key_substr in key]

    if values:
        for ls in values:
            if item in ls: return True

    return None


@register.simple_tag
def define(val=None):
    return val
