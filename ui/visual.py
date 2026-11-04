import sys
import time

_TTY = sys.stdout.isatty()


class Visual:
    """Paleta ANSI usada para manter uma apresentação consistente no terminal."""

    cyan = "\033[96m" if _TTY else ""
    blue = "\033[94m" if _TTY else ""
    green = "\033[92m" if _TTY else ""
    yellow = "\033[93m" if _TTY else ""
    red = "\033[91m" if _TTY else ""
    dim = "\033[2m" if _TTY else ""
    bold = "\033[1m" if _TTY else ""
    reset = "\033[0m" if _TTY else ""


def faixa(titulo: str, subtitulo: str = "") -> None:
    """Desenha um cabeçalho simples e alinhado para cada área."""
    v = Visual
    print(f"\n{v.cyan}{v.bold}╭──────────────────────────────────────────────────────────╮{v.reset}")
    print(f"{v.cyan}{v.bold}│  STUDYTRACK  ·  {titulo:<43}│{v.reset}")
    if subtitulo:
        print(f"{v.cyan}│  {subtitulo[:54]:<54}│{v.reset}")
    print(f"{v.cyan}{v.bold}╰──────────────────────────────────────────────────────────╯{v.reset}\n")


def carregando(texto: str) -> None:
    if not _TTY:
        return
    for simbolo in ("·", "••", "•••"):
        sys.stdout.write(f"\r{Visual.dim}{texto} {simbolo}{Visual.reset}")
        sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write("\r" + " " * (len(texto) + 8) + "\r")
    sys.stdout.flush()


def mensagem(texto: str, tipo: str = "info") -> None:
    """Exibe respostas com cor sem alterar o conteúdo em terminal sem ANSI."""
    cor = {
        "ok": Visual.green,
        "erro": Visual.red,
        "aviso": Visual.yellow,
        "info": Visual.cyan,
    }.get(tipo, "")
    icone = {"ok": "✓", "erro": "✗", "aviso": "!", "info": "›"}.get(tipo, "›")
    print(f"{cor}{icone}  {texto}{Visual.reset}")