import struct

from storage import le_pagina


RECORD_SIZE = 8


pagina = le_pagina(2)

registro = pagina[0:RECORD_SIZE]

id_aluno, matricula = struct.unpack("ii", registro)

print("Registro recuperado:")
print("ID:", id_aluno)
print("Matrícula:", matricula)