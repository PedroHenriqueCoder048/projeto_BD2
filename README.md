# SQLRunner (MiniDB)

Mini banco de dados em Python, feito na disciplina de Banco de Dados 2 (UFPA).
Executa `CREATE TABLE`, `INSERT`, `SELECT * ... WHERE` e `JOIN ... ON`, gravando
tudo em um arquivo `.db` organizado em páginas de 4096 bytes.

O objetivo é entender o que acontece por baixo de um comando SQL: do texto digitado
até os bytes no disco, passando por tokenizador, parser, catálogo, cache de páginas
e algoritmos de junção.

## Como rodar

Só é preciso o Python 3.10 ou mais novo. O MiniDB usa apenas a biblioteca padrão
(o `requirements.txt` instala o `pytest`, usado só nos testes).

**Um clique (Windows):** dê dois cliques em `rodar.bat`. Ele executa a demonstração
`testes/demo.sql` com os dois algoritmos de junção e compara os resultados.

**Pelo terminal:**

```
python minidb.py dados.db testes/consultas.sql     # roda um arquivo .sql
python minidb.py dados.db                          # modo interativo (um comando por linha)
python minidb.py dados.db < testes/consultas.sql   # também funciona (Git Bash, cmd, Linux)
```

No modo interativo, saia com `Ctrl+Z` e Enter (Windows) ou `Ctrl+D` (Linux).
Se o `.db` não existir, ele é criado. Para recomeçar do zero, apague o arquivo.

**Testes:**

```
pip install -r requirements.txt
python -m pytest testes -v
```

## Comandos suportados

```sql
CREATE TABLE aluno (id INT, nome CHAR(20));
INSERT INTO aluno VALUES (1, 'Ana');
SELECT * FROM aluno;
SELECT * FROM aluno WHERE id = 1;
SELECT * FROM aluno JOIN nota ON aluno.id = nota.aluno_id;
SELECT * FROM aluno INNER JOIN nota ON aluno.id = nota.aluno_id;
```

Tipos: `INT` (32 bits) e `CHAR(n)`. Um comando por linha, `;` opcional, palavras-chave em
maiúsculas ou minúsculas, linhas iniciadas por `--` são comentários.

Saída de exemplo:

```
OK
OK 1
1|20260001
(1 linha)
```

Erros aparecem como `ERRO: ...` e o programa continua rodando. A análise semântica roda
antes de qualquer gravação, então um comando inválido não escreve nenhum byte no arquivo.

## JOIN: dois algoritmos

| Algoritmo | Como funciona | Custo |
|---|---|---|
| Hash join (padrão) | monta um dicionário com a tabela menor e sonda com a maior | cerca de n + m |
| Laço aninhado | para cada linha de A, percorre B inteira | n × m |

Para trocar de algoritmo, defina a variável de ambiente `MINIDB_JUNCAO`:

```
# PowerShell
$env:MINIDB_JUNCAO = "laco"
python minidb.py dados.db testes/demo.sql

# Git Bash / Linux
MINIDB_JUNCAO=laco python minidb.py dados.db testes/demo.sql
```

Os dois devolvem o mesmo resultado (há um teste que confere isso).

## Como um comando é executado

```
texto -> tokeniza() -> Parser -> análise semântica -> execução (cache de páginas -> disco)
```

1. **Tokenizador** (`tokeniza`): separa o texto em tokens (palavra-chave, nome, número, texto, símbolo).
2. **Parser** (`Parser`): monta a árvore do comando (um dicionário).
3. **Análise semântica** (`confere`, `_executa_juncao`): confere tabela, colunas e tipos.
4. **Execução** (`executa`): lê ou grava páginas pelo cache.

Formato da página: cabeçalho de 16 bytes (`<ii8x`: registros ocupados e tamanho do registro)
seguido dos registros de tamanho fixo. O catálogo (descrição das tabelas) é uma tabela comum
na página 1.

## Estrutura do projeto

```
minidb.py              executável principal
executar.py            demonstração com um clique (usada pelo rodar.bat)
rodar.bat              dois cliques: roda a demonstração
rodar_testes.bat       dois cliques: roda os testes
SQLRunner/
  config.py            Database (páginas), Cache (cache de páginas), BPlusTree (árvore B+)
  sqlrunner.py         tokenizador, parser, catálogo, análise semântica e executor
  juncao.py            laço aninhado e hash join
testes/
  consultas.sql        exemplo do professor
  saida_esperada.txt   saída esperada do exemplo
  demo.sql             roteiro da demonstração
  test_minidb.py       testes de aceitação
  teste_bplus.py       exemplo da árvore B+
reports/               relatórios (diários) de cada etapa
```

## Limitações conhecidas

- Cada tabela ocupa uma única página de 4096 bytes. Quando enche, o `INSERT` retorna `ERRO: página N cheia`.
- Só existe `SELECT *` (não dá para escolher colunas) e `WHERE coluna = valor`.
- `WHERE` junto com `JOIN` não é suportado (retorna erro).
- JOIN apenas entre duas tabelas diferentes, por igualdade.
- Não há `UPDATE`, `DELETE`, `DROP` nem `LEFT/RIGHT JOIN`.
- A árvore B+ existe e é testada (`BPlusTree`), mas ainda não é usada pelo `SELECT`, que faz varredura completa.
- O cache usa a política "a mais antiga primeiro" (FIFO), com 3 páginas de capacidade.

## Relatórios

Os relatórios de cada etapa estão em `reports/`, um arquivo por dia (`AAAA-MM-DD.md`).
