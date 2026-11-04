"""Leitura e gravação dos dados em um arquivo JSON."""

import json
from pathlib import Path

from exceptions.erros import (DuplicateError, NotFoundError, PersistenceError)


class JsonRepository:
    """Guarda cada coleção (alunos, planos...) como uma lista de dicionários."""

    # nome da coleção -> campo que identifica cada registro
    IDS = {
        "usuarios": "id_usuario",
        "alunos": "id_aluno",
        "planos": "id_plano",
        "disciplinas": "id_disciplina",
        "atividades": "id_atividade",
        "materiais": "id_material",
        "atividade_materiais": "_id",
    }

    # campos que não podem se repetir (além do identificador)
    UNICOS = {
        "usuarios": ["email"],
        "alunos": ["id_usuario", "matricula"],
    }

    # coleção -> (coleção que depende dela, campo que aponta para ela)
    DEPENDENCIAS = {
        "usuarios": ("alunos", "id_usuario"),
        "alunos": ("planos", "id_aluno"),
        "planos": ("atividades", "id_plano"),
        "disciplinas": ("atividades", "id_disciplina"),
    }

    # coleção -> campo que a ligação atividade/material usa para apontar para ela
    LIGACOES = {
        "atividades": "id_atividade",
        "materiais": "id_material",
    }

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    # ---------- arquivo ----------
    def _carregar(self) -> dict:
        """Lê o arquivo. Se ele não existir, devolve todas as coleções vazias."""
        dados = {nome: [] for nome in self.IDS}
        if self.caminho.exists():
            try:
                with open(self.caminho, "r", encoding="utf-8") as arquivo:
                    dados.update(json.load(arquivo))
            except (json.JSONDecodeError, OSError):
                raise PersistenceError("Não foi possível ler o arquivo de dados.")
        return dados

    def _salvar(self, dados: dict) -> None:
        """Grava todas as coleções no arquivo."""
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            raise PersistenceError("Não foi possível salvar os dados.")

    # ---------- auxiliares ----------
    def _campo_id(self, colecao: str) -> str:
        """Confere se a coleção existe e devolve o nome do seu campo de ID."""
        if colecao not in self.IDS:
            raise PersistenceError(f"Coleção desconhecida: {colecao}.")
        return self.IDS[colecao]

    @staticmethod
    def _achar(registros: list[dict], campo: str, valor) -> dict | None:
        """Devolve o primeiro registro com esse valor no campo, ou None."""
        for registro in registros:
            if registro[campo] == valor:
                return registro
        return None

    def _conferir_repetidos(self, colecao: str, registro: dict, dados: dict) -> None:
        """Impede ID, e-mail ou matrícula repetidos."""
        campos = [self.IDS[colecao]] + self.UNICOS.get(colecao, [])
        for campo in campos:
            if self._achar(dados[colecao], campo, registro[campo]) is not None:
                raise DuplicateError(f"Já existe um registro com este valor em '{campo}'.")

    # ---------- consultas ----------
    def listar(self, colecao: str) -> list[dict]:
        self._campo_id(colecao)
        return self._carregar()[colecao]

    def buscar(self, colecao: str, identificador: int) -> dict:
        campo_id = self._campo_id(colecao)
        registro = self._achar(self._carregar()[colecao], campo_id, identificador)
        if registro is None:
            raise NotFoundError(f"Registro {identificador} não encontrado em {colecao}.")
        return registro

    def proximo_id(self, colecao: str) -> int:
        """Maior ID existente + 1."""
        campo_id = self._campo_id(colecao)
        if colecao == "atividade_materiais":
            raise PersistenceError("A ligação usa um ID de texto, sem sequência numérica.")
        maior = 0
        for registro in self._carregar()[colecao]:
            if registro[campo_id] > maior:
                maior = registro[campo_id]
        return maior + 1

    # ---------- alterações ----------
    def criar(self, colecao: str, registro: dict) -> dict:
        return self.criar_em_lote([(colecao, registro)])[0]

    def criar_em_lote(self, itens: list[tuple[str, dict]]) -> list[dict]:
        """Cria vários registros com uma única gravação (ou nenhum, se der erro)."""
        dados = self._carregar()
        criados = []
        for colecao, registro in itens:
            self._campo_id(colecao)
            self._conferir_repetidos(colecao, registro, dados)
            dados[colecao].append(registro)
            criados.append(registro)
        self._salvar(dados)
        return criados

    def atualizar(self, colecao: str, identificador: int, alteracoes: dict) -> dict:
        """Altera campos de um registro (não use para trocar o ID)."""
        campo_id = self._campo_id(colecao)
        dados = self._carregar()
        registro = self._achar(dados[colecao], campo_id, identificador)
        if registro is None:
            raise NotFoundError(f"Registro {identificador} não encontrado em {colecao}.")
        registro.update(alteracoes)
        self._salvar(dados)
        return registro

    def remover(self, colecao: str, identificador: int | str) -> None:
        """Remove um registro, se nenhum outro depender dele."""
        campo_id = self._campo_id(colecao)
        dados = self._carregar()
        if self._achar(dados[colecao], campo_id, identificador) is None:
            raise NotFoundError(f"Registro {identificador} não encontrado em {colecao}.")

        if colecao in self.DEPENDENCIAS:
            destino, campo = self.DEPENDENCIAS[colecao]
            if self._achar(dados[destino], campo, identificador) is not None:
                raise PersistenceError(
                    f"Não é possível excluir: há registros relacionados em '{destino}'.")

        dados[colecao] = [r for r in dados[colecao] if r[campo_id] != identificador]

        # Ao remover uma atividade ou um material, apaga também as ligações dele
        if colecao in self.LIGACOES:
            campo = self.LIGACOES[colecao]
            dados["atividade_materiais"] = [
                ligacao for ligacao in dados["atividade_materiais"]
                if ligacao[campo] != identificador]
        self._salvar(dados)