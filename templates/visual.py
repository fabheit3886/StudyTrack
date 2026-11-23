import sys
import time
class Visual:

    cyan = "\033[96m" if sys.stdout.isatty() else ""
    blue = "\033[94m" if sys.stdout.isatty() else ""
    green = "\033[92m" if sys.stdout.isatty() else ""
    yellow = "\033[93m" if sys.stdout.isatty() else ""
    red = "\033[91m" if sys.stdout.isatty() else ""

    dim = "\033[2m" if sys.stdout.isatty() else ""
    bold = "\033[1m" if sys.stdout.isatty() else ""

    reset = "\033[0m" if sys.stdout.isatty() else ""

def cabecalho(
    titulo: str,
    subtitulo: str = ""
) -> None:

    print(
        f"\n{Visual.cyan}{Visual.bold}"
        "╭──────────────────────────────────────────────────────────╮"
        f"{Visual.reset}"
    )

    print(
        f"{Visual.cyan}{Visual.bold}"
        f"│  STUDYTRACK  ·  {titulo:<43}│"
        f"{Visual.reset}"
    )

    if subtitulo:
        print(
            f"{Visual.cyan}"
            f"│  {subtitulo[:54]:<54}│"
            f"{Visual.reset}"
        )

    print(
        f"{Visual.cyan}{Visual.bold}"
        "╰──────────────────────────────────────────────────────────╯"
        f"{Visual.reset}\n"
    )

def carregando(texto: str) -> None:

    if not sys.stdout.isatty():
        return

    sys.stdout.write(f"{Visual.dim}{texto} ")

    for simbolo in ("·", "••", "•••"):

        sys.stdout.write(
            f"\r{Visual.dim}{texto} {simbolo}{Visual.reset}"
        )

        sys.stdout.flush()

        time.sleep(0.08)

    sys.stdout.write(
        "\r" + " " * (len(texto) + 8) + "\r"
    )

    sys.stdout.flush()

def mensagem(
    texto: str,
    tipo: str = "info"
) -> None:

    cor = {
        "ok": Visual.green,
        "erro": Visual.red,
        "aviso": Visual.yellow,
        "info": Visual.cyan
    }.get(tipo, "")
    icone = {
        "ok": "✓",
        "erro": "✗",
        "aviso": "!",
        "info": "›"
    }.get(tipo, "›")

    print(
        f"{cor}{icone}  {texto}{Visual.reset}"
    )

def mostrar(itens: list[dict]) -> None:
    if not itens:
        mensagem(
            "Nenhum registro encontrado.",
            "aviso"
        )
        return

    ...