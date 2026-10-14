from datetime import date


class PlanoEstudo:
    def __init__(self, id_plano: int, id_aluno: int, nome_plano: str, objetivo: str, descricao: str, data_inicio: date, data_fim: date):
        self.id_plano = id_plano
        self.id_aluno = id_aluno
        self.nome_plano = nome_plano
        self.objetivo = objetivo
        self.descricao = descricao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
