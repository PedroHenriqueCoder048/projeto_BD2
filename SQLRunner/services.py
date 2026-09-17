import struct
from config import Database

database = Database("miniDB");

def cria_registro(id_aluno, matricula):
    return struct.pack("ii", id_aluno, matricula)

page = database.read_page(2)

record = page[0:database.RECORD_SIZE]

id_aluno, matricula = struct.unpack("ii", record)

print("Registro recuperado:")
print("ID:", id_aluno)
print("Matrícula:", matricula)