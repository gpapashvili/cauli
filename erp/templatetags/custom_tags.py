from django import template
import pandas as pd

register = template.Library()

@register.filter
def is_nan(value):
    return pd.isna(value)

@register.filter
def dividerem2(value, arg):
    try:
        return round(float(value) / float(arg),2)
    except (ValueError, ZeroDivisionError):
        return 0

