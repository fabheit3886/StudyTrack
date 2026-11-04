"""Menu inicial: criar conta, entrar como aluno ou como administrador."""

from getpass import getpass

from app.menus.menu_admin import login_admin, menu_admin
from app.menus.menu_aluno import menu_aluno
from templates.visual import cabecalho, mensagem
from app.utils.decoradores import tratar_erros


@tratar_erros
def criar_conta(servico) -> None:
    aluno = servico.cadastrar_aluno(
        input("Nome: "), input("E-mail: "),
        getpass("Crie uma senha (mínimo 8 caracteres): "),
        input("Matrícula: "), input("Turma: "), input("Curso: "),
    )
    mensagem("Conta criada. Bem-vindo ao seu espaço de estudos!", "ok")
    menu_aluno(servico, aluno)


@tratar_erros
def entrar_aluno(servico) -> None:
    aluno = servico.autenticar_aluno(input("E-mail: "), getpass("Senha: "))
    menu_aluno(servico, aluno)


@tratar_erros
def entrar_admin(servico) -> None:
    if login_admin():
        menu_admin(servico)
    else:
        mensagem("Login ou senha administrativa inválidos.", "erro")


ACOES = {"1": criar_conta, "2": entrar_aluno, "3": entrar_admin}


def menu_inicial(servico) -> None:
    """Primeira tela do sistema."""
    mensagem("Acessos de demonstração: ana.demo@studytrack.local / Estudos123 "
             "| administrador: admin / admin123")
    while True:
        cabecalho("ACOMPANHE SEUS ESTUDOS", "Organize tarefas e encontre materiais")
        print("1  Criar conta de aluno")
        print("2  Entrar como aluno")
        print("3  Entrar como administrador")
        print("0  Sair")
        opcao = input("\n> ").strip()
        if opcao == "0":
            print("Até logo!")
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
        else:
            acao(servico)