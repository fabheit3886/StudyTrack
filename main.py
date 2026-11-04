"""Ponto de entrada com interfaces separadas para aluno e administrador."""

from datetime import date
from getpass import getpass
from pathlib import Path
import sys
import time

from app.repositories.database import JsonRepository
from app.services.studytrack_service import StudyTrackService
from exceptions.erros import StudyTrackError

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

ADMIN_LOGIN = "admin"
ADMIN_PASSWORD = "admin123"


class Visual:
    """Paleta ANSI usada para manter uma apresentação consistente no terminal."""

    cyan = "\033[96m" if sys.stdout.isatty() else ""
    blue = "\033[94m" if sys.stdout.isatty() else ""
    green = "\033[92m" if sys.stdout.isatty() else ""
    yellow = "\033[93m" if sys.stdout.isatty() else ""
    red = "\033[91m" if sys.stdout.isatty() else ""
    dim = "\033[2m" if sys.stdout.isatty() else ""
    bold = "\033[1m" if sys.stdout.isatty() else ""
    reset = "\033[0m" if sys.stdout.isatty() else ""


def _faixa(titulo: str, subtitulo: str = "") -> None:
    """Desenha um cabeçalho simples e alinhado para cada área."""
    print(
        f"\n{Visual.cyan}{Visual.bold}╭──────────────────────────────────────────────────────────╮{Visual.reset}"
    )
    print(f"{Visual.cyan}{Visual.bold}│  STUDYTRACK  ·  {titulo:<43}│{Visual.reset}")
    if subtitulo:
        print(f"{Visual.cyan}│  {subtitulo[:54]:<54}│{Visual.reset}")
    print(
        f"{Visual.cyan}{Visual.bold}╰──────────────────────────────────────────────────────────╯{Visual.reset}\n"
    )


def _carregando(texto: str) -> None:
    """Mostra uma animação breve sem poluir saídas redirecionadas."""
    if not sys.stdout.isatty():
        return
    sys.stdout.write(f"{Visual.dim}{texto} ")
    for simbolo in ("·", "••", "•••"):
        sys.stdout.write(f"\r{Visual.dim}{texto} {simbolo}{Visual.reset}")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(texto) + 8) + "\r")
    sys.stdout.flush()


def _mensagem(texto: str, tipo: str = "info") -> None:
    """Exibe respostas com cor sem alterar o conteúdo em terminal sem ANSI."""
    cor = {
        "ok": Visual.green,
        "erro": Visual.red,
        "aviso": Visual.yellow,
        "info": Visual.cyan,
    }.get(tipo, "")
    icone = {"ok": "✓", "erro": "✗", "aviso": "!", "info": "›"}.get(tipo, "›")
    print(f"{cor}{icone}  {texto}{Visual.reset}")


def _inteiro(pergunta: str) -> int:
    """Lê identificador numérico com mensagem amigável."""
    try:
        return int(input(pergunta).strip())
    except ValueError as erro:
        raise ValueError("Informe um número inteiro válido.") from erro


def _data(pergunta: str, obrigatoria: bool = False) -> date | None:
    """Lê uma data ISO opcional ou obrigatória."""
    valor = input(pergunta).strip()
    if not valor and not obrigatoria:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError as erro:
        raise ValueError("Use o formato de data AAAA-MM-DD.") from erro


def _mostrar(itens: list[dict]) -> None:
    """Exibe registros com rótulos familiares, sem nomes internos do banco."""
    if not itens:
        _mensagem("Nenhum registro encontrado.", "aviso")
        return
    rotulos = {
        "id_material": "ID do material",
        "nome_material": "Nome",
        "tipo": "Tipo",
        "descricao_material": "Sobre",
        "link": "Link",
        "categoria": "Categoria",
        "autor": "Autor",
        "id_atividade": "ID da atividade",
        "titulo": "Atividade",
        "descricao": "Detalhes",
        "prazo": "Prazo",
        "prioridade": "Prioridade",
        "status": "Situação",
        "id_plano": "ID",
        "nome_plano": "Plano",
        "objetivo": "Objetivo",
        "data_inicio": "Início",
        "data_fim": "Fim",
        "id_disciplina": "Disciplina",
        "nome_disciplina": "Disciplina",
        "descricao_disciplina": "Sobre",
        "id_aluno": "ID do aluno",
        "nome_usuario": "Aluno",
        "email": "E-mail",
        "matricula": "Matrícula",
        "turma": "Turma",
        "curso": "Curso",
    }
    internos = {"id_usuario"}
    for item in itens:
        campos = []
        for chave, valor in item.items():
            if chave == "senha" or chave.startswith("_") or chave in internos:
                continue
            rotulo = rotulos.get(chave, chave.replace("_", " ").capitalize())
            if chave == "status":
                valor = {
                    "pendente": "Pendente",
                    "em andamento": "Em andamento",
                    "concluida": "Concluída",
                }.get(valor, valor)
            campos.append(f"{rotulo}: {valor or '—'}")
        print(
            f"  {Visual.blue}•{Visual.reset} "
            + f"  {Visual.dim}|{Visual.reset}  ".join(campos)
        )
        if sys.stdout.isatty():
            time.sleep(0.5)


def _tela_aluno(servico: StudyTrackService, aluno: dict) -> None:
    """Oferece ferramentas de acompanhamento para o aluno autenticado."""
    while True:
        planos = servico.listar_planos_aluno(aluno["id_aluno"])
        tarefas = servico.listar_atividades_aluno(aluno["id_aluno"])
        concluidas = sum(t["status"] == "concluida" for t in tarefas)
        _faixa(
            f"OLÁ, {aluno['nome_usuario'].upper()}",
            f"Seu progresso: {concluidas}/{len(tarefas)} tarefas concluídas  ·  {len(planos)} plano(s)",
        )
        print(f"{Visual.green}1{Visual.reset}  Criar plano de estudo")
        print(f"{Visual.green}2{Visual.reset}  Criar atividade")
        print(f"{Visual.green}3{Visual.reset}  Ver minhas atividades")
        print(f"{Visual.green}4{Visual.reset}  Atualizar prioridade/status")
        print(f"{Visual.green}5{Visual.reset}  Buscar materiais no catálogo")
        print(f"{Visual.green}6{Visual.reset}  Associar material a uma atividade minha")
        print(f"{Visual.dim}0  Sair da conta{Visual.reset}")
        opcao = input("\n> ").strip()
        try:
            if opcao == "1":
                resultado = servico.criar_plano(
                    aluno["id_aluno"],
                    input("Nome do plano: "),
                    input("Objetivo de estudo: "),
                    input("Descrição (opcional): "),
                    _data("Data de início (AAAA-MM-DD, vazio = hoje): "),
                    _data("Data de fim (AAAA-MM-DD, opcional): "),
                )
                _mensagem(f"Plano criado com ID {resultado['id_plano']}.", "ok")
            elif opcao == "2":
                if not planos:
                    _mensagem("Crie um plano antes de adicionar atividades.", "aviso")
                    continue
                disciplinas = servico.listar("disciplinas")
                print("Seus planos:")
                _mostrar(planos)
                print("Disciplinas:")
                _mostrar(disciplinas)
                prazo = _data("Prazo (AAAA-MM-DD, opcional): ")
                resultado = servico.criar_atividade_aluno(
                    aluno["id_aluno"],
                    _inteiro("ID do seu plano: "),
                    _inteiro("ID da disciplina: "),
                    input("Atividade: "),
                    input("Detalhes: "),
                    prazo,
                    input("Prioridade (baixa/media/alta, padrão media): ")
                    .strip()
                    .lower()
                    or "media",
                )
                _mensagem(f"Atividade criada com ID {resultado['id_atividade']}.", "ok")
            elif opcao == "3":
                _mostrar(tarefas)
            elif opcao == "4":
                _mostrar(tarefas)
                atividade_id = _inteiro("ID da sua atividade: ")
                prioridade = (
                    input("Prioridade nova (vazio mantém): ").strip().lower() or None
                )
                status = (
                    input(
                        "Status novo (pendente/em andamento/concluida, vazio mantém): "
                    )
                    .strip()
                    .lower()
                    or None
                )
                servico.atualizar_atividade_aluno(
                    aluno["id_aluno"],
                    atividade_id,
                    prioridade=prioridade,
                    status=status,
                )
                _mensagem("Acompanhamento atualizado.", "ok")
            elif opcao == "5":
                termo = input("Busque por título, assunto, categoria ou autor: ")
                _mostrar(servico.buscar_catalogo(termo))
            elif opcao == "6":
                _mostrar(tarefas)
                materiais = servico.buscar_catalogo()
                _mostrar(materiais)
                atividade_id = _inteiro("ID da sua atividade: ")
                if not any(t["id_atividade"] == atividade_id for t in tarefas):
                    raise ValueError("A atividade não pertence à sua conta.")
                material_id = _inteiro("ID do material: ")
                servico.associar_material_aluno(
                    aluno["id_aluno"], atividade_id, material_id
                )
                _mensagem("Material associado à atividade.", "ok")
            elif opcao == "0":
                return
            else:
                print("Escolha uma opção do menu.")
        except (StudyTrackError, ValueError) as erro:
            _mensagem(f"Não foi possível concluir: {erro}", "erro")


def _tela_admin(servico: StudyTrackService) -> None:
    """Permite ao administrador manter o catálogo da biblioteca."""
    while True:
        _faixa(
            "ADMINISTRAÇÃO DO ACERVO",
            "Cadastro e manutenção dos materiais da biblioteca",
        )
        print("1  Ver catálogo")
        print("2  Adicionar material")
        print("3  Remover material")
        print(f"{Visual.dim}0  Sair da área administrativa{Visual.reset}")
        opcao = input("\n> ").strip()
        try:
            if opcao == "1":
                _mostrar(servico.buscar_catalogo())
            elif opcao == "2":
                item = servico.adicionar_material_admin(
                    input("Título/nome: "),
                    input("Tipo: "),
                    input("Descrição/assunto: "),
                    input("Link (opcional): "),
                    input("Categoria/disciplina: "),
                    input("Autor: "),
                )
                _mensagem(
                    f"Material adicionado ao catálogo com ID {item['id_material']}.",
                    "ok",
                )
            elif opcao == "3":
                _mostrar(servico.buscar_catalogo())
                servico.remover_material_admin(_inteiro("ID do material a remover: "))
                _mensagem("Material removido do catálogo.", "ok")
            elif opcao == "0":
                return
            else:
                print("Escolha uma opção do menu.")
        except (StudyTrackError, ValueError) as erro:
            _mensagem(f"Não foi possível concluir: {erro}", "erro")


def executar_menu(servico: StudyTrackService) -> None:
    """Menu inicial com caminhos separados para aluno e administrador."""
    while True:
        _faixa(
            "ACOMPANHE SEUS ESTUDOS",
            "Organize tarefas e encontre materiais para estudar",
        )
        print("1  Criar conta de aluno")
        print("2  Entrar como aluno")
        print("3  Entrar como administrador")
        print(f"{Visual.dim}0  Sair{Visual.reset}")
        opcao = input("\n> ").strip()
        try:
            if opcao == "1":
                aluno = servico.cadastrar_aluno(
                    input("Nome: "),
                    input("E-mail: "),
                    getpass("Crie uma senha (mínimo 8 caracteres): "),
                    input("Matrícula: "),
                    input("Turma: "),
                    input("Curso: "),
                )
                _mensagem("Conta criada. Bem-vindo ao seu espaço de estudos!", "ok")
                _tela_aluno(servico, aluno)
            elif opcao == "2":
                aluno = servico.autenticar_aluno(input("E-mail: "), getpass("Senha: "))
                _tela_aluno(servico, aluno)
            elif opcao == "3":
                login = input("Login administrativo: ").strip()
                senha = getpass("Senha administrativa: ")
                if login != ADMIN_LOGIN or senha != ADMIN_PASSWORD:
                    _mensagem("Login ou senha administrativa inválidos.", "erro")
                    continue
                _tela_admin(servico)
            elif opcao == "0":
                print("Até logo!")
                return
            else:
                print("Escolha uma opção do menu.")
        except (StudyTrackError, ValueError) as erro:
            _mensagem(f"Não foi possível concluir: {erro}", "erro")


def main() -> None:
    """Prepara dados demonstrativos e inicia o sistema."""
    caminho = Path(__file__).resolve().parent / "data" / "studytrack.json"
    servico = StudyTrackService(JsonRepository(caminho))
    _carregando("Preparando seu espaço de estudos")
    servico.garantir_dados_demo()
    _mensagem(
        "Acessos de demonstração: ana.demo@studytrack.local / Estudos123 · "
        "bruno.demo@studytrack.local / Estudos123 · administrador: admin / admin123",
        "info",
    )
    try:
        executar_menu(servico)
    except (KeyboardInterrupt, EOFError):
        print("\nExecução encerrada.")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
