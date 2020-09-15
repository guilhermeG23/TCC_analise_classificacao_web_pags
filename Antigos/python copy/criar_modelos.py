import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import socket
import os
import sys
import sqlite3
import replace

global banco
global modelo_paginas_html

banco = "modelo_teste.db"
modelo_paginas_html = "teste_paginas"

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
        options.add_argument("--headless")
        driver = webdriver.Chrome("chromium/chromedriver.exe", chrome_options=options)
        driver.set_page_load_timeout(30)
        driver.get(url_pagina)
        driver.implicitly_wait(30)
        html = driver.page_source
        driver.close()
        return html
    except:
        return requests.get(url_pagina)

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

def ler_arquivo(arquivo, nome_modelo):
    paginas_modelo = []
    with open(arquivo, encoding="utf-8") as arquivo:
        for c in arquivo:
            c = limpar_n(c)
            if conferir_status(c) == 200:
                inserir_pagina_banco(c)
                #print(c)
                ultima_pagina = selecionar_id_pagina_modelo()
                for t in ultima_pagina[0]:
                    html = ler_pagina_html(c)
                    html = BeautifulSoup(html, 'html.parser')
                    registrar_pagina_html(html.prettify(), t)
                    paginas_modelo = "{}-{}".format(t,paginas_modelo)
    arquivo.close()
    inserir_modelo_banco(nome_modelo, paginas_modelo)

    #for o in todas_paginas():
    #    print(o)
    #for o in todos_modelos():
    #    print(o)

#python "versao_lite copy.py" C:\Users\guilhermebrechot\Desktop\TCC\TCC_Pratico\Links_utilizados\animes.txt modelo_teste
if __name__ == "__main__":
    criar_banco()
    ler_arquivo(sys.argv[1], sys.argv[2])