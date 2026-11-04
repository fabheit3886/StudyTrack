"""Exceções de domínio usadas para apresentar erros claros no StudyTrack."""


class StudyTrackError(Exception):
    """Erro esperado da aplicação que pode ser mostrado ao usuário."""


class ValidationError(StudyTrackError):
    """Indica que um dado informado não atende às regras do domínio."""


class NotFoundError(StudyTrackError):
    """Indica que o registro solicitado não foi encontrado."""


class DuplicateError(StudyTrackError):
    """Indica conflito com uma regra de unicidade."""


class PersistenceError(StudyTrackError):
    """Indica falha ao ler ou gravar os dados persistentes."""


class IntegrityError(PersistenceError):
    """Indica que o arquivo de dados está corrompido ou inconsistente."""
