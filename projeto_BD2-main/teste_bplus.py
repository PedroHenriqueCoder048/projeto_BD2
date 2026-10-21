# teste da arvore B+

from SQLRunner.config import BPlusTree

tree = BPlusTree(order=4)

#chaves para exemplo
for key in [50, 20, 70, 10, 30, 60, 80, 40, 90]:
    page_number = key // 100
    slot = key % 10

    tree.insert(key, page_number, slot)

# Busca exata.
print("Busca 30:", tree.search(30))
print("Busca 99:", tree.search(99))

# Busca por intervalo.
print("Intervalo 25 a 70:")
for key, reference in tree.range_search(25, 70):
    print(key, "->", reference)
