import sys
import time

from ui.visual import Visual, mensagem

ROTULOS = {
    "id_material": "ID do material", "nome_material": "Nome", "tipo": "Tipo",
    "descricao_material": "Sobre", "link": "Link", "categoria": "Categoria",
    "autor": "Autor", "id_atividade": "ID da atividade", "titulo": "Atividade",
    "descricao": "Detalhes", "prazo": "Prazo", "prioridade": "Prioridade",
    "status": "Situação", "id_plano": "ID", "nome_plano": "Plano",
    "objetivo": "Objetivo", "data_inicio": "Início", "data_fim": "Fim",
    "id_disciplina": "Disciplina", "nome_disciplina": "Disciplina",
    "descricao_disciplina": "Sobre", "id_aluno": "ID do aluno",
    "nome_usuario": "Aluno", "email": "E-mail", "matricula": "Matrícula",
    "turma": "Turma", "curso": "Curso",
}
STATUS = {"pendente": "Pendente", "em andamento": "Em andamento", "concluida": "Concluída"}
CAMPOS_OCULTOS = {"id_usuario", "senha"}


def mostrar(itens: list[dict]) -> None:
    """Exibe registros com rótulos familiares, sem nomes internos do banco."""
    if not itens:
        mensagem("Nenhum registro encontrado.", "aviso")
        return
    for item in itens:
        campos = []
        for chave, valor in item.items():
            if chave in CAMPOS_OCULTOS or chave.startswith("_"):
                continue
            if chave == "status":
                valor = STATUS.get(valor, valor)
            rotulo = ROTULOS.get(chave, chave.replace("_", " ").capitalize())
            campos.append(f"{rotulo}: {valor or '—'}")
        print(f"  {Visual.blue}•{Visual.reset} "
              + f"  {Visual.dim}|{Visual.reset}  ".join(campos))
        if sys.stdout.isatty():
            time.sleep(0.5)