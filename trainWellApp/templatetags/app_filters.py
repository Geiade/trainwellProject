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


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def define(val=None):
    return val


@register.filter
def tolist(object):
    return list(object)


@register.filter
def concat_list(objects):
    new_list = []
    for curr in objects:
        new_list += curr

    return new_list
