import os
import struct
import logging
from config import Database,Cache

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
        offset = self.database.displacement(2, 0)
        position_page = offset % self.database.PAGE_SIZE
        page[position_page:position_page+self.database.RECORD_SIZE] = record
        self.database.write_page(2, page)

    def read_record(self, par_page:int,slot:int):
        '''Função criada para ler o registro criado no nosso arquivo de banco de dados'''
        page = self.database.read_page(par_page)
        position = (self.database.HEADER_SIZE + slot * self.database.RECORD_SIZE) % self.database.PAGE_SIZE
        record = page[position:position + self.database.RECORD_SIZE]
        id , registration = struct.unpack("ii", record)
        print(f"Registro recuperado: ID={id}, Matrícula={registration}")

    def insert_header(self ,page_number:int, num_records:int):

        header = self.create_header(1, 1, 1, 1)

        header_page = bytearray(self.database.PAGE_SIZE)

        header_page[0:self.database.HEADER_SIZE] = header

        self.database.write_page(0, header_page)


    def aloc(self):
        """Função que faz o cálculo e descobre o último valor
        do arquivo e salva na próxima página alocando a memória"""
        number_pages = os.path.getsize(self.database.DB_FILE)// self.database.PAGE_SIZE
        print(number_pages)

    def sync(self):
        self.database.flush()
        os.fsync(self.database.file.fileno())

    def to_sweep(self):
        with open(self.database.DB_FILE, "r+b") as file:
            file.seek(0,2)
            file_size = file.tell()

        total_pages = file_size // self.database.PAGE_SIZE

        cache =Cache(self.database)

        for p in range(total_pages):
            buf = cache.fixed(p)
            print(f"Processando pagina {p}")
            # Aqui você pode processar a página conforme necessár

    def create_logging(user_id:int, transaction_id:int, operation:int, timestamp):
        logging.basicConfig(filename='database.log',level=logging.INFO)
        logging.info(f"User ID: {user_id}, Transaction ID: {transaction_id}, Operation: {operation}, Timestamp: {timestamp}")



services = Services(database)

# services.insert_record(1, 12345)

# services.read_record(2, database.read_page(2))
services.insert_record(1, 20260001)

# database.write_page(0, b"A" * database.PAGE_SIZE)
# database.write_page(1, b"B" * database.PAGE_SIZE)

# p2 = database.read_page(0)
services.to_sweep()


# print(len(p2), p2 == b"A" * database.PAGE_SIZE)
# print(database.read_page(1)[:1])