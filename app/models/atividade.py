"""Atividade acadêmica associada a um plano e a uma disciplina."""

from datetime import date

from exceptions.erros import ValidationError
from app.models.validacao import data_ou_nula, identificador_positivo, texto_obrigatorio


class Atividade:
    """Tarefa, prova, entrega ou revisão planejada pelo aluno."""

    PRIORIDADES = {"baixa", "media", "alta"}
    STATUS = {"pendente", "em andamento", "concluida"}

    def __init__(
        self,
        id_atividade: int,
        id_plano: int,
        id_disciplina: int,
        titulo: str,
        descricao: str = "",
        prazo: date | None = None,
        prioridade: str = "media",
        status: str = "pendente",
    ) -> None:
        self._id_atividade = identificador_positivo(id_atividade, "ID da atividade")
        self._id_plano = identificador_positivo(id_plano, "ID do plano")
        self._id_disciplina = identificador_positivo(id_disciplina, "ID da disciplina")
        self.titulo = titulo
        self.descricao = descricao
        self.prazo = prazo
        self.prioridade = prioridade
        self.status = status

    @property
    def id_atividade(self) -> int:
        """Identificador da atividade."""
        return self._id_atividade

    @property
    def id_plano(self) -> int:
        """Plano ao qual a atividade pertence."""
        return self._id_plano

    @property
    def id_disciplina(self) -> int:
        """Disciplina relacionada à atividade."""
        return self._id_disciplina

    @property
    def titulo(self) -> str:
        """Título da atividade."""
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self._titulo = texto_obrigatorio(valor, "Título", 150)

    @property
    def descricao(self) -> str:
        """Descrição da atividade."""
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor) > 500:
            raise ValidationError("A descrição deve ter até 500 caracteres.")
        self._descricao = valor.strip()

    @property
    def prazo(self) -> date | None:
        """Data limite opcional."""
        return self._prazo

    @prazo.setter
    def prazo(self, valor: date | None) -> None:
        self._prazo = data_ou_nula(valor, "Prazo")

    @property
    def prioridade(self) -> str:
        """Nível de prioridade definido pelo aluno."""
        return self._prioridade

    @prioridade.setter
    def prioridade(self, valor: str) -> None:
        valor = texto_obrigatorio(valor, "Prioridade", 20).lower()
        if valor not in self.PRIORIDADES:
            raise ValidationError("Prioridade deve ser baixa, media ou alta.")
        self._prioridade = valor

    @property
    def status(self) -> str:
        """Situação atual da atividade."""
        return self._status

    @status.setter
    def status(self, valor: str) -> None:
        valor = texto_obrigatorio(valor, "Status", 30).lower()
        if valor not in self.STATUS:
            raise ValidationError(
                "Status deve ser pendente, em andamento ou concluida."
            )
        self._status = valor

    def concluir(self) -> None:
        """Marca a atividade como concluída."""
        self.status = "concluida"
