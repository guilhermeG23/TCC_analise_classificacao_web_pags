import requests
import wget
from bs4 import BeautifulSoup
import re

#Captura pagina
def capturar_pagina_url(url):
    page = requests.get(url, timeout=10, verify=False)
    pagina = BeautifulSoup(page.text, 'html.parser')
    return pagina

#Contador de linhas
def qtd_linhas_pagina(pagina):
    pagina = pagina.prettify()
    contador = 0
    for i in pagina:
        contador = contador + 1
    return contador

#Filtrar dominio
def obter_dominio(url):
    page = url.split('/')
    return "{}//{}".format(page[0], page[2])

#Todas as frases listadas
def frases_listadas(tags, pagina):
    frases_inteiras = []
    for tag in tags:
        for i in range(1, len(pagina.find_all(tag))):
            frases_inteiras.append(pagina.find_all(tag)[i].get_text().split())
    return frases_inteiras

#Quebrar todo o texto e extrair as palavras
def palavras_listadas(tags, pagina):

    frases_inteiras = frases_listadas(tags, pagina)
    todas_palavras =[]

    for linha in frases_inteiras:
        for palavra in linha:
            todas_palavras.append(palavra)

    return todas_palavras

#Extrair todas as tags da pagina
def tags_pagina(pagina):
    tags = []
    #Todas as tags do url
    for tag in pagina.find_all(True):
        tags.append(tag.name)
    return tags

#Buscar todas as imagens da pagina
def tags_imagens(pagina, dominio):
    formatos = ['.jpeg', '.gif', '.jpg', '.png', '.bmp', '.tiff', '.psd', '.exif', '.raw', '.svg']
    imagens = []    
    #Todas as tags do url
    for img_tag in pagina.find_all('img'):
        #Quebra a tag de imagens em um array
        array_img = re.findall(r'[^"]+', str(img_tag))
        #Liste esse array e filtre para fazer entrada no append
        for i in range(0, len(array_img)):
            #Passe por todos os formatos
            for formato in formatos:
                #Confirma se existe o formato
                if array_img[i].rfind(formato) >= 0:
                    #Ve se a imagem é um link ou não
                    if array_img[i].rfind('http') >= 0:
                        #Adiciona a imagem com http 
                        imagens.append(array_img[i])
                    else:
                        #Adiciona o dominio na imagem para fazer a entrada no append
                        imagens.append("{}{}".format(dominio, array_img[i]))
    return imagens
    #wget.download(entrada)

#Ordenador do quantificador de palavras
def sortSecond(val): 
    return int(val[1])

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
        ja_listadas_palavras.sort(key = sortSecond, reverse = True) 
    return ja_listadas_palavras

#Buscador de lista[[Esse][],...]
def buscar_lista(array_entrada):
    saida = []
    for i in range(0, len(array_entrada)):
        saida.append(array_entrada[i][0])
    return saida