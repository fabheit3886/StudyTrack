"""Dados de demonstração do StudyTrack."""


def criar_dados_demo(servico) -> None:

    if servico.listar("usuarios"):
        return

    ana = servico.cadastrar_aluno(
        "Ana Demo",
        "ana.demo@studytrack.local",
        "Estudos123",
        "2026001",
        "2INFO",
        "Informática"
    )

    plano = servico.criar_plano(
        ana["id_aluno"],
        "Plano Inicial",
        "Aprender POO"
    )

    disciplina = servico.criar_disciplina(
        "Programação Orientada a Objetos"
    )

    servico.criar_atividade(
        plano["id_plano"],
        disciplina["id_disciplina"],
        "Revisar Classes"
    )