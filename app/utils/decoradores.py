"""Decoradores utilizados pelos menus."""
from functools import wraps

from exceptions.erros import StudyTrackError
from templates.visual import mensagem

def tratar_erros(funcao):
    """Captura erros e mostra mensagens amigáveis."""
    @wraps(funcao)
    def interna(*args, **kwargs):
        try:
            return funcao(*args, **kwargs)
        except (StudyTrackError, ValueError) as erro:
            mensagem(str(erro), "erro")
    return interna