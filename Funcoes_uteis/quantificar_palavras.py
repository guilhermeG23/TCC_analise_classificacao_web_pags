#Quantificar a qtd de palavras existentes a partir de um array
def quantificar_palavras(array_palavras):
    ja_listadas_palavras = []
    for i in range(0, len(array_palavras)):
        atual = array_palavras[i]
        interno = []
        interno.append(atual)
        interno.append(array_palavras.count(atual))
        try:
            ja_listadas_palavras.index(interno)
        except ValueError:
            ja_listadas_palavras.append(interno) 

    return ja_listadas_palavras