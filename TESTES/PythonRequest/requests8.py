import requests
import sys
from bs4 import BeautifulSoup
import re
from googletrans import Translator

def exibir_dominio(url):
    page = url.split('/')
    print(page)
    print("{}//{}/".format(page[0], page[2]))

def buscar_pagina(url):
    pagina = requests.get(url)
    pagina.encoding = 'utf-8'
    return BeautifulSoup(pagina.text, 'html.parser')

def listar_tags_pagina(pagina):
    tags = ['title', 'p', 'h1', 'h2', 'h3', 'h4', 'a', 'span', 'li', 'footer']
    frases_inteiras = []
    todas_palavras = []

    for tag in tags:
        for i in range(1, len(pagina.find_all(tag))):
            frases_inteiras.append(pagina.find_all(tag)[i].get_text().lower().split())

    for linha in frases_inteiras:
        for palavra in linha:
            todas_palavras.append(palavra)

    return frases_inteiras, todas_palavras

def contador_palavras(todas_palavras, visulizar, qtd_rank):
    ja_listadas_palavras = []
    for i in range(0, len(todas_palavras)):
        atual = todas_palavras[i]
        if len(atual) > 1:
            interno = []
            interno.append(atual)
            interno.append(todas_palavras.count(atual))
            try:
                ja_listadas_palavras.index(interno)
            except ValueError:
                ja_listadas_palavras.append(interno)
        
    def sortSecond(val): 
        return int(val[1])

    ja_listadas_palavras.sort(key = sortSecond, reverse = True) 

    if visulizar:
        if len(ja_listadas_palavras) > 0:
            for i in range(0, qtd_rank):
                print("Rank: {} - Palavra: {} - Qtd: {}".format((i+1), ja_listadas_palavras[i][0], ja_listadas_palavras[i][1]))
        else:
            print("Não foi possivel analisar nenhum conteudo textual da página")

    return ja_listadas_palavras

if __name__ == "__main__":
    #pagina = buscar_pagina(input("URL: "))
    pagina = "https://stackoverflow.com/questions/34599760/python-requests-module-getting-the-domain-name"
    exibir_dominio(pagina)
    """
    qtd_rank = int(input("Qtd de Rank: "))
    frases_inteiras, todas_palavras = listar_tags_pagina(pagina)
    palavras_ja_rankeadas = contador_palavras(todas_palavras, True, qtd_rank)
    """