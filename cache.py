class Cache:
    def __init__(self):
        self.paginas = {}

    def buscar(self, numero_pagina):
        return self.paginas.get(numero_pagina)

    def armazenar(self, numero_pagina, dados):
        self.paginas[numero_pagina] = dados

    def remover(self, numero_pagina):
        self.paginas.pop(numero_pagina, None)

    def limpar(self):
        self.paginas.clear()

    def esta_no_cache(self, numero_pagina):
        return numero_pagina in self.paginas