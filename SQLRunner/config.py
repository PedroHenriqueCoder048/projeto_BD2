import os
import struct


class Database:
    '''Classe criada para manipular os arquivos de dados com funções de 
    de leitura e escritas de páginas, e definir o calculo de delocamento de memória
    para inserir os registros de dados'''
    def __init__(self, par_db_file:str):

        self.PAGE_SIZE = 4096
        self.DB_FILE = par_db_file+".db"
        self.RECORD_SIZE = 8
        self.HEADER_SIZE = 16

    def write_page(self ,par_page_number:int, data:struct):
        '''Função que escreve uma página e caso ela não exista ele cria um arquivo que 
        serve para salvas dados no formato de bytes'''
        if len(data) != self.PAGE_SIZE:
            raise ValueError("A página deve ter exatamente 4096 bytes.")

        try:
            par_page_number = int(par_page_number)
        except ValueError as erro:
            raise ValueError(f"O valor do parametro de escrita não é um inteiro\nerror:{erro} ")

        modo = "r+b" if os.path.exists(self.DB_FILE) else "w+b"

        with open(self.DB_FILE, modo) as file_db:
            position = par_page_number * self.PAGE_SIZE
            file_db.seek(position)
            file_db.write(data)
            print("O registro está salvo com sucesso")

    def read_page(self, par_page_number:int):
        '''Função que realiza a leitura de uma página dos arquivos e caso ele não exista
        ele retorna um error'''
        try:
            with open(self.DB_FILE, "rb") as file_db:
                position = par_page_number * self.PAGE_SIZE
                file_db.seek(position)

                data = file_db.read(self.PAGE_SIZE)

                if len(data) != self.PAGE_SIZE:
                    raise ValueError("A página não existe ou está incompleta.")

                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"O arquivo {self.DB_FILE} não foi encontrado.")

    def displacement(self, par_page_number:int, slot:int):
        '''Função que calcula o tamanho das paginas para se deslocar 
        e salvar o registro na próxima página de forma correta sem salvar em cima 
        dos dados anteriores'''
        offset = (par_page_number * self.PAGE_SIZE) + self.HEADER_SIZE + (slot * self.RECORD_SIZE)
        return offset

    def insert(self):
        print("inserindo dados")

# class Tables(Database):
#     def __init__(self, par_table_name:str):
#         self.TABLE_NAME = Database.+f".{par_table_name}"

