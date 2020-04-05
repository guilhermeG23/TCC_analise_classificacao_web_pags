import requests
from bs4 import BeautifulSoup

def capturar_pagina_url(url):
    page = requests.get(url, timeout=10, verify=False)
    pagina = BeautifulSoup(page.text, 'html.parser')
    return pagina

def obter_dominio(url):
    page = url.split('/')
    return "{}//{}/".format(page[0], page[2])

def palavras_listadas(tags, pagina):

    frases_inteiras = []
    todas_palavras =[]

    for tag in tags:
        for i in range(1, len(pagina.find_all(tag))):
            frases_inteiras.append(pagina.find_all(tag)[i].get_text().lower().split())

    for linha in frases_inteiras:
        for palavra in linha:
            todas_palavras.append(palavra)

    return todas_palavras

def tags_pagina(pagina):
    tags = []
    #Todas as tags do url
    for tag in pagina.find_all(True):
        tags.append(tag.name)
    return tags

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

    """
    def sortSecond(val): 
        return int(val[1])

    ja_listadas_palavras.sort(key = sortSecond, reverse = True) 
    """
    return ja_listadas_palavras

def buscar_lista(array_entrada):
    saida = []
    for i in range(0, len(array_entrada)):
        saida.append(array_entrada[i][0])
    return saida