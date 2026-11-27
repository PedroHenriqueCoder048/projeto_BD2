"""Testes de aceitação do minidb (M1 a M4).

Rodam o minidb.py como processo separado, do mesmo jeito que o script do
professor: SQL na entrada padrão, resultado na saída padrão.
Rodar a partir da raiz do projeto:  python -m pytest testes -v
"""
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from SQLRunner.config import BPlusTree  # noqa: E402


def roda(sql, db, juncao=None):
    ambiente = dict(os.environ)
    if juncao:
        ambiente["MINIDB_JUNCAO"] = juncao  # "hash" (padrão) ou "laco"
    r = subprocess.run([sys.executable, str(RAIZ / "minidb.py"), str(db)],
                       input=sql, capture_output=True, text=True,
                       encoding="utf-8", cwd=RAIZ, env=ambiente)
    return r.stdout.strip().splitlines()


def test_exemplo_do_professor(tmp_path):
    sql = (RAIZ / "testes" / "consultas.sql").read_text(encoding="utf-8")
    esperado = (RAIZ / "testes" / "saida_esperada.txt").read_text(encoding="utf-8").split()
    assert " ".join(roda(sql, tmp_path / "t.db")) == " ".join(esperado)


def test_dados_persistem_depois_de_reabrir(tmp_path):
    db = tmp_path / "t.db"
    roda("CREATE TABLE a (x INT, nome CHAR(10));\nINSERT INTO a VALUES (7, 'ana');\n", db)
    assert roda("SELECT * FROM a;\n", db) == ["7|ana", "(1 linha)"]


def test_varias_tabelas(tmp_path):
    db = tmp_path / "t.db"
    saida = roda("CREATE TABLE a (x INT);\nCREATE TABLE b (y INT);\n"
                 "INSERT INTO a VALUES (1);\nINSERT INTO b VALUES (2);\nINSERT INTO b VALUES (3);\n"
                 "SELECT * FROM a;\nSELECT * FROM b;\n", db)
    assert saida == ["OK", "OK", "OK 1", "OK 1", "OK 1", "1", "(1 linha)", "2", "3", "(2 linhas)"]


def test_erros_nao_gravam_nada(tmp_path):
    db = tmp_path / "t.db"
    saida = roda("CREATE TABLE a (x INT, y INT);\n"
                 "SELECT * FROM nada;\n"
                 "INSERT INTO a VALUES (1);\n"
                 "INSERT INTO a VALUES ('texto', 2);\n"
                 "CREATE TABLE a (z INT);\n"
                 "SELECT * FROM a;\n", db)
    assert saida[0] == "OK"
    assert all(linha.startswith("ERRO:") for linha in saida[1:5])
    assert saida[5] == "(0 linhas)"


def test_cache_com_mais_paginas_que_a_capacidade(tmp_path):
    # capacidade do cache = 3; 5 tabelas = 5 páginas de dados + catálogo
    db = tmp_path / "t.db"
    sql = "".join(f"CREATE TABLE t{i} (x INT);\nINSERT INTO t{i} VALUES ({i});\n" for i in range(5))
    roda(sql, db)
    for i in range(5):
        assert roda(f"SELECT * FROM t{i};\n", db) == [str(i), "(1 linha)"]


TABELAS_JOIN = ("CREATE TABLE a (x INT, nome CHAR(10));\n"
                "CREATE TABLE b (y INT, cidade CHAR(10));\n"
                "INSERT INTO a VALUES (1, 'ana');\nINSERT INTO a VALUES (2, 'bia');\n"
                "INSERT INTO a VALUES (3, 'caio');\n"
                "INSERT INTO b VALUES (1, 'belem');\nINSERT INTO b VALUES (3, 'maraba');\n"
                "INSERT INTO b VALUES (5, 'santarem');\n")


def test_join_padrao(tmp_path):  # sem MINIDB_JUNCAO o padrão é o hash join
    saida = roda(TABELAS_JOIN + "SELECT * FROM a JOIN b ON a.x = b.y;\n", tmp_path / "t.db")
    assert saida[-3:] == ["1|ana|1|belem", "3|caio|3|maraba", "(2 linhas)"]


def test_join_on_invertido_da_o_mesmo_resultado(tmp_path):
    saida = roda(TABELAS_JOIN + "SELECT * FROM a JOIN b ON b.y = a.x;\n", tmp_path / "t.db")
    assert saida[-3:] == ["1|ana|1|belem", "3|caio|3|maraba", "(2 linhas)"]


def test_join_chave_repetida_e_sem_correspondencia(tmp_path):
    sql = ("CREATE TABLE a (x INT);\nCREATE TABLE b (y INT);\nCREATE TABLE c (z INT);\n"
           + "INSERT INTO a VALUES (7);\n" * 2 + "INSERT INTO b VALUES (7);\n" * 3
           + "INSERT INTO c VALUES (8);\n"
           + "SELECT * FROM a JOIN b ON a.x = b.y;\nSELECT * FROM a JOIN c ON a.x = c.z;\n")
    saida = roda(sql, tmp_path / "t.db")
    assert saida[-8:] == ["7|7"] * 6 + ["(6 linhas)", "(0 linhas)"]  # 2 x 3 = 6


def test_join_erros_semanticos(tmp_path):
    saida = roda(TABELAS_JOIN
                 + "SELECT * FROM a JOIN nada ON a.x = nada.y;\n"   # tabela inexistente
                 + "SELECT * FROM a JOIN b ON a.zzz = b.y;\n"       # coluna inexistente
                 + "SELECT * FROM a JOIN b ON a.x = b.cidade;\n"    # INT com CHAR
                 + "SELECT * FROM a JOIN b ON a.x = a.x;\n"         # ON sem a tabela b
                 + "SELECT * FROM a;\n", tmp_path / "t.db")
    assert all(linha.startswith("ERRO:") for linha in saida[-8:-4])
    assert saida[-1] == "(3 linhas)"  # o programa continuou rodando


def test_inner_join_igual_ao_join(tmp_path):
    saida = roda(TABELAS_JOIN
                 + "SELECT * FROM a INNER JOIN b ON a.x = b.y;\n"
                 + "SELECT * FROM a JOIN b ON a.x = b.y;\n", tmp_path / "t.db")
    resultado = ["1|ana|1|belem", "3|caio|3|maraba", "(2 linhas)"]
    assert saida[-6:] == resultado + resultado


def test_inner_join_minusculo_e_on_invertido(tmp_path):
    saida = roda(TABELAS_JOIN + "select * from a inner join b on b.y = a.x;\n", tmp_path / "t.db")
    assert saida[-3:] == ["1|ana|1|belem", "3|caio|3|maraba", "(2 linhas)"]


def test_inner_sem_join_e_erro_de_sintaxe(tmp_path):
    saida = roda(TABELAS_JOIN
                 + "SELECT * FROM a INNER b ON a.x = b.y;\n"   # faltou JOIN
                 + "SELECT * FROM a INNER;\n"                  # INNER no fim
                 + "SELECT * FROM a JOIN INNER b ON a.x = b.y;\n"  # ordem trocada
                 + "SELECT * FROM a;\n", tmp_path / "t.db")
    assert saida[-7] == "ERRO: esperava JOIN, veio 'b'"
    assert saida[-6] == "ERRO: esperava JOIN, veio ';'"
    assert saida[-5].startswith("ERRO:")
    assert saida[-1] == "(3 linhas)"  # o programa continuou rodando


def test_inner_join_erros_semanticos(tmp_path):
    saida = roda(TABELAS_JOIN
                 + "SELECT * FROM a INNER JOIN nada ON a.x = nada.y;\n"  # tabela inexistente
                 + "SELECT * FROM a INNER JOIN b ON a.x = b.cidade;\n",  # INT com CHAR
                 tmp_path / "t.db")
    assert all(linha.startswith("ERRO:") for linha in saida[-2:])


def test_arvore_bplus_busca_e_intervalo():
    arvore = BPlusTree(order=4)
    for chave in [50, 20, 70, 10, 30, 60, 80, 40, 90]:
        arvore.insert(chave, chave // 10, chave % 10)
    assert arvore.search(30) == (3, 0)
    assert arvore.search(99) is None
    assert [k for k, _ in arvore.range_search(25, 70)] == [30, 40, 50, 60, 70]
    assert not arvore.root.leaf  # houve divisão de nó


def test_hash_e_laco_aninhado_dao_o_mesmo_resultado(tmp_path):
    consulta = "SELECT * FROM a JOIN b ON a.x = b.y;\n"
    com_hash = roda(TABELAS_JOIN + consulta, tmp_path / "h.db", juncao="hash")
    com_laco = roda(TABELAS_JOIN + consulta, tmp_path / "l.db", juncao="laco")
    assert com_hash[-3:] == com_laco[-3:] == ["1|ana|1|belem", "3|caio|3|maraba", "(2 linhas)"]


def test_algoritmo_de_juncao_inexistente_da_erro(tmp_path):
    saida = roda(TABELAS_JOIN + "SELECT * FROM a JOIN b ON a.x = b.y;\n",
                 tmp_path / "t.db", juncao="xyz")
    assert saida[-1].startswith("ERRO:")


def test_arquivo_sql_como_argumento(tmp_path):
    r = subprocess.run([sys.executable, str(RAIZ / "minidb.py"), str(tmp_path / "t.db"),
                        str(RAIZ / "testes" / "consultas.sql")],
                       capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
    esperado = (RAIZ / "testes" / "saida_esperada.txt").read_text(encoding="utf-8").split()
    assert " ".join(r.stdout.split()) == " ".join(esperado)
