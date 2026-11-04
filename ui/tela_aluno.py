from app.services.studytrack_service import StudyTrackService
from exceptions.erros import StudyTrackError
from ui import entrada
from ui.exibicao import mostrar
from ui.visual import Visual, faixa, mensagem


def _criar_plano(servico, aluno):
    resultado = servico.criar_plano(
        aluno["id_aluno"],
        input("Nome do plano: "),
        input("Objetivo de estudo: "),
        input("Descrição (opcional): "),
        entrada.data("Data de início (AAAA-MM-DD, vazio = hoje): "),
        entrada.data("Data de fim (AAAA-MM-DD, opcional): "),
    )
    mensagem(f"Plano criado com ID {resultado['id_plano']}.", "ok")


def _criar_atividade(servico, aluno):
    planos = servico.listar_planos_aluno(aluno["id_aluno"])
    if not planos:
        mensagem("Crie um plano antes de adicionar atividades.", "aviso")
        return
    print("Seus planos:")
    mostrar(planos)
    print("Disciplinas:")
    mostrar(servico.listar("disciplinas"))
    prazo = entrada.data("Prazo (AAAA-MM-DD, opcional): ")
    resultado = servico.criar_atividade_aluno(
        aluno["id_aluno"],
        entrada.inteiro("ID do seu plano: "),
        entrada.inteiro("ID da disciplina: "),
        input("Atividade: "),
        input("Detalhes: "),
        prazo,
        input("Prioridade (baixa/media/alta, padrão media): ").strip().lower() or "media",
    )
    mensagem(f"Atividade criada com ID {resultado['id_atividade']}.", "ok")


def _ver_atividades(servico, aluno):
    mostrar(servico.listar_atividades_aluno(aluno["id_aluno"]))


def _atualizar_atividade(servico, aluno):
    mostrar(servico.listar_atividades_aluno(aluno["id_aluno"]))
    atividade_id = entrada.inteiro("ID da sua atividade: ")
    prioridade = input("Prioridade nova (vazio mantém): ").strip().lower() or None
    status = input(
        "Status novo (pendente/em andamento/concluida, vazio mantém): "
    ).strip().lower() or None
    servico.atualizar_atividade_aluno(
        aluno["id_aluno"], atividade_id, prioridade=prioridade, status=status
    )
    mensagem("Acompanhamento atualizado.", "ok")


def _buscar_materiais(servico, aluno):
    termo = input("Busque por título, assunto, categoria ou autor: ")
    mostrar(servico.buscar_catalogo(termo))


def _associar_material(servico, aluno):
    tarefas = servico.listar_atividades_aluno(aluno["id_aluno"])
    mostrar(tarefas)
    mostrar(servico.buscar_catalogo())
    atividade_id = entrada.inteiro("ID da sua atividade: ")
    if not any(t["id_atividade"] == atividade_id for t in tarefas):
        raise ValueError("A atividade não pertence à sua conta.")
    material_id = entrada.inteiro("ID do material: ")
    servico.associar_material_aluno(aluno["id_aluno"], atividade_id, material_id)
    mensagem("Material associado à atividade.", "ok")


ACOES = {
    "1": _criar_plano,
    "2": _criar_atividade,
    "3": _ver_atividades,
    "4": _atualizar_atividade,
    "5": _buscar_materiais,
    "6": _associar_material,
}


def _cabecalho(servico, aluno):
    planos = servico.listar_planos_aluno(aluno["id_aluno"])
    tarefas = servico.listar_atividades_aluno(aluno["id_aluno"])
    concluidas = sum(t["status"] == "concluida" for t in tarefas)
    faixa(
        f"OLÁ, {aluno['nome_usuario'].upper()}",
        f"Seu progresso: {concluidas}/{len(tarefas)} tarefas concluídas  ·  {len(planos)} plano(s)",
    )
    g, r, d = Visual.green, Visual.reset, Visual.dim
    print(f"{g}1{r}  Criar plano de estudo")
    print(f"{g}2{r}  Criar atividade")
    print(f"{g}3{r}  Ver minhas atividades")
    print(f"{g}4{r}  Atualizar prioridade/status")
    print(f"{g}5{r}  Buscar materiais no catálogo")
    print(f"{g}6{r}  Associar material a uma atividade minha")
    print(f"{d}0  Sair da conta{r}")


def tela_aluno(servico: StudyTrackService, aluno: dict) -> None:
    """Oferece ferramentas de acompanhamento para o aluno autenticado."""
    while True:
        _cabecalho(servico, aluno)
        opcao = input("\n> ").strip()
        if opcao == "0":
            return
        acao = ACOES.get(opcao)
        if acao is None:
            print("Escolha uma opção do menu.")
            continue
        try:
            acao(servico, aluno)
        except (StudyTrackError, ValueError) as erro:
            mensagem(f"Não foi possível concluir: {erro}", "erro")