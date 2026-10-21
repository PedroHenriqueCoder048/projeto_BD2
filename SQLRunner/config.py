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

    def create_header(self,user_id:int, transiction_id:int, operation:int, timestamp):
        "Função que cria o registro de cabeçalho do arquivo de banco de dados"
        " e registra a operação, as tabelas e os campos afetados"
        struct.pack("iiii",user_id,transiction_id,operation,timestamp)  # Inicializa o cabeçalho com dois inteiros

    def read_header(data):
        return struct.unpack("iiii", data)

    def insert(self):
        print("inserindo dados")

class Cache:

    def __init__(self , database, capacity = 3):
        self.database = database
        self.capacity = capacity
        self.pages = {}

    def fixed(self,page_number):
        if page_number in self.pages:
            print(f"Página {page_number} veio do CACHE")
            return self.pages[page_number]
        page =  self.database.read_page(page_number)

        print(f"Página {page_number} veio do .db")

        if len(self.pages)>= self.capacity:
            self.pages.pop(next(iter(self.pages)))

        self.pages[page_number] = page

        return page
# class Tables(Database):
#     def __init__(self, par_table_name:str):
#         self.TABLE_NAME = Database.+f".{par_table_name}"

from bisect import bisect_left, bisect_right


class BPlusNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []

        # Nós internos usam children.
        self.children = []

        # Folhas usam values para guardar referências.
        self.values = []

        # Encadeamento entre folhas.
        self.next_leaf = None


class BPlusTree:
    def __init__(self, order=4):
        if order < 3:
            raise ValueError("A ordem deve ser pelo menos 3.")

        self.order = order
        self.max_keys = order - 1
        self.root = BPlusNode(leaf=True)

    def search(self, key):
        node = self.root

        # Percorre os nós internos até encontrar uma folha.
        while not node.leaf:
            index = bisect_right(node.keys, key)
            node = node.children[index]

        index = bisect_left(node.keys, key)

        if index < len(node.keys) and node.keys[index] == key:
            return node.values[index]

        return None

    def insert(self, key, page_number, slot):
        reference = (page_number, slot)

        # Chave existente: atualiza a referência.
        existing = self.search(key)
        if existing is not None:
            self._update(self.root, key, reference)
            return

        split = self._insert_recursive(
            self.root, key, reference
        )

        # Se a raiz dividiu, cria uma nova raiz.
        if split is not None:
            separator, right_node = split

            new_root = BPlusNode(leaf=False)
            new_root.keys = [separator]
            new_root.children = [self.root, right_node]

            self.root = new_root

    def _update(self, node, key, reference):
        while not node.leaf:
            node = node.children[
                bisect_right(node.keys, key)
            ]

        index = bisect_left(node.keys, key)
        node.values[index] = reference

    def _insert_recursive(self, node, key, reference):
        if node.leaf:
            index = bisect_left(node.keys, key)
            node.keys.insert(index, key)
            node.values.insert(index, reference)

            if len(node.keys) <= self.max_keys:
                return None

            # Divide a folha em duas.
            middle = (len(node.keys) + 1) // 2

            right = BPlusNode(leaf=True)
            right.keys = node.keys[middle:]
            right.values = node.values[middle:]

            node.keys = node.keys[:middle]
            node.values = node.values[:middle]

            right.next_leaf = node.next_leaf
            node.next_leaf = right

            # A primeira chave da nova folha sobe.
            return right.keys[0], right

        # Encontra o filho adequado.
        index = bisect_right(node.keys, key)

        split = self._insert_recursive(
            node.children[index], key, reference
        )

        if split is None:
            return None

        separator, right_child = split

        node.keys.insert(index, separator)
        node.children.insert(index + 1, right_child)

        if len(node.keys) <= self.max_keys:
            return None

        # Divide o nó interno.
        middle = len(node.keys) // 2
        promoted = node.keys[middle]

        right = BPlusNode(leaf=False)
        right.keys = node.keys[middle + 1:]
        right.children = node.children[middle + 1:]

        node.keys = node.keys[:middle]
        node.children = node.children[:middle + 1]

        return promoted, right

    def range_search(self, start, end):
        results = []
        node = self.root

        while not node.leaf:
            node = node.children[
                bisect_right(node.keys, start)
            ]

        index = bisect_left(node.keys, start)

        while node is not None:
            while index < len(node.keys):
                key = node.keys[index]

                if key > end:
                    return results

                results.append((key, node.values[index]))
                index += 1

            node = node.next_leaf
            index = 0

        return results



# ============================================================
# Teste da árvore B+ (arquivo teste_bplus.py)
# Rode a partir da raiz do projeto: python teste_bplus.py
# ============================================================

from SQLRunner.config import BPlusTree

tree = BPlusTree(order=4)

#chaves para exemplo
for key in [50, 20, 70, 10, 30, 60, 80, 40, 90]:
    page_number = key // 10
    slot = key % 10

    tree.insert(key, page_number, slot)

# Busca exata.
print("Busca 30:", tree.search(30))
print("Busca 99:", tree.search(99))

# Busca por intervalo.
print("Intervalo 25 a 70:")
for key, reference in tree.range_search(25, 70):
    print(key, "->", reference)
