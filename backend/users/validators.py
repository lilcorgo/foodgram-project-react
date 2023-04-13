import re

from rest_framework.serializers import ValidationError


def username_validation(value):
    if len(value) > 150:
        raise ValidationError(
            'Превышено допустимое количество символов.'
        )
    if re.match(r'^[\w@.+-]+$', value) is None:
        raise ValidationError(
            'Допустимы только буквы, цифры и символы "@.+-".'
        )
    name = value.lower()
    if name == 'me':
        raise ValidationError(
            'Нельзя использовать имя "me" в качестве имени пользователя.'
        )
    return value
