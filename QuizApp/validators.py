import re
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext as _


class NumberValidator(BaseValidator):

    def __init__(self, limit_value=20, message=None):
        super().__init__(limit_value, message)

    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(_("The password must contain at least 1 digit, 0-9.\n"), code='password_no_number',)

    def get_help_text(self):
        return _("Your password must contain at least 1 digit, 0-9.\n")


class UpperCaseValidator(BaseValidator):
    def __init__(self, limit_value=20, message=None):
        super().__init__(limit_value, message)

    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(_("The password must contain at least 1 uppercase letter\n"))

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter\n")


class SymbolValidator(BaseValidator):
    def __init__(self, limit_value=20, message=None):
        super().__init__(limit_value, message)

    def validate(self, password, user=None):
        if not re.findall('[*!@#&%_.,$?+=-]', password):
            raise ValidationError(_("The password must contain at least 1 symbol: *!@#&%_.,$?+=-\n"))

    def get_help_text(self):
        return _("The password must contain at least 1 symbol of the following: *!@#&%_.,$?+=-\n")


