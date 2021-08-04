from django.template.defaultfilters import register
import os


@register.filter('ellipse')
def ellipse(value, arg=-1):
    return value[:3] + str(arg)
