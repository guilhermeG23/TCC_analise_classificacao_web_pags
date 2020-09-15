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
    print(html)
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
    for _ in pagina:
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
        for i in range(0, funcoes_gerais.ler_quantidade_variavel(pagina.find_all(tag))):
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
    return Aplicar_extracao('a', pagina, dominio)

#Buscar todas as imagens da pagina
def tags_imagens(pagina, dominio):
    return Aplicar_extracao('img', pagina, dominio)

#Extrair videos
def Extrair_videos(pagina, dominio):
    return Aplicar_extracao('video', pagina, dominio)

#Extrair audios
def Extrair_audios(pagina, dominio):
    return Aplicar_extracao('audio', pagina, dominio)

#Forma generica de extrair os valores
def Aplicar_extracao(tag, pagina, dominio):
    extrair = []
    for valores_encontrados in pagina.find_all(tag):
        extrair.append(com_sem_http(valores_encontrados.get('src'), dominio))
    return limpar_link(extrair)

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

#Ordenador do quantificador de palavras
def sortSecond(val):
    return funcoes_gerais.converte_inteiro(val[1])

#Quantificar a qtd de palavras existentes a partir de um array
def quantificar_palavras(array_palavras):
    ja_listadas_palavras = []
    for i in range(0, funcoes_gerais.ler_quantidade_variavel(array_palavras)):
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
    for i in range(0, funcoes_gerais.ler_quantidade_variavel(array_entrada)):
        saida.append(array_entrada[i][0])
    return saida
