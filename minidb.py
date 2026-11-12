import contextlib
import sys

from SQLRunner.config import Database, Cache
from SQLRunner.sqlrunner import Catalogo, ErroSemantico, ErroSintaxe, analisa, executa


def main():
    if len(sys.argv) != 2:
        print("uso: python minidb.py arquivo.db < consultas.sql", file=sys.stderr)
        sys.exit(1)

    for fluxo in (sys.stdin, sys.stdout, sys.stderr):
        fluxo.reconfigure(encoding="utf-8")

    nome = sys.argv[1]
    if nome.endswith(".db"):
        nome = nome[:-3]

    saida = sys.stdout

    with contextlib.redirect_stdout(sys.stderr):
        database = Database(nome)
        cache = Cache(database)
        catalogo = Catalogo(cache)

        for linha in sys.stdin:
            comando = linha.strip()
            if not comando or comando.startswith("--"):
                continue
            try:
                resultado = executa(analisa(comando), catalogo, cache)
                cache.descarrega()
            except (ErroSintaxe, ErroSemantico, RuntimeError, NotImplementedError) as erro:
                resultado = f"ERRO: {erro}"
            print(resultado, file=saida, flush=True)

        cache.descarrega()


if __name__ == "__main__":
    main()
