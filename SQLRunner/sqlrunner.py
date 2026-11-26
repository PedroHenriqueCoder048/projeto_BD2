import os
import struct

from .juncao import hash_join, laco_aninhado
ALGORITMO_JUNCAO = {"hash": hash_join, "laco": laco_aninhado}

class ErroSintaxe(Exception):
    pass


PALAVRAS_CHAVE = {"CREATE", "TABLE", "INSERT", "INTO", "VALUES",
"SELECT", "FROM", "WHERE", "INT", "CHAR", "JOIN", "ON", "SET" ,"INNER" ,"AND"}
SIMBOLOS = "(),;*=."


def tokeniza(texto):
    tokens = []
    i = 0
    while i < len(texto):
        c = texto[i]

        if c.isspace():
            i += 1

        elif c in SIMBOLOS:
            tokens.append(("SIMBOLO", c))
            i += 1

        elif c == "'":
            i += 1
            partes = []
            while True:
                if i >= len(texto):
                    raise ErroSintaxe("texto sem aspa de fechamento")
                if texto[i] == "'":
                    if i + 1 < len(texto) and texto[i + 1] == "'":
                        partes.append("'")
                        i += 2
                        continue
                    i += 1
                    break
                partes.append(texto[i])
                i += 1
            tokens.append(("TEXTO", "".join(partes)))

        elif c.isdigit() or (c == "-" and i + 1 < len(texto) and texto[i + 1].isdigit()):
            inicio = i
            i += 1
            while i < len(texto) and texto[i].isdigit():
                i += 1
            tokens.append(("NUMERO", int(texto[inicio:i])))

        elif c.isalpha() or c == "_":
            inicio = i
            while i < len(texto) and (texto[i].isalnum() or texto[i] == "_"):
                i += 1
            palavra = texto[inicio:i]
            if palavra.upper() in PALAVRAS_CHAVE:
                tokens.append(("PALAVRA", palavra.upper()))
            else:
                tokens.append(("NOME", palavra))

        else:
            raise ErroSintaxe(f"caractere inesperado {c!r}")

    return tokens


FIM = ("FIM", None)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _olha(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else FIM

    def _consome(self, tipo, valor=None):
        token = self._olha()
        if token[0] != tipo or (valor is not None and token[1] != valor):
            esperado = valor if valor is not None else tipo.lower()
            veio = "fim do comando" if token == FIM else repr(token[1])
            raise ErroSintaxe(f"esperava {esperado}, veio {veio}")
        self.pos += 1
        return token[1]

    def analisa(self):
        token = self._olha()
        if token == ("PALAVRA", "CREATE"):
            arvore = self._create()
        elif token == ("PALAVRA", "INSERT"):
            arvore = self._insert()
        elif token == ("PALAVRA", "SELECT"):
            arvore = self._select()
        else:
            veio = "comando vazio" if token == FIM else repr(token[1])
            raise ErroSintaxe(f"comando desconhecido: {veio}")

        if self._olha() == ("SIMBOLO", ";"):
            self.pos += 1
        if self._olha() != FIM:
            raise ErroSintaxe(f"sobrou {self._olha()[1]!r} no fim do comando")
        return arvore

    def _create(self):
        self._consome("PALAVRA", "CREATE")
        self._consome("PALAVRA", "TABLE")
        tabela = self._consome("NOME")
        self._consome("SIMBOLO", "(")
        colunas = [self._coluna()]
        while self._olha() == ("SIMBOLO", ","):
            self.pos += 1
            colunas.append(self._coluna())
        self._consome("SIMBOLO", ")")
        return {"op": "CREATE", "tabela": tabela, "colunas": colunas}

    def _coluna(self):
        nome = self._consome("NOME")
        if self._olha() == ("PALAVRA", "INT"):
            self.pos += 1
            return (nome, "INT", 4)
        self._consome("PALAVRA", "CHAR")
        self._consome("SIMBOLO", "(")
        tamanho = self._consome("NUMERO")
        self._consome("SIMBOLO", ")")
        if tamanho <= 0:
            raise ErroSintaxe(f"CHAR({tamanho}) inválido")
        return (nome, "CHAR", tamanho)

    def _insert(self):
        self._consome("PALAVRA", "INSERT")
        self._consome("PALAVRA", "INTO")
        tabela = self._consome("NOME")
        self._consome("PALAVRA", "VALUES")
        self._consome("SIMBOLO", "(")
        valores = [self._valor()]
        while self._olha() == ("SIMBOLO", ","):
            self.pos += 1
            valores.append(self._valor())
        self._consome("SIMBOLO", ")")
        return {"op": "INSERT", "tabela": tabela, "valores": valores}

    def _valor(self):
        tipo, valor = self._olha()
        if tipo in ("NUMERO", "TEXTO"):
            self.pos += 1
            return valor
        veio = "fim do comando" if tipo == "FIM" else repr(valor)
        raise ErroSintaxe(f"esperava um valor, veio {veio}")

    def _select(self):
        self._consome("PALAVRA", "SELECT")
        self._consome("SIMBOLO", "*")
        self._consome("PALAVRA", "FROM")
        tabela = self._consome("NOME")

        juncao = None
        if self._olha() == ("PALAVRA", "INNER"):
            # INNER é opcional: "INNER JOIN" e "JOIN" significam a mesma coisa
            self.pos += 1
            self._consome("PALAVRA", "JOIN")
            juncao = True
        elif self._olha() == ("PALAVRA", "JOIN"):
            self.pos += 1
            juncao = True
        if juncao:
            outra = self._consome("NOME")
            self._consome("PALAVRA", "ON")
            esquerda = self._nome_qualificado()
            self._consome("SIMBOLO", "=")
            direita = self._nome_qualificado()
            juncao = {"tabela": outra, "esquerda": esquerda, "direita": direita}

        onde = None
        if self._olha() == ("PALAVRA", "WHERE"):
            self.pos += 1
            coluna = self._consome("NOME")
            self._consome("SIMBOLO", "=")
            onde = (coluna, self._valor())
        return {"op": "SELECT", "tabela": tabela, "juncao": juncao, "onde": onde}

    def _nome_qualificado(self):
        # tabela.coluna  ->  ("tabela", "coluna")
        tabela = self._consome("NOME")
        self._consome("SIMBOLO", ".")
        coluna = self._consome("NOME")
        return (tabela, coluna)


def analisa(texto):
    return Parser(tokeniza(texto)).analisa()


class Esquema:
    def __init__(self, colunas):
        self.colunas = colunas
        partes = ["i" if tipo == "INT" else f"{tamanho}s" for _, tipo, tamanho in colunas]
        self.formato = "<" + "".join(partes)
        self.tamanho = struct.calcsize(self.formato)

    def serializa(self, valores):
        dados = [v.encode("utf-8") if isinstance(v, str) else v for v in valores]
        return struct.pack(self.formato, *dados)

    def desserializa(self, dados):
        return [v.rstrip(b"\x00").decode("utf-8") if isinstance(v, bytes) else v
                for v in struct.unpack(self.formato, dados)]


def analisa_colunas(texto):
    colunas = []
    for parte in texto.split(","):
        nome, tipo = parte.split()
        if tipo.upper() == "INT":
            colunas.append((nome, "INT", 4))
        else:
            tamanho = int(tipo[tipo.index("(") + 1:tipo.index(")")])
            colunas.append((nome, "CHAR", tamanho))
    return colunas


CABECALHO = "<ii8x"
TAMANHO_CABECALHO = struct.calcsize(CABECALHO)

ESQUEMA_CATALOGO = Esquema([("nome", "CHAR", 32), ("primeira", "INT", 4),
                            ("colunas", "CHAR", 200)])
PAGINA_CATALOGO = 1


class ErroSemantico(Exception):
    pass


def insere_na_pagina(cache, n_pagina, esquema, valores):
    pagina = cache.fixa(n_pagina)
    ocupados, _ = struct.unpack_from("<ii", pagina, 0)
    inicio = TAMANHO_CABECALHO + ocupados * esquema.tamanho

    if inicio + esquema.tamanho > len(pagina):
        cache.solta(n_pagina)
        raise RuntimeError(f"página {n_pagina} cheia")

    pagina[inicio:inicio + esquema.tamanho] = esquema.serializa(valores)
    struct.pack_into("<ii", pagina, 0, ocupados + 1, esquema.tamanho)
    cache.solta(n_pagina, suja=True)


def le_registros(cache, n_pagina, esquema):
    pagina = cache.fixa(n_pagina)
    ocupados, _ = struct.unpack_from("<ii", pagina, 0)
    registros = []
    for slot in range(ocupados):
        inicio = TAMANHO_CABECALHO + slot * esquema.tamanho
        registros.append(esquema.desserializa(pagina[inicio:inicio + esquema.tamanho]))
    cache.solta(n_pagina)
    return registros


class Catalogo:
    def __init__(self, cache):
        self.cache = cache
        self.tabelas = {}
        for nome, primeira, colunas in le_registros(cache, PAGINA_CATALOGO, ESQUEMA_CATALOGO):
            self.tabelas[nome] = (primeira, Esquema(analisa_colunas(colunas)))

    def busca(self, nome):
        if nome not in self.tabelas:
            raise ErroSemantico(f"tabela {nome} não existe")
        return self.tabelas[nome]

    def registra(self, nome, primeira, colunas):
        insere_na_pagina(self.cache, PAGINA_CATALOGO, ESQUEMA_CATALOGO,
                         [nome, primeira, colunas])
        self.tabelas[nome] = (primeira, Esquema(analisa_colunas(colunas)))


def confere(catalogo, tabela, valores):
    primeira, esquema = catalogo.busca(tabela)

    if len(valores) != len(esquema.colunas):
        raise ErroSemantico(f"esperava {len(esquema.colunas)} valores, vieram {len(valores)}")

    for (nome, tipo, tamanho), valor in zip(esquema.colunas, valores):
        if tipo == "INT" and not isinstance(valor, int):
            raise ErroSemantico(f"coluna {nome} é INT, veio {valor!r}")
        if tipo == "INT" and not -2**31 <= valor < 2**31:
            raise ErroSemantico(f"coluna {nome} é INT de 32 bits, {valor} não cabe")
        if tipo == "CHAR" and (not isinstance(valor, str) or len(valor.encode("utf-8")) > tamanho):
            raise ErroSemantico(f"coluna {nome} é CHAR({tamanho}), veio {valor!r}")

    return primeira, esquema


def executa(arvore, catalogo, cache):
    if arvore["op"] == "CREATE":
        return _executa_create(arvore, catalogo, cache)

    if arvore["op"] == "INSERT":
        primeira, esquema = confere(catalogo, arvore["tabela"], arvore["valores"])
        insere_na_pagina(cache, primeira, esquema, arvore["valores"])
        return "OK 1"

    if arvore["op"] == "SELECT":
        return _executa_select(arvore, catalogo, cache)

    raise NotImplementedError(f"comando {arvore['op']} ainda não suportado")


def _proxima_pagina_livre(catalogo, cache):
    candidatas = [PAGINA_CATALOGO + 1]
    if os.path.exists(cache.database.DB_FILE):
        candidatas.append(os.path.getsize(cache.database.DB_FILE) // cache.database.PAGE_SIZE)
    candidatas += [primeira + 1 for primeira, _ in catalogo.tabelas.values()]
    candidatas += [n + 1 for n in cache.pages]
    return max(candidatas)


def _executa_create(arvore, catalogo, cache):
    nome, colunas = arvore["tabela"], arvore["colunas"]

    if nome in catalogo.tabelas:
        raise ErroSemantico(f"tabela {nome} já existe")
    if len(nome.encode("utf-8")) > 32:
        raise ErroSemantico(f"nome da tabela {nome} tem mais de 32 bytes")
    nomes = [c[0] for c in colunas]
    repetidas = sorted({n for n in nomes if nomes.count(n) > 1})
    if repetidas:
        raise ErroSemantico(f"coluna repetida: {', '.join(repetidas)}")

    texto = ", ".join(f"{n} INT" if t == "INT" else f"{n} CHAR({tam})" for n, t, tam in colunas)
    if len(texto.encode("utf-8")) > 200:
        raise ErroSemantico("descrição das colunas passa de 200 bytes")
    if TAMANHO_CABECALHO + Esquema(colunas).tamanho > cache.database.PAGE_SIZE:
        raise ErroSemantico("registro não cabe em uma página")

    primeira = _proxima_pagina_livre(catalogo, cache)
    catalogo.registra(nome, primeira, texto)
    cache.fixa(primeira)
    cache.solta(primeira, suja=True)
    return "OK"


def _executa_select(arvore, catalogo, cache):
    if arvore.get("juncao") is not None:
        return _executa_juncao(arvore, catalogo, cache)
    primeira, esquema = catalogo.busca(arvore["tabela"])
    registros = le_registros(cache, primeira, esquema)

    if arvore["onde"] is not None:
        coluna, valor = arvore["onde"]
        nomes = [c[0] for c in esquema.colunas]
        if coluna not in nomes:
            raise ErroSemantico(f"coluna {coluna} não existe")
        indice = nomes.index(coluna)
        tipo = esquema.colunas[indice][1]
        if (tipo == "INT") != isinstance(valor, int):
            raise ErroSemantico(f"coluna {coluna} é {tipo}, veio {valor!r}")
        registros = [r for r in registros if r[indice] == valor]

    return _formata(registros)


def _formata(registros):
    linhas = ["|".join(str(v) for v in r) for r in registros]
    n = len(registros)
    linhas.append(f"({n} linha)" if n == 1 else f"({n} linhas)")
    return "\n".join(linhas)


def _posicao_coluna(esquema, tabela, coluna):
    # devolve (posição da coluna no registro, tipo da coluna)
    nomes = [c[0] for c in esquema.colunas]
    if coluna not in nomes:
        raise ErroSemantico(f"coluna {tabela}.{coluna} não existe")
    i = nomes.index(coluna)
    return i, esquema.colunas[i][1]


def _executa_juncao(arvore, catalogo, cache):
    juncao = arvore["juncao"]
    nome_a, nome_b = arvore["tabela"], juncao["tabela"]

  
    primeira_a, esquema_a = catalogo.busca(nome_a)
    primeira_b, esquema_b = catalogo.busca(nome_b)
    if nome_a == nome_b:
        raise ErroSemantico("JOIN de uma tabela com ela mesma não é suportado")

    # 2) o ON compara uma coluna de a com uma de b (aceita a.x = b.y ou b.y = a.x)
    esquerda, direita = juncao["esquerda"], juncao["direita"]
    if (esquerda[0], direita[0]) == (nome_b, nome_a):
        esquerda, direita = direita, esquerda
    if (esquerda[0], direita[0]) != (nome_a, nome_b):
        raise ErroSemantico(f"o ON deve comparar uma coluna de {nome_a} com uma de {nome_b}")

    # 3) as colunas existem e os tipos batem (INT com INT, CHAR com CHAR)
    i, tipo_a = _posicao_coluna(esquema_a, nome_a, esquerda[1])
    j, tipo_b = _posicao_coluna(esquema_b, nome_b, direita[1])
    if tipo_a != tipo_b:
        raise ErroSemantico(f"tipos diferentes no ON: {nome_a}.{esquerda[1]} é {tipo_a}, "
                            f"{nome_b}.{direita[1]} é {tipo_b}")

    if arvore["onde"] is not None:
        raise NotImplementedError("WHERE junto com JOIN ainda não é suportado")

    # --- execução ---
    nome_algoritmo = os.environ.get("MINIDB_JUNCAO", "hash")
    if nome_algoritmo not in ALGORITMOS_JUNCAO:
        raise NotImplementedError(f"algoritmo de junção {nome_algoritmo} não existe (use hash ou laco)")
    algoritmo = ALGORITMOS_JUNCAO[nome_algoritmo]
    def varre_a():
        return le_registros(cache, primeira_a, esquema_a)

    def varre_b():
        return le_registros(cache, primeira_b, esquema_b)

    registros = list(algoritmo(varre_a, varre_b, i, j))
    return _formata(registros)


