import struct

from storage import escreve_pagina, le_pagina, PAGE_SIZE


RECORD_SIZE = 8


def cria_registro(id_aluno, matricula):
    return struct.pack("ii", id_aluno, matricula)


def le_registro(dados):
    return struct.unpack("ii", dados)


registro = cria_registro(1, 20260001)

pagina = bytearray(PAGE_SIZE)

pagina[0:RECORD_SIZE] = registro

escreve_pagina(2, pagina)

print("Registro gravado.")
print("Página: 2")
print("Slot: 0")
print("Byte inicial:", 2 * PAGE_SIZE)