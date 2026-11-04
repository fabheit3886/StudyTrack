"""Menu do aluno logado."""

from templates.visual import cabecalho, mensagem, mostrar
from app.utils.decoradores import tratar_erros
from app.utils.entradas import ler_data, ler_inteiro


@tratar_erros
def criar_plano(servico, aluno: dict) -> None:
    plano = servico.criar_plano(
        aluno["id_aluno"], input("Nome do plano: "), input("Objetivo de estudo: "),
        input("Descrição (opcional): "),
        ler_data("Data de início (AAAA-MM-DD, vazio = hoje): "),
        ler_data("Data de fim (AAAA-MM-DD, opcional): "),
    )
    mensagem(f"Plano criado com ID {plano['id_plano']}.", "ok")


@tratar_erros
def criar_atividade(servico, aluno: dict) -> None:
    planos = servico.listar_planos_aluno(aluno["id_aluno"])
    if not planos:
        mensagem("Crie um plano antes de adicionar atividades.", "aviso")
        return
    print("Seus planos:")
    mostrar(planos)
    print("Disciplinas:")
    mostrar(servico.listar("disciplinas"))
    atividade = servico.criar_atividade_aluno(
        aluno["id_aluno"], ler_inteiro("ID do seu plano: "),
        ler_inteiro("ID da disciplina: "), input("Atividade: "),
        input("Detalhes: "), ler_data("Prazo (AAAA-MM-DD, opcional): "),
        input("Prioridade (baixa/media/alta, padrão media): ").strip().lower() or "media",
    )
    mensagem(f"Atividade criada com ID {atividade['id_atividade']}.", "ok")


@tratar_erros
def ver_atividades(servico, aluno: dict) -> None:
    mostrar(servico.listar_atividades_aluno(aluno["id_aluno"]))


@tratar_erros
def atualizar_atividade(servico, aluno: dict) -> None:
    mostrar(servico.listar_atividades_aluno(aluno["id_aluno"]))
    id_atividade = ler_inteiro("ID da sua atividade: ")
    prioridade = input("Prioridade nova (vazio mantém): ").strip().lower() or None
    status = input("Status novo (pendente/em andamento/concluida, vazio mantém): ").strip().lower() or None
    servico.atualizar_atividade_aluno(
        aluno["id_aluno"], id_atividade, prioridade=prioridade, status=status)
    mensagem("Acompanhamento atualizado.", "ok")


@tratar_erros
def buscar_materiais(servico, aluno: dict) -> None:
    termo = input("Busque por título, assunto, categoria ou autor: ")
    mostrar(servico.buscar_catalogo(termo))


@tratar_erros
def associar_material(servico, aluno: dict) -> None:
    atividades = servico.listar_atividades_aluno(aluno["id_aluno"])
    mostrar(atividades)
    mostrar(servico.buscar_catalogo())
    id_atividade = ler_inteiro("ID da sua atividade: ")
    if not any(a["id_atividade"] == id_atividade for a in atividades):
        raise ValueError("A atividade não pertence à sua conta.")
    servico.associar_material_aluno(
        aluno["id_aluno"], id_atividade, ler_inteiro("ID do material: "))
    mensagem("Material associado à atividade.", "ok")


ACOES = {
    "1": criar_plano,
    "2": criar_atividade,
    "3": ver_atividades,
    "4": atualizar_atividade,
    "5": buscar_materiais,
    "6": associar_material,
}


def menu_aluno(servico, aluno: dict) -> None:
    """Repete o menu até o aluno escolher sair."""
    while True:
        planos = servico.listar_planos_aluno(aluno["id_aluno"])
        tarefas = servico.listar_atividades_aluno(aluno["id_aluno"])
        concluidas = sum(1 for t in tarefas if t["status"] == "concluida")
        cabecalho(f"OLÁ, {aluno['nome_usuario'].upper()}",
                  f"Progresso: {concluidas}/{len(tarefas)} tarefas  |  {len(planos)} plano(s)")
        print("1  Criar plano de estudo")
        print("2  Criar atividade")
        print("3  Ver minhas atividades")
        print("4  Atualizar prioridade/status")
        print("5  Buscar materiais no catálogo")
        print("6  Associar material a uma atividade")
        print("0  Sair da conta")
        opcao = input("\n> ").strip()
        if opcao == "0":
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
        else:
            acao(servico, aluno)