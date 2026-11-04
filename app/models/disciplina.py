"""Disciplina escolar usada para organizar atividades."""

from exceptions.erros import ValidationError
from app.models.validacao import identificador_positivo, texto_obrigatorio


class Disciplina:
    """Matéria pesquisável no planejamento acadêmico."""

    def __init__(
        self, id_disciplina: int, nome_disciplina: str, descricao_disciplina: str = ""
    ) -> None:
        self._id_disciplina = identificador_positivo(id_disciplina, "ID da disciplina")
        self.nome_disciplina = nome_disciplina
        self.descricao_disciplina = descricao_disciplina

    @property
    def id_disciplina(self) -> int:
        """Identificador da disciplina."""
        return self._id_disciplina

    @property
    def nome_disciplina(self) -> str:
        """Nome da matéria."""
        return self._nome_disciplina

    @nome_disciplina.setter
    def nome_disciplina(self, valor: str) -> None:
        self._nome_disciplina = texto_obrigatorio(valor, "Disciplina", 100)

    @property
    def descricao_disciplina(self) -> str:
        """Descrição da matéria."""
        return self._descricao_disciplina

    @descricao_disciplina.setter
    def descricao_disciplina(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValidationError("A descrição da disciplina deve ser texto.")
        self._descricao_disciplina = valor.strip()
