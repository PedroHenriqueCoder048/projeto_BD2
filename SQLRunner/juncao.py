def laco_aninhado(varre_a, varre_b, i, j):
    for r in varre_a():              
        for s in varre_b():          
            if r[i] == s[j]:         
                yield r + s         
def hash_join(varre_a,varre_b,i,j):
    linhas_a = list(varre_a())
    linhas_b = list(varre_b()) #cada tabela pe lida uma unica vez
    if len(linhas_a) <= len(linhas_b):
        construcao,sondagem = linhas_a,linhas_b
        col_construcao,col_sondagem= i,j
        a_na_construcao = True
    else:
        construcao, sondagem = linhas_b, linhas_a
        col_construcao, col_sondagem = j, i
        a_na_construcao = False
    tabela_hash = {}
    for linha in construcao:
        chave = linha[col_construcao]
        if chave not in tabela_hash:
            tabela_hash[chave]=[]
        tabela_hash[chave].append(linha)
        
    for linha in sondagem:
        chave = linha[col_sondagem]
        for par in tabela_hash.get(chave,[]):
            if a_na_construcao:
                yield par + linha
            else:
                yield linha + par

                
                
