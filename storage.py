import os


PAGE_SIZE = 4096
DB_FILE = "dados.db"


def escreve_pagina(n, dados):
    if len(dados) != PAGE_SIZE:
        raise ValueError("A página deve ter exatamente 4096 bytes.")

    modo = "r+b" if os.path.exists(DB_FILE) else "w+b"

    with open(DB_FILE, modo) as arquivo:
        posicao = n * PAGE_SIZE
        arquivo.seek(posicao)
        arquivo.write(dados)


def le_pagina(n):
    with open(DB_FILE, "rb") as arquivo:
        posicao = n * PAGE_SIZE
        arquivo.seek(posicao)

        dados = arquivo.read(PAGE_SIZE)

        if len(dados) != PAGE_SIZE:
            raise ValueError("A página não existe ou está incompleta.")

        return dados
    