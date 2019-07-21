from django.core.exceptions import ValidationError


def validate_isic_number(number):
    try:
        int(number)
    except ValueError:
        raise ValidationError('Not a valid ISIC number')

    if len(number) != 17:
        raise ValidationError('Not a valid ISIC number')
