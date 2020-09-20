import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import socket
import os
import sys
import sqlite3
import replace
import time
from PIL import Image
import wget
from datetime import datetime
import shutil

global banco
global modelo_paginas_html
global todos_paginas_registras

banco = "modelo_teste.db"
modelo_paginas_html = "teste_paginas"

todos_paginas_registras = []


def contactar_banco():
    try:
        return sqlite3.connect(banco)
    except:
        contactar_banco()

def criar_banco():
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id_modelo INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Nome varchar(10000) NOT NULL,
            Paginas varchar(10000) NOT NULL
        );
        """)
        conn.commit()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paginas (
            id_pagina INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            URL varchar(10000) NOT NULL
        );
        """)
        conn.commit()
        conn.close()
    except:
        pass    
    return True

def select_banco_sem_parametros(entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute(entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

def banco_com_paramentros(chamada, parametros):
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute(chamada, parametros)
    conn.commit()
    conn.close()
    return saida
        
def selecionar_id_pagina_modelo():
    return select_banco_sem_parametros("""select id_pagina from paginas order by id_pagina desc limit 1;""")

def todas_paginas():
    return select_banco_sem_parametros("""select * from paginas order by id_pagina desc;""")

def todos_modelos():
    return select_banco_sem_parametros("""select * from modelos order by id_modelo desc;""")

def inserir_pagina_banco(url):
    banco_com_paramentros("""insert into paginas (URL) values (?);""", [url])
    return True

def inserir_modelo_banco(nome_modelo, paginas):
    banco_com_paramentros("""insert into modelos (Nome, Paginas) values (?, ?);""", [nome_modelo, paginas])
    return True

def criar_diretorio(diretorio):
    if os.path.exists(diretorio) == False:
        os.mkdir(diretorio)
    return True

def ler_pagina_html(url_pagina):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_experimental_option("excludeSwitches", ['enable-logging'])
        driver = webdriver.Chrome("chromium/chromedriver.exe", chrome_options=options)
        driver.delete_all_cookies()
        driver.set_page_load_timeout(30)
        driver.get(url_pagina)
        driver.implicitly_wait(30)
        html = driver.page_source
        driver.close()
        return html
    except:
        return requests.get(url_pagina, headers={'User-Agent': 'Custom'})

def registrar_pagina_html(html, id_pagina):
    #Registrar página
    criar_diretorio(modelo_paginas_html)
    gravar_pagina = "{}/{}.txt".format(modelo_paginas_html, id_pagina)
    with open(gravar_pagina, "a+", encoding="UTF-8") as arquivo:   
        arquivo.write("{}".format(html))
    arquivo.close()
    return True

def conferir_status(url):
    pagina = requests.get(url)
    return pagina.status_code

def limpar_n(entrada):
    t = str(entrada)
    t = t.replace("\n", "")
    return t

def quebrar_link(url):
    t = str(url)
    t = t.split("/")
    return t

def dormir(tempo):
    time.sleep(tempo)
    return True

def retorno_hora_atual():
    return datetime.now()

def retorno_data_para_pasta():
    x = retorno_hora_atual()
    return "{}{}{}{}{}{}".format(x.year,x.month,x.day,x.hour,x.minute,x.second)

def retorno_arquivos_diretorio(entrada):
    return os.listdir(entrada)

def download_tratamento_imagem(imagem, pasta, contador):
    diretorio_temporario = "img_temporario_temporario_{}".format(retorno_data_para_pasta())
    try:
        criar_diretorio(diretorio_temporario)
        wget.download(imagem, "{}/".format(diretorio_temporario), bar=None)
        for c in retorno_arquivos_diretorio(diretorio_temporario):
            img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('L')
            img.save('{}/{}.jpeg'.format(pasta, contador))
            img.verify()
            img.close()  
    except:
        pass
    shutil.rmtree(diretorio_temporario)


def quebrar_ids(entrada):
    c = entrada.split("-")
    x = []
    for v in c:
        try:
            v = int(v)
        except:
            pass
        if type(v) is int:
            x.append(v)
    return x

        
def selecionar_ultimo_modelo():
    return select_banco_sem_parametros("""select id_modelo, Paginas from modelos order by id_modelo desc limit 1;""")


def select_url_pagina(id_pagina):
    return select_banco_sem_parametros("""select URL from paginas where id_pagina = {};""".format(id_pagina))


def ler_arquivo(arquivo, nome_modelo):
    paginas_modelo = []
    with open(arquivo, encoding="utf-8") as arquivo:
        for c in arquivo:
            c = limpar_n(c)
            if conferir_status(c) == 200:
                try:
                    inserir_pagina_banco(c)
                    todos_paginas_registras.append(c)
                    ultima_pagina = selecionar_id_pagina_modelo()
                    for t in ultima_pagina[0]:
                        html = ler_pagina_html(c)
                        html = BeautifulSoup(html, 'html.parser')
                        registrar_pagina_html(html.prettify(), t)
                        paginas_modelo = "{}-{}".format(t,paginas_modelo)
                except:
                    pass

    arquivo.close()
    inserir_modelo_banco(nome_modelo, paginas_modelo)

    for i in selecionar_ultimo_modelo():
        imagens_modelo = []
        for j in quebrar_ids(i[1]):
            with open("teste_paginas/{}.txt".format(j), "r", encoding="UTF-8") as pagina_atual_modelo:
                html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                html_para_imagens = html_modelo.find_all('img')
                url_modelo = None
                ids_urls = select_url_pagina(j)
                for x in ids_urls:
                    url_modelo = x[0]
                o = quebrar_link(url_modelo)
                pagina = "{}//{}".format(o[0], o[2])
                for k in html_para_imagens:
                    try:
                        if 'http' not in str(k['src']):
                            imagens_modelo.append("{}{}".format(pagina, k['src']))
                        else:
                            imagens_modelo.append(k['src'])
                    except:
                        pass
            pagina_atual_modelo.close()


        diretorio_modelo = "imagem_modelo_{}_{}".format(i[0], nome_modelo)
        if os.path.exists(diretorio_modelo) == False:
            criar_diretorio(diretorio_modelo)
            contador=0
            for i in imagens_modelo:
                download_tratamento_imagem(i, diretorio_modelo, contador)
                dormir(1)
                contador=contador+1

#python -W ignore criar_modelos.py <txt> <nome modelo>
if __name__ == "__main__":
    criar_banco()
    ler_arquivo(sys.argv[1], sys.argv[2])
    print("Criado modelo: {}\nCom: {} de páginas registradas\nSendo estas: {}".format(sys.argv[2], len(todos_paginas_registras), todos_paginas_registras))