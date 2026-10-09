from django import template
from utils.image_optimizer import srcset_for

register = template.Library()


@register.filter
def srcset(fieldfile):
    return srcset_for(fieldfile)
