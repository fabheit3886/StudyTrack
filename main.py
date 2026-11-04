"""Ponto de entrada do sistema."""

from app.repositories.database import JsonRepository
from app.services.studytrack_service import StudyTrackService
from app.menus.menu_inicial import menu_inicial

def main() -> None:
    repositorio = JsonRepository("data/studytrack.json")

    servico = StudyTrackService(repositorio)

    servico.garantir_dados_demo()
    try:
        menu_inicial(servico)
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")

    except Exception as erro:
        print(f"\nErro inesperado: {erro}")
if __name__ == "__main__":
    main()