from datetime import date


class Atividade:
    def __init__(self, id_atividade: int, id_plano: int, id_disciplina: int, titulo: str, descricao: str, prazo: date, prioridade: str, status: str):
        self.id_atividade = id_atividade
        self.id_plano = id_plano
        self.id_disciplina = id_disciplina
        self.titulo = titulo
        self.descricao = descricao
        self.prazo = prazo
        self.prioridade = prioridade
        self.status = status
