'''Algoritmos de junção do MiniDB (Tópico 05 do guia).

Cada algoritmo recebe:
    varre_a, varre_b : funções SEM argumentos que, a cada chamada, devolvem as
                       linhas da tabela do zero (cada linha é uma lista de valores).
                       São funções, e não listas, porque o laço aninhado precisa
                       reler a tabela b inteira para cada linha de a.
    i                : posição (índice) da coluna de junção na tabela a
    j                : posição (índice) da coluna de junção na tabela b

E devolve (com yield) as linhas juntadas: colunas de a seguidas das colunas de b.
'''


def laco_aninhado(varre_a, varre_b, i, j):
    # custo em páginas: B(a) + |a| · B(b)
    #   B(a) = páginas de a, |a| = linhas de a, B(b) = páginas de b
    for r in varre_a():              # laço de FORA: cada linha de a, uma vez
        for s in varre_b():          # laço de DENTRO: relê b inteira para cada linha de a
            if r[i] == s[j]:         # condição do ON: a.x = b.y
                yield r + s          # linha de saída = colunas de a + colunas de b
