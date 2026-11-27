"""Roda a demonstração do SQLRunner com um clique.

Não altera nenhum código do projeto: só chama o minidb.py com o arquivo
testes/demo.sql, uma vez com cada algoritmo de junção (hash e laço aninhado).
Uso: dê dois cliques em rodar.bat, ou rode `python executar.py`.
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SQL = RAIZ / "testes" / "demo.sql"
BANCO = RAIZ / "demo.db"


def roda(algoritmo):
    BANCO.unlink(missing_ok=True)  # banco novo a cada execução
    ambiente = dict(os.environ, MINIDB_JUNCAO=algoritmo)
    r = subprocess.run([sys.executable, str(RAIZ / "minidb.py"), str(BANCO)],
                       input=SQL.read_text(encoding="utf-8"), capture_output=True,
                       text=True, encoding="utf-8", cwd=RAIZ, env=ambiente)
    return r.stdout.strip()


print("=== Comandos executados (testes/demo.sql) ===")
print(SQL.read_text(encoding="utf-8"))

saidas = {}
for nome in ("hash", "laco"):
    saidas[nome] = roda(nome)
    print(f"=== Resultado com junção: {nome} ===")
    print(saidas[nome])
    print()

print("Os dois algoritmos deram o mesmo resultado:", saidas["hash"] == saidas["laco"])
BANCO.unlink(missing_ok=True)
