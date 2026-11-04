"""Funções para leitura de dados do usuário."""

from datetime import date
def ler_inteiro(pergunta: str) -> int:
    try:
        return int(input(pergunta).strip())

    except ValueError:
        raise ValueError("Digite um número inteiro válido.")
def ler_data(pergunta: str) -> date | None:
    texto = input(pergunta).strip()

    if not texto:
        return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise ValueError("Digite a data no formato AAAA-MM-DD.")