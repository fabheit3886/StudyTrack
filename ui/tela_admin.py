from app.services.studytrack_service import StudyTrackService
from exceptions.erros import StudyTrackError
from ui import entrada
from ui.exibicao import mostrar
from ui.visual import Visual, faixa, mensagem


def _ver_catalogo(servico):
    mostrar(servico.buscar_catalogo())


def _adicionar(servico):
    item = servico.adicionar_material_admin(
        input("Título/nome: "),
        input("Tipo: "),
        input("Descrição/assunto: "),
        input("Link (opcional): "),
        input("Categoria/disciplina: "),
        input("Autor: "),
    )
    mensagem(f"Material adicionado ao catálogo com ID {item['id_material']}.", "ok")


def _remover(servico):
    mostrar(servico.buscar_catalogo())
    servico.remover_material_admin(entrada.inteiro("ID do material a remover: "))
    mensagem("Material removido do catálogo.", "ok")


ACOES = {"1": _ver_catalogo, "2": _adicionar, "3": _remover}


def tela_admin(servico: StudyTrackService) -> None:
    """Permite ao administrador manter o catálogo da biblioteca."""
    while True:
        faixa("ADMINISTRAÇÃO DO ACERVO",
              "Cadastro e manutenção dos materiais da biblioteca")
        print("1  Ver catálogo")
        print("2  Adicionar material")
        print("3  Remover material")
        print(f"{Visual.dim}0  Sair da área administrativa{Visual.reset}")
        opcao = input("\n> ").strip()
        if opcao == "0":
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
            continue
        try:
            acao(servico)
        except (StudyTrackError, ValueError) as erro:
            mensagem(f"Não foi possível concluir: {erro}", "erro")