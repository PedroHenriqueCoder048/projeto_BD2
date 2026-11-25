import struct

from SQLRunner.config import Database

miniDB = Database("miniDB")

RECORD_SIZE = 8

def cria_registro(id_aluno, matricula):
    return struct.pack("ii", id_aluno, matricula)


def le_registro(dados):
    return struct.unpack("ii", dados)


registro = cria_registro(1, 20260001)

page = bytearray(miniDB.PAGE_SIZE)

page[0:RECORD_SIZE] = registro

miniDB.write_page(9, page)

