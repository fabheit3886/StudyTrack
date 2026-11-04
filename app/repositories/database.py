"""Repositório JSON com gravação atômica e validação de integridade."""

import json
import os
from pathlib import Path
from typing import Any

from exceptions.erros import (
    DuplicateError, IntegrityError, NotFoundError, PersistenceError,
)


class JsonRepository:
    """Armazena entidades em JSON sem acoplar regras de negócio ao arquivo."""

    IDS = {
        "usuarios": "id_usuario", "alunos": "id_aluno",
        "planos": "id_plano", "disciplinas": "id_disciplina",
        "atividades": "id_atividade", "materiais": "id_material",
        "atividade_materiais": "_id",
    }
    COLLECTIONS = tuple(IDS)

    def __init__(self, caminho: str | Path) -> None:
        self.caminho = Path(caminho)

    def _carregar(self) -> dict[str, list[dict[str, Any]]]:
        """Carrega e valida o formato antes de expor os dados."""
        if not self.caminho.exists():
            return {collection: [] for collection in self.COLLECTIONS}
        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise IntegrityError("O arquivo de dados está corrompido.") from erro
        except OSError as erro:
            raise PersistenceError(f"Não foi possível ler os dados: {erro}") from erro
        if not isinstance(dados, dict):
            raise IntegrityError("A estrutura do arquivo de dados é inválida.")
        for collection in self.COLLECTIONS:
            registros = dados.setdefault(collection, [])
            if not isinstance(registros, list) or any(not isinstance(item, dict) for item in registros):
                raise IntegrityError(f"A coleção '{collection}' está inválida.")
            campo_id = self.IDS[collection]
            ids = [item.get(campo_id) for item in registros]
            ids_invalidos = (
                any(not isinstance(item_id, str) or not item_id for item_id in ids)
                if collection == "atividade_materiais"
                else any(not isinstance(item_id, int) or isinstance(item_id, bool) or item_id <= 0 for item_id in ids)
            )
            if ids_invalidos:
                raise IntegrityError(f"Há identificadores inválidos em '{collection}'.")
            if len(ids) != len(set(ids)):
                raise IntegrityError(f"Há identificadores duplicados em '{collection}'.")
        campos_unicos = {
            "usuarios": ("email",),
            "alunos": ("id_usuario", "matricula"),
            "atividade_materiais": ("id_atividade", "id_material"),
        }
        for collection, campos in campos_unicos.items():
            vistos: list[tuple[Any, ...]] = []
            for registro in dados[collection]:
                chave = tuple(registro.get(campo) for campo in campos)
                if chave in vistos:
                    raise IntegrityError(f"Há valores duplicados em '{collection}'.")
                vistos.append(chave)
        referencias = (
            ("alunos", "id_usuario", "usuarios", "id_usuario"),
            ("planos", "id_aluno", "alunos", "id_aluno"),
            ("atividades", "id_plano", "planos", "id_plano"),
            ("atividades", "id_disciplina", "disciplinas", "id_disciplina"),
            ("atividade_materiais", "id_atividade", "atividades", "id_atividade"),
            ("atividade_materiais", "id_material", "materiais", "id_material"),
        )
        for origem, campo, destino, campo_destino in referencias:
            ids_destino = {item[campo_destino] for item in dados[destino]}
            if any(item.get(campo) not in ids_destino for item in dados[origem]):
                raise IntegrityError(f"Há referência inválida em '{origem}.{campo}'.")
        return dados

    def _salvar(self, dados: dict[str, list[dict[str, Any]]]) -> None:
        """Grava primeiro em arquivo temporário e substitui o arquivo final."""
        temporario = self.caminho.with_suffix(self.caminho.suffix + ".tmp")
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                arquivo.write("\n")
                arquivo.flush()
                os.fsync(arquivo.fileno())
            temporario.replace(self.caminho)
        except OSError as erro:
            try:
                temporario.unlink(missing_ok=True)
            except OSError:
                pass
            raise PersistenceError(f"Não foi possível salvar os dados: {erro}") from erro

    def listar(self, collection: str) -> list[dict[str, Any]]:
        """Retorna cópias dos registros de uma coleção conhecida."""
        self._validar_colecao(collection)
        return [dict(item) for item in self._carregar()[collection]]

    def buscar(self, collection: str, identificador: int) -> dict[str, Any]:
        """Busca um registro pelo identificador ou informa que não existe."""
        self._validar_colecao(collection)
        campo_id = self.IDS[collection]
        for item in self._carregar()[collection]:
            if item[campo_id] == identificador:
                return dict(item)
        raise NotFoundError(f"Registro {identificador} não encontrado em {collection}.")

    def proximo_id(self, collection: str) -> int:
        """Calcula o próximo identificador da coleção."""
        self._validar_colecao(collection)
        if collection == "atividade_materiais":
            raise PersistenceError("A associação usa uma chave composta, sem sequência numérica.")
        registros = self._carregar()[collection]
        campo_id = self.IDS[collection]
        return max((item[campo_id] for item in registros), default=0) + 1

    def criar(self, collection: str, registro: dict[str, Any]) -> dict[str, Any]:
        """Cria um registro e grava a alteração."""
        return self.criar_em_lote([(collection, registro)])[0]

    def criar_em_lote(
        self, itens: list[tuple[str, dict[str, Any]]]
    ) -> list[dict[str, Any]]:
        """Cria vários registros em uma única gravação, ou nenhum."""
        dados = self._carregar()
        criados: list[dict[str, Any]] = []
        for collection, registro in itens:
            self._validar_colecao(collection)
            novo = dict(registro)
            campo_id = self.IDS[collection]
            if collection == "atividade_materiais":
                novo.setdefault("_id", f"{novo.get('id_atividade')}:{novo.get('id_material')}")
            else:
                novo.setdefault(campo_id, max((item[campo_id] for item in dados[collection]), default=0) + 1)
            if any(item[campo_id] == novo[campo_id] for item in dados[collection]):
                raise DuplicateError(f"O identificador já existe em {collection}.")
            self._validar_unicidade(collection, novo, dados)
            dados[collection].append(novo)
            criados.append(dict(novo))
        self._salvar(dados)
        return criados

    def atualizar(
        self, collection: str, identificador: int, alteracoes: dict[str, Any]
    ) -> dict[str, Any]:
        """Atualiza campos de um registro sem alterar sua chave primária."""
        self._validar_colecao(collection)
        dados = self._carregar()
        campo_id = self.IDS[collection]
        for indice, registro in enumerate(dados[collection]):
            if registro[campo_id] == identificador:
                atualizado = {**registro, **alteracoes, campo_id: identificador}
                self._validar_unicidade(collection, atualizado, dados, ignorar=identificador)
                dados[collection][indice] = atualizado
                self._salvar(dados)
                return dict(atualizado)
        raise NotFoundError(f"Registro {identificador} não encontrado em {collection}.")

    def remover(self, collection: str, identificador: int | str) -> None:
        """Remove registro, respeitando restrições e cascata da associação."""
        self._validar_colecao(collection)
        dados = self._carregar()
        campo_id = self.IDS[collection]
        registro = next(
            (item for item in dados[collection] if item[campo_id] == identificador), None,
        )
        if registro is None:
            raise NotFoundError(f"Registro {identificador} não encontrado em {collection}.")

        dependencias = {
            "usuarios": ("alunos", "id_usuario"),
            "alunos": ("planos", "id_aluno"),
            "planos": ("atividades", "id_plano"),
            "disciplinas": ("atividades", "id_disciplina"),
        }
        if collection in dependencias:
            destino, campo = dependencias[collection]
            if any(item.get(campo) == identificador for item in dados[destino]):
                raise PersistenceError(
                    f"Não é possível excluir: há registros relacionados em '{destino}'."
                )
        dados[collection] = [item for item in dados[collection] if item[campo_id] != identificador]
        if collection == "atividades":
            dados["atividade_materiais"] = [
                item for item in dados["atividade_materiais"]
                if item["id_atividade"] != identificador
            ]
        elif collection == "materiais":
            dados["atividade_materiais"] = [
                item for item in dados["atividade_materiais"]
                if item["id_material"] != identificador
            ]
        self._salvar(dados)

    def _validar_colecao(self, collection: str) -> None:
        if collection not in self.IDS:
            raise PersistenceError(f"Coleção desconhecida: {collection}.")

    @staticmethod
    def _validar_unicidade(
        collection: str, registro: dict[str, Any], dados: dict[str, list[dict[str, Any]]],
        ignorar: int | None = None,
    ) -> None:
        """Impede e-mails, matrículas e associações duplicados."""
        campos: tuple[str, ...] = ()
        if collection == "usuarios":
            campos = ("email",)
        elif collection == "alunos":
            campos = ("id_usuario", "matricula")
        elif collection == "atividade_materiais":
            campos = ("id_atividade", "id_material")
        for campo in campos:
            if any(
                item.get(campo) == registro.get(campo)
                and (ignorar is None or item.get(JsonRepository.IDS[collection]) != ignorar)
                for item in dados[collection]
            ):
                rotulo = "associação" if collection == "atividade_materiais" else campo
                raise DuplicateError(f"Já existe um registro com este {rotulo}.")
