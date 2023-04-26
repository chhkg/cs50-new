import decimal 
from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def percent(value):
    return "{:.2%}".format(value)

@register.filter(name='normalize_fiat_crypto')
def normalize_fiat_crypto(value, arg):
    if value is None:
        return ''
    elif arg == "Crypto":
        two_decimal_value = Decimal("{:.2f}".format(value))
        normalized_value = value.normalize()
        decimal_places = -normalized_value.as_tuple().exponent
        if decimal_places > 2:
            return normalized_value
        return two_decimal_value
    elif arg == "FiatMoney":
        return "{:.2f}".format(value)
    else:
        return value
    
@register.filter(name='custom_rounding')
def custom_rounding(value, arg):
    if value is None:
        return ''
    elif arg == "Crypto":
        two_decimal_value = Decimal("{:.2f}".format(value))
        normalized_value = value.normalize()
        decimal_places = -normalized_value.as_tuple().exponent
        if decimal_places > 2:
            return normalized_value
        return two_decimal_value
    else:
        return "{:.2f}".format(value)