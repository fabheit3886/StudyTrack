"""Ponto de entrada do StudyTrack."""

import time

from app.repositories.database import JsonRepository
from app.services.studytrack_service import StudyTrackService
from config import CAMINHO_DB
from ui.menu_inicial import executar_menu
from ui.visual import carregando, mensagem


def main() -> None:
    """Prepara dados demonstrativos e inicia o sistema."""
    servico = StudyTrackService(JsonRepository(CAMINHO_DB))
    carregando("Preparando seu espaço de estudos")
    servico.garantir_dados_demo()
    mensagem(
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