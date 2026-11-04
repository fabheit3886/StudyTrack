"""Casos de uso da aplicação StudyTrack."""

import hashlib
import hmac
import secrets
from datetime import date
from typing import Any

from app.models.aluno import Aluno
from app.models.atividade import Atividade
from app.models.atividade_material import AtividadeMaterial
from app.models.disciplina import Disciplina
from app.models.material import Material
from app.models.plano_estudo import PlanoEstudo
from app.repositories.database import JsonRepository
from exceptions.erros import NotFoundError, ValidationError


class StudyTrackService:
    """Coordena validação de domínio e persistência dos casos de uso."""

    def __init__(self, repositorio: JsonRepository) -> None:
        self.repositorio = repositorio

    def autenticar_aluno(self, email: str, senha: str) -> dict[str, Any]:
        """Autentica aluno usando o hash derivado armazenado."""
        email = email.strip().lower()
        conta = next((item for item in self.repositorio.listar("usuarios") if item["email"] == email), None)
        if conta is None or not self._verificar_senha(senha, conta["senha"]):
            raise ValidationError("E-mail ou senha inválidos.")
        perfil = next((item for item in self.repositorio.listar("alunos")
                       if item["id_usuario"] == conta["id_usuario"]), None)
        if perfil is None:
            raise ValidationError("Esta conta não possui perfil de aluno.")
        return {**perfil, "nome_usuario": conta["nome_usuario"], "email": conta["email"]}

    @staticmethod
    def _verificar_senha(senha: str, senha_armazenada: str) -> bool:
        """Compara a senha informada com o hash PBKDF2 persistido."""
        try:
            algoritmo, salt_hex, hash_hex = senha_armazenada.split("$", 2)
            if algoritmo != "pbkdf2_sha256":
                return False
            salt = bytes.fromhex(salt_hex)
            esperado = bytes.fromhex(hash_hex)
        except (AttributeError, ValueError):
            return False
        calculado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 200_000)
        return hmac.compare_digest(calculado, esperado)

    def garantir_catalogo_demo(self) -> None:
        """Insere recursos fictícios somente quando o catálogo estiver vazio."""
        if self.repositorio.listar("materiais"):
            return
        exemplos = [
            ("Python para Iniciantes", "Livro", "Introdução à lógica, variáveis e funções.", "", "Programação", "Equipe StudyTrack"),
            ("Banco de Dados: Primeiros Passos", "Livro", "Conceitos de tabelas, chaves e consultas SQL.", "", "Banco de Dados", "Biblioteca Escolar"),
            ("Guia de Matemática Básica", "Apostila", "Revisão de frações, equações e funções.", "", "Matemática", "Núcleo de Estudos"),
            ("Fundamentos de Biologia", "Livro", "Células, genética e ecologia em linguagem introdutória.", "", "Biologia", "Acervo Demonstrativo"),
            ("Redação: estrutura do texto dissertativo", "Artigo", "Material de apoio para planejar e revisar redações.", "", "Português", "Oficina de Redação"),
            ("Física no Cotidiano", "Livro", "Exemplos de mecânica e energia aplicados ao dia a dia.", "", "Física", "Acervo Demonstrativo"),
        ]
        for exemplo in exemplos:
            self.cadastrar_material(*exemplo)

    def garantir_disciplinas_demo(self) -> None:
        """Disponibiliza disciplinas fictícias para iniciar um plano de estudos."""
        existentes = {item["nome_disciplina"] for item in self.repositorio.listar("disciplinas")}
        for nome in ("Matemática", "Português", "Programação", "Banco de Dados", "Biologia", "História", "Física"):
            if nome not in existentes:
                self.criar_disciplina(nome)

    def garantir_dados_demo(self) -> None:
        """Inicializa um cenário fictício completo sem recriar dados existentes."""
        self.garantir_catalogo_demo()
        self.garantir_disciplinas_demo()
        if self.repositorio.listar("usuarios"):
            return
        ana = self.cadastrar_aluno(
            "Ana Demonstração", "ana.demo@studytrack.local", "Estudos123",
            "DEMO001", "2INFO-A", "Informática para Internet",
        )
        bruno = self.cadastrar_aluno(
            "Bruno Demonstração", "bruno.demo@studytrack.local", "Estudos123",
            "DEMO002", "2INFO-B", "Informática para Internet",
        )
        plano_ana = self.criar_plano(
            ana["id_aluno"], "Trilha de Programação", "Praticar lógica e Python",
            "Pequenas sessões de estudo ao longo da semana.",
        )
        plano_bruno = self.criar_plano(
            bruno["id_aluno"], "Revisão de Exatas", "Revisar matemática e física",
            "Plano de demonstração independente do perfil da Ana.",
        )
        prog = next(item for item in self.repositorio.listar("disciplinas")
                    if item["nome_disciplina"] == "Programação")
        mat = next(item for item in self.repositorio.listar("disciplinas")
                   if item["nome_disciplina"] == "Matemática")
        fis = next(item for item in self.repositorio.listar("disciplinas")
                   if item["nome_disciplina"] == "Física")
        atividade_ana = self.criar_atividade(
            plano_ana["id_plano"], prog["id_disciplina"], "Resolver exercícios de Python",
            "Praticar condicionais e laços.", prioridade="alta",
        )
        self.criar_atividade(
            plano_ana["id_plano"], prog["id_disciplina"], "Revisar funções",
            "Escrever exemplos curtos.", prioridade="media",
        )
        atividade_bruno = self.criar_atividade(
            plano_bruno["id_plano"], mat["id_disciplina"], "Revisar equações",
            "Resolver uma lista de exercícios.", prioridade="alta",
        )
        self.criar_atividade(
            plano_bruno["id_plano"], fis["id_disciplina"], "Estudar energia",
            "Ler o material e anotar dúvidas.", prioridade="media",
        )
        python = next(item for item in self.repositorio.listar("materiais")
                      if item["nome_material"] == "Python para Iniciantes")
        matematica = next(item for item in self.repositorio.listar("materiais")
                          if item["nome_material"] == "Guia de Matemática Básica")
        self.associar_material(atividade_ana["id_atividade"], python["id_material"])
        self.associar_material(atividade_bruno["id_atividade"], matematica["id_material"])

    def adicionar_material_admin(self, nome: str, tipo: str, descricao: str = "",
                                 link: str = "", categoria: str = "", autor: str = "") -> dict[str, Any]:
        """Caso de uso administrativo para incluir item no catálogo."""
        return self.cadastrar_material(nome, tipo, descricao, link, categoria, autor)

    def remover_material_admin(self, id_material: int) -> None:
        """Remove um item do catálogo e seus vínculos de estudo."""
        self.repositorio.remover("materiais", id_material)

    def listar_atividades_aluno(self, id_aluno: int) -> list[dict[str, Any]]:
        """Lista somente tarefas pertencentes aos planos do aluno autenticado."""
        planos = {item["id_plano"] for item in self.repositorio.listar("planos")
                  if item["id_aluno"] == id_aluno}
        return [item for item in self.repositorio.listar("atividades")
                if item["id_plano"] in planos]

    def listar_planos_aluno(self, id_aluno: int) -> list[dict[str, Any]]:
        """Lista exclusivamente os planos do aluno conectado."""
        return [item for item in self.repositorio.listar("planos")
                if item["id_aluno"] == id_aluno]

    def atualizar_atividade_aluno(self, id_aluno: int, id_atividade: int, *,
                                  prioridade: str | None = None,
                                  status: str | None = None) -> dict[str, Any]:
        """Impede que um aluno altere a atividade de outra pessoa."""
        atividade = self.repositorio.buscar("atividades", id_atividade)
        plano = self.repositorio.buscar("planos", atividade["id_plano"])
        if plano["id_aluno"] != id_aluno:
            raise NotFoundError("Atividade não encontrada nos seus planos.")
        return self.atualizar_atividade(id_atividade, prioridade=prioridade, status=status)

    def criar_atividade_aluno(self, id_aluno: int, id_plano: int, id_disciplina: int,
                              titulo: str, descricao: str = "", prazo: date | None = None,
                              prioridade: str = "media") -> dict[str, Any]:
        """Cria atividade apenas dentro de um plano pertencente ao aluno."""
        plano = self.repositorio.buscar("planos", id_plano)
        if plano["id_aluno"] != id_aluno:
            raise NotFoundError("Plano não encontrado na sua conta.")
        return self.criar_atividade(id_plano, id_disciplina, titulo, descricao, prazo, prioridade)

    def associar_material_aluno(self, id_aluno: int, id_atividade: int,
                                id_material: int) -> dict[str, Any]:
        """Vincula recurso somente a uma atividade dos planos do aluno."""
        atividade = self.repositorio.buscar("atividades", id_atividade)
        plano = self.repositorio.buscar("planos", atividade["id_plano"])
        if plano["id_aluno"] != id_aluno:
            raise NotFoundError("Atividade não encontrada nos seus planos.")
        return self.associar_material(id_atividade, id_material)

    @staticmethod
    def _hash_senha(senha: str) -> str:
        """Deriva um hash com salt para não persistir senha em texto puro."""
        if not isinstance(senha, str) or len(senha) < 8:
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")
        salt = secrets.token_bytes(16)
        chave = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 200_000)
        return f"pbkdf2_sha256${salt.hex()}${chave.hex()}"

    def cadastrar_aluno(
        self, nome: str, email: str, senha: str, matricula: str,
        turma: str, curso: str,
    ) -> dict[str, Any]:
        """Cadastra conta e perfil acadêmico em uma gravação atômica."""
        id_usuario = self.repositorio.proximo_id("usuarios")
        id_aluno = self.repositorio.proximo_id("alunos")
        aluno = Aluno(id_aluno, id_usuario, nome, email, self._hash_senha(senha), matricula, turma, curso)
        conta, perfil = self.repositorio.criar_em_lote([
            ("usuarios", {
                "id_usuario": aluno.id_usuario, "nome_usuario": aluno.nome_usuario,
                "email": aluno.email, "senha": aluno.senha,
            }),
            ("alunos", {
                "id_aluno": aluno.id_aluno, "id_usuario": aluno.id_usuario,
                "matricula": aluno.matricula, "turma": aluno.turma, "curso": aluno.curso,
            }),
        ])
        return {**perfil, "nome_usuario": conta["nome_usuario"], "email": conta["email"]}

    def criar_plano(
        self, id_aluno: int, nome: str, objetivo: str, descricao: str = "",
        data_inicio: date | None = None, data_fim: date | None = None,
    ) -> dict[str, Any]:
        """Cria um plano para um aluno existente."""
        self.repositorio.buscar("alunos", id_aluno)
        plano = PlanoEstudo(
            self.repositorio.proximo_id("planos"), id_aluno, nome, objetivo,
            descricao, data_inicio or date.today(), data_fim,
        )
        return self.repositorio.criar("planos", {
            "id_plano": plano.id_plano, "id_aluno": plano.id_aluno,
            "nome_plano": plano.nome_plano, "objetivo": plano.objetivo,
            "descricao": plano.descricao, "data_inicio": plano.data_inicio.isoformat(),
            "data_fim": plano.data_fim.isoformat() if plano.data_fim else None,
        })

    def criar_disciplina(self, nome: str, descricao: str = "") -> dict[str, Any]:
        """Adiciona uma disciplina ao catálogo acadêmico."""
        disciplina = Disciplina(self.repositorio.proximo_id("disciplinas"), nome, descricao)
        return self.repositorio.criar("disciplinas", {
            "id_disciplina": disciplina.id_disciplina,
            "nome_disciplina": disciplina.nome_disciplina,
            "descricao_disciplina": disciplina.descricao_disciplina,
        })

    def criar_atividade(
        self, id_plano: int, id_disciplina: int, titulo: str,
        descricao: str = "", prazo: date | None = None,
        prioridade: str = "media",
    ) -> dict[str, Any]:
        """Cria uma atividade validando plano e disciplina existentes."""
        self.repositorio.buscar("planos", id_plano)
        self.repositorio.buscar("disciplinas", id_disciplina)
        atividade = Atividade(
            self.repositorio.proximo_id("atividades"), id_plano, id_disciplina,
            titulo, descricao, prazo, prioridade,
        )
        return self.repositorio.criar("atividades", {
            "id_atividade": atividade.id_atividade, "id_plano": atividade.id_plano,
            "id_disciplina": atividade.id_disciplina, "titulo": atividade.titulo,
            "descricao": atividade.descricao,
            "prazo": atividade.prazo.isoformat() if atividade.prazo else None,
            "prioridade": atividade.prioridade, "status": atividade.status,
        })

    def cadastrar_material(
        self, nome: str, tipo: str, descricao: str = "", link: str = "",
        categoria: str = "", autor: str = "",
    ) -> dict[str, Any]:
        """Cadastra um livro ou outro recurso no catálogo."""
        material = Material(
            self.repositorio.proximo_id("materiais"), nome, tipo, descricao,
            link, categoria, autor,
        )
        return self.repositorio.criar("materiais", {
            "id_material": material.id_material, "nome_material": material.nome_material,
            "tipo": material.tipo, "descricao_material": material.descricao_material,
            "link": material.link, "categoria": material.categoria, "autor": material.autor,
        })

    def associar_material(self, id_atividade: int, id_material: int) -> dict[str, Any]:
        """Vincula material do catálogo a uma atividade existente."""
        self.repositorio.buscar("atividades", id_atividade)
        self.repositorio.buscar("materiais", id_material)
        associacao = AtividadeMaterial(id_atividade, id_material)
        return self.repositorio.criar("atividade_materiais", {
            "_id": f"{associacao.id_atividade}:{associacao.id_material}",
            "id_atividade": associacao.id_atividade,
            "id_material": associacao.id_material,
        })

    def atualizar_atividade(
        self, id_atividade: int, *, prioridade: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Altera prioridade/status após validar todo o objeto."""
        atual = self.repositorio.buscar("atividades", id_atividade)
        atividade = Atividade(
            atual["id_atividade"], atual["id_plano"], atual["id_disciplina"],
            atual["titulo"], atual.get("descricao", ""),
            date.fromisoformat(atual["prazo"]) if atual.get("prazo") else None,
            prioridade or atual["prioridade"], status or atual["status"],
        )
        return self.repositorio.atualizar("atividades", id_atividade, {
            "prioridade": atividade.prioridade, "status": atividade.status,
        })

    def buscar_catalogo(
        self, termo: str = "", id_disciplina: int | None = None,
    ) -> list[dict[str, Any]]:
        """Busca por nome/assunto ou limita aos materiais usados na disciplina."""
        termo = termo.strip().casefold()
        materiais = self.repositorio.listar("materiais")
        if id_disciplina is not None:
            self.repositorio.buscar("disciplinas", id_disciplina)
            atividades = {
                item["id_atividade"] for item in self.repositorio.listar("atividades")
                if item["id_disciplina"] == id_disciplina
            }
            materiais_vinculados = {
                item["id_material"] for item in self.repositorio.listar("atividade_materiais")
                if item["id_atividade"] in atividades
            }
            materiais = [item for item in materiais if item["id_material"] in materiais_vinculados]
        if termo:
            materiais = [item for item in materiais if termo in " ".join((
                item.get("nome_material", ""), item.get("descricao_material", ""),
                item.get("categoria", ""), item.get("autor", ""),
            )).casefold()]
        return materiais

    def listar(self, collection: str) -> list[dict[str, Any]]:
        """Lista registros para as telas de consulta do terminal."""
        return self.repositorio.listar(collection)

    def excluir(self, collection: str, identificador: int) -> None:
        """Remove um registro quando as regras de relacionamento permitem."""
        self.repositorio.remover(collection, identificador)

    def resumo_usuario(self, id_aluno: int) -> str:
        """Usa o comportamento sobrescrito de Aluno para exibir seu perfil."""
        perfil = self.repositorio.buscar("alunos", id_aluno)
        conta = self.repositorio.buscar("usuarios", perfil["id_usuario"])
        aluno = Aluno(
            perfil["id_aluno"], conta["id_usuario"], conta["nome_usuario"],
            conta["email"], conta["senha"], perfil["matricula"],
            perfil["turma"], perfil["curso"],
        )
        return aluno.resumo()
