"""Regras do sistema: ficam entre os menus e o repositório."""

from datetime import date

from app.models.aluno import Aluno
from app.models.atividade import Atividade
from app.models.atividade_material import AtividadeMaterial
from app.models.disciplina import Disciplina
from app.models.material import Material
from app.models.plano_estudo import PlanoEstudo
from app.repositories.database import JsonRepository
from app.services.dados_demo import criar_dados_demo
from exceptions.erros import NotFoundError, ValidationError

class StudyTrackService:
    def __init__(self, repositorio: JsonRepository) -> None:
        self.repositorio = repositorio

    # ---------- auxiliares ----------
    def _procurar(self, colecao: str, campo: str, valor) -> dict | None:
        """Devolve o primeiro registro com esse valor no campo, ou None."""
        for item in self.repositorio.listar(colecao):
            if item[campo] == valor:
                return item
        return None

    @staticmethod
    def _juntar_conta_e_perfil(conta: dict, perfil: dict) -> dict:
        """Junta os dados do usuário com os do aluno em um só dicionário."""
        dados = dict(perfil)
        dados["nome_usuario"] = conta["nome_usuario"]
        dados["email"] = conta["email"]
        return dados

    @staticmethod
    def _texto_da_data(data: date | None) -> str | None:
        """Converte a data em texto para salvar no JSON."""
        return data.isoformat() if data else None

    def _plano_do_aluno(self, id_aluno: int, id_plano: int) -> dict:
        """Busca o plano e garante que ele pertence ao aluno."""
        plano = self.repositorio.buscar("planos", id_plano)
        if plano["id_aluno"] != id_aluno:
            raise NotFoundError("Plano não encontrado na sua conta.")
        return plano

    def _atividade_do_aluno(self, id_aluno: int, id_atividade: int) -> dict:
        """Busca a atividade e garante que ela está em um plano do aluno."""
        atividade = self.repositorio.buscar("atividades", id_atividade)
        plano = self.repositorio.buscar("planos", atividade["id_plano"])
        if plano["id_aluno"] != id_aluno:
            raise NotFoundError("Atividade não encontrada nos seus planos.")
        return atividade

    # ---------- contas ----------
    def cadastrar_aluno(self, nome: str, email: str, senha: str,
                        matricula: str, turma: str, curso: str) -> dict:
        """Cria a conta (usuário) e o perfil de aluno de uma vez."""
        senha = senha.strip()  # o modelo também remove espaços das pontas
        if len(senha) < 8:
            raise ValidationError("A senha deve ter pelo menos 8 caracteres.")

        id_usuario = self.repositorio.proximo_id("usuarios")
        id_aluno = self.repositorio.proximo_id("alunos")
        # Criar o objeto Aluno já valida todos os campos antes de salvar
        # Obs.: senha guardada como texto, simplificação só para o trabalho.
        aluno = Aluno(id_aluno, id_usuario, nome, email, senha, matricula, turma, curso)

        conta, perfil = self.repositorio.criar_em_lote([
            ("usuarios", {"id_usuario": aluno.id_usuario,
                          "nome_usuario": aluno.nome_usuario,
                          "email": aluno.email, "senha": aluno.senha}),
            ("alunos", {"id_aluno": aluno.id_aluno, "id_usuario": aluno.id_usuario,
                        "matricula": aluno.matricula, "turma": aluno.turma,
                        "curso": aluno.curso}),
        ])
        return self._juntar_conta_e_perfil(conta, perfil)

    def autenticar_aluno(self, email: str, senha: str) -> dict:
        conta = self._procurar("usuarios", "email", email.strip().lower())
        if conta is None or conta["senha"] != senha.strip():
            raise ValidationError("E-mail ou senha inválidos.")
        perfil = self._procurar("alunos", "id_usuario", conta["id_usuario"])
        if perfil is None:
            raise ValidationError("Esta conta não possui perfil de aluno.")
        return self._juntar_conta_e_perfil(conta, perfil)

    def resumo_usuario(self, id_aluno: int) -> str:
        """Mostra o resumo do aluno (usa o resumo() sobrescrito em Aluno)."""
        perfil = self.repositorio.buscar("alunos", id_aluno)
        conta = self.repositorio.buscar("usuarios", perfil["id_usuario"])
        aluno = Aluno(perfil["id_aluno"], conta["id_usuario"], conta["nome_usuario"],
                      conta["email"], conta["senha"], perfil["matricula"],
                      perfil["turma"], perfil["curso"])
        return aluno.resumo()

    # ---------- planos ----------
    def criar_plano(self, id_aluno: int, nome: str, objetivo: str, descricao: str = "",
                    data_inicio: date | None = None,
                    data_fim: date | None = None) -> dict:
        self.repositorio.buscar("alunos", id_aluno)  # garante que o aluno existe
        plano = PlanoEstudo(self.repositorio.proximo_id("planos"), id_aluno, nome,
                            objetivo, descricao, data_inicio or date.today(), data_fim)
        return self.repositorio.criar("planos", {
            "id_plano": plano.id_plano, "id_aluno": plano.id_aluno,
            "nome_plano": plano.nome_plano, "objetivo": plano.objetivo,
            "descricao": plano.descricao,
            "data_inicio": self._texto_da_data(plano.data_inicio),
            "data_fim": self._texto_da_data(plano.data_fim),
        })

    def listar_planos_aluno(self, id_aluno: int) -> list[dict]:
        return [p for p in self.repositorio.listar("planos") if p["id_aluno"] == id_aluno]

    # ---------- disciplinas ----------
    def criar_disciplina(self, nome: str, descricao: str = "") -> dict:
        disciplina = Disciplina(self.repositorio.proximo_id("disciplinas"), nome, descricao)
        return self.repositorio.criar("disciplinas", {
            "id_disciplina": disciplina.id_disciplina,
            "nome_disciplina": disciplina.nome_disciplina,
            "descricao_disciplina": disciplina.descricao_disciplina,
        })

    # ---------- atividades ----------
    def criar_atividade(self, id_plano: int, id_disciplina: int, titulo: str,
                        descricao: str = "", prazo: date | None = None,
                        prioridade: str = "media") -> dict:
        self.repositorio.buscar("planos", id_plano)
        self.repositorio.buscar("disciplinas", id_disciplina)
        atividade = Atividade(self.repositorio.proximo_id("atividades"), id_plano,
                              id_disciplina, titulo, descricao, prazo, prioridade)
        return self.repositorio.criar("atividades", {
            "id_atividade": atividade.id_atividade, "id_plano": atividade.id_plano,
            "id_disciplina": atividade.id_disciplina, "titulo": atividade.titulo,
            "descricao": atividade.descricao,
            "prazo": self._texto_da_data(atividade.prazo),
            "prioridade": atividade.prioridade, "status": atividade.status,
        })

    def atualizar_atividade(self, id_atividade: int, prioridade: str | None = None,
                            status: str | None = None) -> dict:
        atual = self.repositorio.buscar("atividades", id_atividade)
        prazo = date.fromisoformat(atual["prazo"]) if atual["prazo"] else None
        # Recria o objeto só para reaproveitar as validações da classe
        atividade = Atividade(
            atual["id_atividade"], atual["id_plano"], atual["id_disciplina"],
            atual["titulo"], atual["descricao"], prazo,
            prioridade or atual["prioridade"], status or atual["status"])
        return self.repositorio.atualizar("atividades", id_atividade, {
            "prioridade": atividade.prioridade, "status": atividade.status})

    def listar_atividades_aluno(self, id_aluno: int) -> list[dict]:
        ids_planos = [p["id_plano"] for p in self.listar_planos_aluno(id_aluno)]
        return [a for a in self.repositorio.listar("atividades")
                if a["id_plano"] in ids_planos]

    # ---------- versões "do aluno": só mexem no que é dele ----------
    def criar_atividade_aluno(self, id_aluno: int, id_plano: int, id_disciplina: int,
                              titulo: str, descricao: str = "", prazo: date | None = None,
                              prioridade: str = "media") -> dict:
        self._plano_do_aluno(id_aluno, id_plano)
        return self.criar_atividade(id_plano, id_disciplina, titulo, descricao,
                                    prazo, prioridade)

    def atualizar_atividade_aluno(self, id_aluno: int, id_atividade: int,
                                  prioridade: str | None = None,
                                  status: str | None = None) -> dict:
        self._atividade_do_aluno(id_aluno, id_atividade)
        return self.atualizar_atividade(id_atividade, prioridade, status)

    def associar_material_aluno(self, id_aluno: int, id_atividade: int,
                                id_material: int) -> dict:
        self._atividade_do_aluno(id_aluno, id_atividade)
        return self.associar_material(id_atividade, id_material)

    # ---------- materiais ----------
    def cadastrar_material(self, nome: str, tipo: str, descricao: str = "",
                           link: str = "", categoria: str = "", autor: str = "") -> dict:
        material = Material(self.repositorio.proximo_id("materiais"), nome, tipo,
                            descricao, link, categoria, autor)
        return self.repositorio.criar("materiais", {
            "id_material": material.id_material, "nome_material": material.nome_material,
            "tipo": material.tipo, "descricao_material": material.descricao_material,
            "link": material.link, "categoria": material.categoria,
            "autor": material.autor,
        })

    def associar_material(self, id_atividade: int, id_material: int) -> dict:
        self.repositorio.buscar("atividades", id_atividade)
        self.repositorio.buscar("materiais", id_material)
        ligacao = AtividadeMaterial(id_atividade, id_material)
        return self.repositorio.criar("atividade_materiais", {
            "_id": f"{ligacao.id_atividade}:{ligacao.id_material}",
            "id_atividade": ligacao.id_atividade,
            "id_material": ligacao.id_material,
        })

    def buscar_catalogo(self, termo: str = "",
                        id_disciplina: int | None = None) -> list[dict]:
        """Lista materiais, filtrando por texto e/ou por disciplina."""
        materiais = self.repositorio.listar("materiais")
        if id_disciplina is not None:
            usados = self._materiais_da_disciplina(id_disciplina)
            materiais = [m for m in materiais if m["id_material"] in usados]
        termo = termo.strip().lower()
        if termo:
            materiais = [m for m in materiais if termo in self._texto_do_material(m)]
        return materiais

    def _materiais_da_disciplina(self, id_disciplina: int) -> list[int]:
        """IDs dos materiais ligados a atividades dessa disciplina."""
        self.repositorio.buscar("disciplinas", id_disciplina)  # garante que existe
        ids_atividades = [a["id_atividade"] for a in self.repositorio.listar("atividades")
                          if a["id_disciplina"] == id_disciplina]
        return [v["id_material"] for v in self.repositorio.listar("atividade_materiais")
                if v["id_atividade"] in ids_atividades]

    @staticmethod
    def _texto_do_material(material: dict) -> str:
        """Junta os campos pesquisáveis em um texto só, em minúsculas."""
        campos = ("nome_material", "descricao_material", "categoria", "autor")
        return " ".join(material[campo] for campo in campos).lower()

    # ---------- administrador ----------
    def adicionar_material_admin(self, nome: str, tipo: str, descricao: str = "",
                                 link: str = "", categoria: str = "",
                                 autor: str = "") -> dict:
        return self.cadastrar_material(nome, tipo, descricao, link, categoria, autor)

    def remover_material_admin(self, id_material: int) -> None:
        self.repositorio.remover("materiais", id_material)

    # ---------- genéricos e demonstração ----------
    def listar(self, colecao: str) -> list[dict]:
        return self.repositorio.listar(colecao)

    def excluir(self, colecao: str, identificador: int) -> None:
        self.repositorio.remover(colecao, identificador)

    def garantir_dados_demo(self) -> None:
        criar_dados_demo(self)