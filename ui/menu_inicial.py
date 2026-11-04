from getpass import getpass

from app.services.studytrack_service import StudyTrackService
from config import ADMIN_LOGIN, ADMIN_PASSWORD
from exceptions.erros import StudyTrackError
from ui.tela_admin import tela_admin
from ui.tela_aluno import tela_aluno
from ui.visual import Visual, faixa, mensagem


def _criar_conta(servico):
    aluno = servico.cadastrar_aluno(
        input("Nome: "),
        input("E-mail: "),
        getpass("Crie uma senha (mínimo 8 caracteres): "),
        input("Matrícula: "),
        input("Turma: "),
        input("Curso: "),
    )
    mensagem("Conta criada. Bem-vindo ao seu espaço de estudos!", "ok")
    tela_aluno(servico, aluno)


def _entrar_aluno(servico):
    aluno = servico.autenticar_aluno(input("E-mail: "), getpass("Senha: "))
    tela_aluno(servico, aluno)


def _entrar_admin(servico):
    login = input("Login administrativo: ").strip()
    senha = getpass("Senha administrativa: ")
    if login != ADMIN_LOGIN or senha != ADMIN_PASSWORD:
        mensagem("Login ou senha administrativa inválidos.", "erro")
        return
    tela_admin(servico)


ACOES = {"1": _criar_conta, "2": _entrar_aluno, "3": _entrar_admin}


def executar_menu(servico: StudyTrackService) -> None:
    """Menu inicial com caminhos separados para aluno e administrador."""
    while True:
        faixa("ACOMPANHE SEUS ESTUDOS",
              "Organize tarefas e encontre materiais para estudar")
        print("1  Criar conta de aluno")
        print("2  Entrar como aluno")
        print("3  Entrar como administrador")
        print(f"{Visual.dim}0  Sair{Visual.reset}")
        opcao = input("\n> ").strip()
        if opcao == "0":
            print("Até logo!")
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
            continue
        try:
            acao(servico)
        except (StudyTrackError, ValueError) as erro:
            mensagem(f"Não foi possível concluir: {erro}", "erro")