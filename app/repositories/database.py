"""Leitura e gravação simples dos dados do StudyTrack em JSON."""

import json
import os
from pathlib import Path

from exceptions.erros import (
    DuplicateError,
    IntegrityError,
    NotFoundError,
    PersistenceError,
)


class JsonRepository:
    """Repositório que guarda cada tipo de registro em uma lista do arquivo JSON."""

    ids = {
        "usuarios": "id_usuario",
        "alunos": "id_aluno",
        "planos": "id_plano",
        "disciplinas": "id_disciplina",
        "atividades": "id_atividade",
        "materiais": "id_material",
        "atividade_materiais": "_id",
    }

    def __init__(self, caminho):
        self.caminho = Path(caminho)

    def _ler(self):
        """Lê o arquivo; se ele ainda não existir, começa com coleções vazias."""
        if not self.caminho.exists():
            return {nome: [] for nome in self.ids}
        try:
            with self.caminho.open(encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise IntegrityError("O arquivo de dados está corrompido.") from erro
        except OSError as erro:
            raise PersistenceError(f"Não foi possível ler os dados: {erro}") from erro

        if not isinstance(dados, dict):
            raise IntegrityError("A estrutura do arquivo de dados é inválida.")
        for nome in self.ids:
            dados.setdefault(nome, [])
            if not isinstance(dados[nome], list):
                raise IntegrityError(f"A lista '{nome}' está inválida.")
        return dados

    def _salvar(self, dados):
        """Escreve num arquivo temporário e só depois troca o arquivo principal."""
        temporario = self.caminho.with_suffix(".json.tmp")
        try:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with temporario.open("w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                arquivo.flush()
                os.fsync(arquivo.fileno())
            temporario.replace(self.caminho)
        except OSError as erro:
            temporario.unlink(missing_ok=True)
            raise PersistenceError(
                f"Não foi possível salvar os dados: {erro}"
            ) from erro

    def listar(self, colecao):
        """Retorna todos os registros de uma coleção."""
        self._validar_colecao(colecao)
        return self._ler()[colecao]

    def buscar(self, colecao, identificador):
        """Procura um registro pelo identificador."""
        self._validar_colecao(colecao)
        campo_id = self.ids[colecao]
        for registro in self._ler()[colecao]:
            if registro.get(campo_id) == identificador:
                return registro
        raise NotFoundError(f"Registro {identificador} não encontrado em {colecao}.")

    def proximo_id(self, colecao):
        """Calcula o próximo número de ID da coleção."""
        self._validar_colecao(colecao)
        if colecao == "atividade_materiais":
            raise PersistenceError("A associação usa dois IDs, não uma sequência.")
        campo_id = self.ids[colecao]
        return max([item[campo_id] for item in self.listar(colecao)] + [0]) + 1

    def criar(self, colecao, registro):
        """Adiciona um registro e salva o arquivo."""
        dados = self._ler()
        self._validar_colecao(colecao)
        novo = dict(registro)
        campo_id = self.ids[colecao]
        if colecao == "atividade_materiais":
            novo.setdefault("_id", f"{novo['id_atividade']}:{novo['id_material']}")
        else:
            novo.setdefault(campo_id, self.proximo_id(colecao))
        if any(item.get(campo_id) == novo[campo_id] for item in dados[colecao]):
            raise DuplicateError(f"Esse registro já existe em {colecao}.")
        self._verificar_unicidade(colecao, novo, dados[colecao])
        dados[colecao].append(novo)
        self._salvar(dados)
        return novo

    def criar_em_lote(self, registros):
        """Salva vários registros juntos; usado no cadastro de um aluno."""
        dados = self._ler()
        novos = []
        for colecao, registro in registros:
            self._validar_colecao(colecao)
            novo = dict(registro)
            campo_id = self.ids[colecao]
            novo.setdefault(campo_id, self.proximo_id(colecao))
            self._verificar_unicidade(colecao, novo, dados[colecao])
            dados[colecao].append(novo)
            novos.append(novo)
        self._salvar(dados)
        return novos

    def atualizar(self, colecao, identificador, alteracoes):
        """Troca os campos informados e mantém o mesmo ID."""
        dados = self._ler()
        campo_id = self.ids[colecao]
        for posicao, registro in enumerate(dados[colecao]):
            if registro.get(campo_id) == identificador:
                atualizado = {**registro, **alteracoes, campo_id: identificador}
                self._verificar_unicidade(
                    colecao, atualizado, dados[colecao], identificador
                )
                dados[colecao][posicao] = atualizado
                self._salvar(dados)
                return atualizado
        raise NotFoundError(f"Registro {identificador} não encontrado em {colecao}.")

    def remover(self, colecao, identificador):
        """Remove um registro e seus vínculos quando necessário."""
        dados = self._ler()
        campo_id = self.ids[colecao]
        encontrados = [
            item for item in dados[colecao] if item.get(campo_id) == identificador
        ]
        if not encontrados:
            raise NotFoundError(
                f"Registro {identificador} não encontrado em {colecao}."
            )
        dados[colecao] = [
            item for item in dados[colecao] if item.get(campo_id) != identificador
        ]
        if colecao in ("atividades", "materiais"):
            chave = "id_atividade" if colecao == "atividades" else "id_material"
            dados["atividade_materiais"] = [
                item
                for item in dados["atividade_materiais"]
                if item[chave] != identificador
            ]
        self._salvar(dados)

    def _validar_colecao(self, colecao):
        if colecao not in self.ids:
            raise PersistenceError(f"Coleção desconhecida: {colecao}.")

    @staticmethod
    def _verificar_unicidade(colecao, novo, existentes, ignorar=None):
        """Impede repetição de e-mail, matrícula ou associação."""
        campos = {
            "usuarios": ["email"],
            "alunos": ["id_usuario", "matricula"],
            "atividade_materiais": ["id_atividade", "id_material"],
        }.get(colecao, [])
        for item in existentes:
            if item.get(JsonRepository.ids[colecao]) == ignorar:
                continue
            if campos and all(item.get(campo) == novo.get(campo) for campo in campos):
                raise DuplicateError(f"Já existe um registro igual em {colecao}.")
