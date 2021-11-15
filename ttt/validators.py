from django.core.exceptions import ValidationError

from ttt.core import CIRCLE_SYMBOL, CROSS_SYMBOL, MAX_POSITION, MIN_POSITION


def validate_symbol(value):
    if value != CROSS_SYMBOL and value != CIRCLE_SYMBOL:
        raise ValidationError(f"invalid symbol: {value}")


def validate_position(value):
    if value < MIN_POSITION or MAX_POSITION < value:
        raise ValidationError(f"invalid position: {value}")
