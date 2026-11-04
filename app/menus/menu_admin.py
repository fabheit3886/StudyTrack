"""Login e menu do administrador."""

from getpass import getpass

from templates.visual import cabecalho, mensagem, mostrar
from app.utils.decoradores import tratar_erros
from app.utils.entradas import ler_inteiro

ADMIN_LOGIN = "admin"
ADMIN_SENHA = "admin123"  # fixo, apenas para demonstração acadêmica


def login_admin() -> bool:
    """Pede login e senha e diz se estão corretos."""
    login = input("Login administrativo: ").strip()
    senha = getpass("Senha administrativa: ")
    return login == ADMIN_LOGIN and senha == ADMIN_SENHA


@tratar_erros
def ver_catalogo(servico) -> None:
    mostrar(servico.buscar_catalogo())


@tratar_erros
def adicionar_material(servico) -> None:
    item = servico.adicionar_material_admin(
        input("Título/nome: "), input("Tipo: "), input("Descrição/assunto: "),
        input("Link (opcional): "), input("Categoria/disciplina: "), input("Autor: "),
    )
    mensagem(f"Material adicionado com ID {item['id_material']}.", "ok")


@tratar_erros
def remover_material(servico) -> None:
    mostrar(servico.buscar_catalogo())
    servico.remover_material_admin(ler_inteiro("ID do material a remover: "))
    mensagem("Material removido do catálogo.", "ok")


ACOES = {"1": ver_catalogo, "2": adicionar_material, "3": remover_material}


def menu_admin(servico) -> None:
    """Repete o menu até o administrador escolher sair."""
    while True:
        cabecalho("ADMINISTRAÇÃO DO ACERVO", "Cadastro e manutenção dos materiais")
        print("1  Ver catálogo")
        print("2  Adicionar material")
        print("3  Remover material")
        print("0  Sair da área administrativa")
        opcao = input("\n> ").strip()
        if opcao == "0":
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
        else:
            acao(servico)