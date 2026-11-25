import sys
from pathlib import Path

# coloca a raiz do projeto no caminho, para achar o pacote SQLRunner
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from SQLRunner.config import BPlusTree  # noqa: E402

tree = BPlusTree(order=4)

# chaves para exemplo
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
