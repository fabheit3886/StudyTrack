"""Funções de exibição no terminal."""

LARGURA = 60

CAMPOS_OCULTOS = ("senha", "id_usuario")


def cabecalho(
    titulo: str,
    subtitulo: str = ""
) -> None:

    print("\n" + "=" * LARGURA)

    print(titulo.center(LARGURA))

    if subtitulo:
        print(subtitulo.center(LARGURA))

    print("=" * LARGURA)


def mensagem(texto: str, tipo: str = "info") -> None:
    simbolos = {
        "info": "[*]",
        "ok": "[OK]",
        "erro": "[ERRO]"
    }

    print(f"{simbolos.get(tipo, '[*]')} {texto}")


def mostrar(itens: list[dict]) -> None:
    if not itens:
        mensagem("Nenhum registro encontrado.")
        return

    for item in itens:
        dados = []

        for chave, valor in item.items():
            if chave in CAMPOS_OCULTOS:
                continue

            nome = chave.replace("_", " ").title()
            dados.append(f"{nome}: {valor}")

        print(" | ".join(dados))