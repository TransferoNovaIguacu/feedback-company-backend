from validate_docbr import CNPJ
from django.core.exceptions import ValidationError

def validate_cnpj(value):
    cnpj = CNPJ()
    if not cnpj.validate(value):
        raise ValidationError(
            "CNPJ inválido. Por favor, forneça um CNPJ válido com 14 números, sem pontos ou traços.",
            code='invalid'
        )
