"""Validações compartilhadas pelas entidades do domínio."""

from datetime import date

from exceptions.erros import ValidationError


def texto_obrigatorio(valor: str, campo: str, limite: int) -> str:
    """Normaliza texto e valida presença e tamanho máximo."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValidationError(f"{campo} é obrigatório.")
    valor = valor.strip()
    if len(valor) > limite:
        raise ValidationError(f"{campo} deve ter no máximo {limite} caracteres.")
    return valor


def identificador_positivo(valor: int, campo: str) -> int:
    """Valida um identificador numérico positivo."""
    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        raise ValidationError(f"{campo} deve ser um número inteiro positivo.")
    return valor


def data_ou_nula(valor: date | None, campo: str) -> date | None:
    """Aceita uma data ou None e rejeita outros tipos."""
    if valor is not None and not isinstance(valor, date):
        raise ValidationError(f"{campo} deve ser uma data válida.")
    return valor
