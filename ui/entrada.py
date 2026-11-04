from datetime import date


def inteiro(pergunta: str) -> int:
    """Lê identificador numérico com mensagem amigável."""
    try:
        return int(input(pergunta).strip())
    except ValueError as erro:
        raise ValueError("Informe um número inteiro válido.") from erro


def data(pergunta: str, obrigatoria: bool = False) -> date | None:
    """Lê uma data ISO opcional ou obrigatória."""
    valor = input(pergunta).strip()
    if not valor and not obrigatoria:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError("Use o formato de data AAAA-MM-DD.") from erro