#Bibliotecas necessárias
#Especifica
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from googletrans import Translator
import socket

#Funcoes gerais
import funcoes_gerais

#Captura pagina
#Captura os status da página
def capturar_pagina_url(url):
    try:
        return requests.get(url)
    except:
        return False

#Endereco da pagina
def endereco_ip_web(pagina):
    try:
        return socket.gethostbyname(pagina.split("/")[2])
    except:
        return "0.0.0.0"
        
#Hora atual
def hora_atual_operacao():
    return funcoes_gerais.retorno_data_ajustada()

#Uso de selenium e web driver para montar a pagina no host e depois extraila
def uso_chromium(url_pagina):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome("chromium/chromedriver.exe", chrome_options=options)
    driver.set_page_load_timeout(30)
    driver.get(url_pagina)
    driver.implicitly_wait(30)
    html = driver.page_source
    driver.close()
    return html
    
#Trazer o html da página
def capturar_pagina(url_pagina):
    #Uso do chromiun
    try:
        url_pagina = uso_chromium(url_pagina)
    except:
        pass
    #Resultado comum caso o chrome falhe
    return BeautifulSoup(url_pagina.text, 'html.parser')

#Status da pagina
def status_url(pagina):
    return pagina.status_code

#Extrair titulo da página
def extrar_titulo(pagina):
    try:
        return pagina.title.string
    except:
        return "Sem titulo - Pagina não possível um titulo ao extrair"

#Detectar idioma da página pelo titulo
def detectar_idioma(titulo):
    translator = Translator()
    return translator.detect(titulo).lang

#Estrutura da página
def estrutura_pagina(pagina):
    return pagina.prettify()

#Contador de linhas
def qtd_linhas_pagina(pagina):
    pagina = estrutura_pagina(pagina)
    contador = 0
    for i in pagina:
        contador = contador + 1
    return contador

#Filtrar dominio
def obter_dominio(url):
    page = funcoes_gerais.split_geral(url, "/")
    return "{}//{}".format(page[0], page[2])

#Todas as frases listadas
def frases_listadas(tags, pagina):
    frases_inteiras = []
    for tag in tags:
        for i in range(0, funcoes_gerais.ler_caracteres(pagina.find_all(tag))):
            frases_inteiras.append(funcoes_gerais.split_simples(pagina.find_all(tag)[i].get_text()))
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
    return funcoes_gerais.replace_links(entrada)

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
    if funcoes_gerais.re_findall_http(entrada):
        #Adiciona o audio com http 
        saida = entrada
    else:
        #Adiciona o dominio no audio para fazer a entrada no append
        saida = "{}{}".format(dominio, entrada)
    return limpar_link(saida)

#Buscar todas as imagens da pagina
def tags_imagens(pagina, dominio):
    try:
        #Puxando os formatos existentes gravados
        with open("extensoes/formato_imagens.txt", "r") as arquivo_formatos:
            formatos = []
            for i in arquivo_formatos:
                i = funcoes_gerais.limpar_entrada_array(funcoes_gerais.split_simples(i))
                formatos.append(".{}".format(i))
            #Possiveis imagens
            imagens = []    
            #Todas as tags do url
            for img_tag in pagina.find_all('img'):
                #Quebra a tag de imagens em um array
                array_img = funcoes_gerais.re_findall_imagens_extracao(img_tag)
                #Liste esse array e filtre para fazer entrada no append
                for i in range(0, funcoes_gerais.ler_caracteres(array_img)):
                    #Passe por todos os formatos
                    for formato in formatos:
                        #print(array_img[i].rfind(".{}".format(formato)))
                        if array_img[i].rfind(formato) >= 0:
                            imagens.append(com_sem_http(array_img[i], dominio))
            #retorno das imagens
            return imagens
    except:
        pass

#Ordenador do quantificador de palavras
def sortSecond(val): 
    return funcoes_gerais.converte_inteiro(val[1])

#Quantificar a qtd de palavras existentes a partir de um array
def quantificar_palavras(array_palavras):
    ja_listadas_palavras = []
    for i in range(0, funcoes_gerais.ler_caracteres(array_palavras)):
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
    for i in range(0, funcoes_gerais.ler_caracteres(array_entrada)):
        saida.append(array_entrada[i][0])
    return saida