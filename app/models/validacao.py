"""Funções de validação usadas pelas classes."""

from datetime import date
from exceptions.erros import ValidationError

def texto_obrigatorio(
    valor: str,
    campo: str,
    limite: int = 150
) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValidationError(
            f"{campo} é obrigatório."
        )
    valor = valor.strip()

    if len(valor) > limite:
        raise ValidationError(
            f"{campo} deve ter no máximo {limite} caracteres."
        )

    return valor
def identificador_positivo(
    valor: int,
    campo: str
) -> int:

    if not isinstance(valor, int) or valor <= 0:
        raise ValidationError(
            f"{campo} deve ser um inteiro positivo."
        )

    return valor

def data_ou_nula(
    valor: date | None,
    campo: str
) -> date | None:

    if valor is not None and not isinstance(valor, date):
        raise ValidationError(
            f"{campo} deve ser uma data válida."
        )
    return valor
def converter_data(
    texto: str,
    campo: str
) -> date | None:
    texto = texto.strip()
    if not texto:
        return None
    try:
        return date.fromisoformat(texto)

    except ValueError:
        raise ValidationError(
            f"{campo}: use o formato AAAA-MM-DD."
        )