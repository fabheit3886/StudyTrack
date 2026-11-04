"""Plano de estudo de um aluno."""

from datetime import date

from exceptions.erros import ValidationError
from app.models.validacao import data_ou_nula, identificador_positivo, texto_obrigatorio


class PlanoEstudo:
    """Agrupa objetivos e atividades dentro de um período."""

    def __init__(self, id_plano: int, id_aluno: int, nome_plano: str,
                 objetivo: str, descricao: str = "", data_inicio: date | None = None,
                 data_fim: date | None = None) -> None:
        self._id_plano = identificador_positivo(id_plano, "ID do plano")
        self._id_aluno = identificador_positivo(id_aluno, "ID do aluno")
        self.nome_plano = nome_plano
        self.objetivo = objetivo
        self.descricao = descricao
        self.data_inicio = data_inicio or date.today()
        self.data_fim = data_fim

    @property
    def id_plano(self) -> int:
        """Identificador do plano."""
        return self._id_plano

    @property
    def id_aluno(self) -> int:
        """Aluno responsável pelo plano."""
        return self._id_aluno

    @property
    def nome_plano(self) -> str:
        """Nome curto do plano."""
        return self._nome_plano

    @nome_plano.setter
    def nome_plano(self, valor: str) -> None:
        self._nome_plano = texto_obrigatorio(valor, "Nome do plano", 120)

    @property
    def objetivo(self) -> str:
        """Objetivo de aprendizagem do plano."""
        return self._objetivo

    @objetivo.setter
    def objetivo(self, valor: str) -> None:
        self._objetivo = texto_obrigatorio(valor, "Objetivo", 255)

    @property
    def descricao(self) -> str:
        """Descrição opcional do plano."""
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValidationError("A descrição do plano deve ser texto.")
        self._descricao = valor.strip()

    @property
    def data_inicio(self) -> date:
        """Data de início do plano."""
        return self._data_inicio

    @data_inicio.setter
    def data_inicio(self, valor: date) -> None:
        data = data_ou_nula(valor, "Data de início")
        if data is None:
            raise ValidationError("Data de início é obrigatória.")
        self._data_inicio = data
        if getattr(self, "_data_fim", None) and self._data_fim < data:
            raise ValidationError("A data de fim não pode anteceder o início.")

    @property
    def data_fim(self) -> date | None:
        """Data final opcional do plano."""
        return self._data_fim

    @data_fim.setter
    def data_fim(self, valor: date | None) -> None:
        data = data_ou_nula(valor, "Data de fim")
        if data is not None and data < self.data_inicio:
            raise ValidationError("A data de fim não pode anteceder o início.")
        self._data_fim = data
