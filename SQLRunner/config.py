import os
import struct

class Database:

    def __init__(self, par_db_file:str):

        self.PAGE_SIZE = 4096
        self.DB_FILE = par_db_file+".db"
        self.RECORD_SIZE = 8

    def write_page(self ,n:int, dados):
        if len(dados) != self.PAGE_SIZE:
            raise ValueError("A página deve ter exatamente 4096 bytes.")

        try:
            n = int(n)
        except ValueError as erro:
            raise ValueError(f"O valor do parametro de escrita não é um inteiro\nerror:{erro} ")

        modo = "r+b" if os.path.exists(self.DB_FILE) else "w+b"

        with open(self.DB_FILE, modo) as file_db:
            position = n * self.PAGE_SIZE
            file_db.seek(position)
            file_db.write(dados)

    def read_page(self, n:int):
        try:
            with open(self.DB_FILE, "rb") as file_db:
                position = n * self.PAGE_SIZE
                file_db.seek(position)

                dados = file_db.read(self.PAGE_SIZE)

                if len(dados) != self.PAGE_SIZE:
                    raise ValueError("A página não existe ou está incompleta.")

                return dados
        except FileNotFoundError:
            raise FileNotFoundError(f"O arquivo {self.DB_FILE} não foi encontrado.")

    def displacement(self, n:int, slot):
        pass


    def insert(self):
        print("inserindo dados")

# class Tables(Database):
#     def __init__(self, par_table_name:str):
#         self.TABLE_NAME = Database.+f".{par_table_name}"