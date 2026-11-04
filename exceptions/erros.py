"""Exceções do StudyTrack."""


class StudyTrackError(Exception):
    """Erro base do sistema."""


class ValidationError(StudyTrackError):
    """Dado inválido."""


class NotFoundError(StudyTrackError):
    """Registro não encontrado."""


class DuplicateError(StudyTrackError):
    """Registro repetido."""


class AuthError(StudyTrackError):
    """Falha no login."""
    
class PersistenceError(StudyTrackError):
    """Erro relacionado à leitura ou gravação de dados."""