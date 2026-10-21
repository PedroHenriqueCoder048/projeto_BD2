import re

class Query:

    def __init__(self,query:str):
        self.query = query 

    def tokenization(self):
        self.list_tokens = self.query.split()

        if not re.search(f"{self.list_tokens[0]}","CREATE",re.IGNORECASE):
            raise("O comando declarado possui sintaxe não foi reconhecida pelo sistema")

        if not re.search(f"{self.list_tokens[1]}","TABLE",re.IGNORECASE):
            raise("O comando declarado possui sintaxe não foi reconhecida pelo sistema")
    
        table = self.list_tokens[2]

        list_data = re.findall(r"\(.*\)",self.query)

qr = Query("create table aluno ( id INT , nome CHAR(20) )")

qr.tokenization()