import os
import struct
from config import Database

database = Database("miniDB");


class Services:
    '''Classe criada para manipular os arquivos de banco de dados,aqui vamos 
    manipular os arquivos e como serão salvo os dados e como irão se comportar e caso
    precisarmos recuperarmos'''
    def __init__(self,database:Database):
        self.database = database

    def create_record(self, id, matricula):
        '''Cria um registro de dados em formato de bytes de no nosso arquivo configurado na classe Database
        e que está como parametro self.database'''
        return struct.pack("ii", id, matricula)

    def insert_record(self,id:int,registration:int):
        '''Aqui insere o o registro que foi configurado em tipo byte para ser salvo no nosso arquivo 
        do banco de dados em uma página especifica'''
        record = self.create_record(id, registration)
        page = bytearray(self.database.PAGE_SIZE)
        page[0:self.database.RECORD_SIZE] = record
        self.database.write_page(2, page)

    def read_record(self, par_page:int,data):
        '''Função criada para ler o registro criado no nosso arquivo de banco de dados'''
        page = self.database.read_page(par_page)
        record = page[0:self.database.RECORD_SIZE]
        id , registration = struct.unpack("ii", record)
        print(f"Registro recuperado: ID={id}, Matrícula={registration}")

    def insert_header(self ,page_number:int, num_records:int):

        self.database.displacement(page_number,0)
        
        record = self.create_record(page_number, num_records)


    def aloc(self):
        """Função que faz o cálculo e descobre o último valor
        do arquivo e salva na próxima página alocando a memória"""
        number_pages = os.path.getsize(self.database.DB_FILE)// self.database.PAGE_SIZE
        print(number_pages)


services = Services(database)

# services.insert_record(1, 12345)

# services.read_record(2, database.read_page(2))

teste = database.displacement(2,0)

print(teste)

# database.write_page(0, b"A" * database.PAGE_SIZE)
# database.write_page(1, b"B" * database.PAGE_SIZE)

# p2 = database.read_page(0)

# print(len(p2), p2 == b"A" * database.PAGE_SIZE)
# print(database.read_page(1)[:1])