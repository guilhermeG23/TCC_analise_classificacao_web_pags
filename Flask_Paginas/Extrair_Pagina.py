#Bibliotecas necessárias
import requests
from bs4 import BeautifulSoup
import re
import replace

#Captura pagina
def capturar_pagina_url(url):
    page = requests.get(url, timeout=10, verify=False)
    pagina = BeautifulSoup(page.text, 'html.parser')
    return pagina

#Extrair titulo da página
def extrar_titulo(pagina):
    return pagina.title.string

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

#Limpar erro no link
def limpar_link(entrada):
    return replace.replace(entrada, {"..":"", "/\/\/\/":""})

#Extrair todos os links da página
def Extrair_links(pagina, dominio):
    links = []
    for link in pagina.find_all('a'):
        links.append(com_sem_http(link.get('href'), dominio))

    return limpar_link(links)

#Extrair videos
def Extrair_videos(pagina, dominio):
    videos = []
    for link in pagina.find_all('video'):
        videos.append(com_sem_http(link.get('src'), dominio))

    return limpar_link(videos)

#Extrair audios
def Extrair_audios(pagina, dominio):
    audio = []
    for link in pagina.find_all('audio'):
        audio.append(com_sem_http(link.get('src'), dominio))
    
    return limpar_link(audio)

#Adicionado HTTP aos links ou conteudos online
def com_sem_http(entrada, dominio):
    saida = ""
    if str(entrada).rfind("http://") >= 0 or str(entrada).rfind("https://") >= 0:
        #Adiciona o audio com http 
        saida = entrada
    else:
        #Adiciona o dominio no audio para fazer a entrada no append
        saida = "{}{}".format(dominio, entrada)

    return limpar_link(saida)

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
                    imagens.append(com_sem_http(array_img[i], dominio))

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

#Buscador de lista[[Esse][], [][], [][],...]
def buscar_lista(array_entrada):
    saida = []
    for i in range(0, len(array_entrada)):
        saida.append(array_entrada[i][0])
    return saida