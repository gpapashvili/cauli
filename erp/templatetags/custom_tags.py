from django import template
import pandas as pd

register = template.Library()

@register.filter
def is_nan(value):
    return pd.isna(value)
