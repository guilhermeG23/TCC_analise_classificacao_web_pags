import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import socket
import os
import sys
import sqlite3
import spicy
import replace
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import cv2
import numpy as np
import statistics
from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.svm import LinearSVC
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectPercentile
from PIL import Image
import wget
import time
import timeit
import threading
import re
import shutil
import glob
import replace
from datetime import datetime


global banco
global modelo_paginas_html

banco = "modelo_teste.db"
modelo_paginas_html = "teste_paginas"

def contactar_banco():
    try:
        return sqlite3.connect(banco)
    except:
        contactar_banco()

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

def select_url_pagina(id_pagina):
    return select_banco_sem_parametros("""select URL from paginas where id_pagina = {};""".format(id_pagina))

def inserir_pagina_banco(url):
    banco_com_paramentros("""insert into paginas (URL) values (?);""", [url])
    return True

def inserir_modelo_banco(nome_modelo, paginas):
    banco_com_paramentros("""insert into modelos (Nome, Paginas) values (?, ?);""", [nome_modelo, paginas])
    return True


def ler_pagina_html(url_pagina):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_argument("--headless")
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
        return requests.get(url_pagina)


def conferir_status(url):
    pagina = requests.get(url)
    return pagina.status_code

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

def limpar_barra(entrada):
    t = str(entrada)
    t = t.replace("//", "/")
    return t


def quebrar_link(url):
    t = str(url)
    t = t.split("/")
    return t

def limpar_n(entrada):
    t = str(entrada)
    t = t.replace("\n", " ")
    return t

def criar_diretorio(diretorio):
    if os.path.exists(diretorio) == False:
        os.mkdir(diretorio)
    return True

def retorno_hora_atual():
    return datetime.now()

def retorno_data_para_pasta():
    x = retorno_hora_atual()
    return "{}{}{}{}{}{}".format(x.year,x.month,x.day,x.hour,x.minute,x.second)

def retorno_arquivos_diretorio(entrada):
    return os.listdir(entrada)

def dormir(tempo):
    time.sleep(tempo)
    return True

def eliminar_conteudo_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        shutil.rmtree(diretorio)
    return True

def destruir_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        os.rmdir(diretorio)
    return True

def download_tratamento_imagem(imagem, pasta, contador):
    diretorio_temporario = "img_temporario_temporario_{}".format(retorno_data_para_pasta())
    try:
        criar_diretorio(diretorio_temporario)
        wget.download(imagem, "{}/".format(diretorio_temporario), bar=None)
        img = None
        for c in retorno_arquivos_diretorio(diretorio_temporario):
            img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('L')
            img.save('{}/{}.jpeg'.format(pasta, contador))
            img.verify()
            img.close()
    except:
        pass
  
    eliminar_conteudo_diretorio(diretorio_temporario)
    destruir_diretorio(diretorio_temporario)

 
def modelos_regressao(modelos, teste_modelos_regressao):
    X = np.concatenate((modelos), axis=0)
    y = []
    for i in range(0, len(modelos)):
        y.append(i)
    y = np.array(y)
    Y = y.reshape(-1)
    X = X.reshape(len(y), -1)
    classifier_linear = None
    np.random.seed(20)
    if teste_modelos_regressao == 0:
        classifier_linear = LinearSVC()
    elif teste_modelos_regressao == 1:
        classifier_linear = LinearSVR()
    elif teste_modelos_regressao == 2:
        classifier_linear = SVC()
    elif teste_modelos_regressao == 3:
        classifier_linear = SVR()
    elif teste_modelos_regressao == 4:
        classifier_linear = DecisionTreeClassifier()
    elif teste_modelos_regressao == 5:
        classifier_linear = DecisionTreeRegressor()
    else:
        pass
    return classifier_linear.fit(X,Y)

def retorno_predicao_imagem(imagens_base, imagens_modelos, classifier_linear):
    somador = []
    for i in imagens_base:
        teste = ler_imagem(i)
        valor = int(classifier_linear.predict(teste.reshape(1,-1)))
        try:
            teste = teste.tolist()
            modelo = imagens_modelos[valor]
            modelo = modelo.tolist()
            teste_final = converter_unico_array(teste)
            modelo_final = converter_unico_array(modelo)
            somador.append(retorno_para_somador_modelos(teste_final, modelo_final))
        except:
            somador.append(0)
    return float("{:.2}".format(sum(somador) / len(somador)))

def ler_imagem(entrada):
    img_tamanho = 10
    return cv2.resize(cv2.imread(entrada), (img_tamanho, img_tamanho))

def retorno_glob(entrada):
    return glob.glob("{}/*".format(entrada))

def retorno_para_somador_modelos(teste_final, modelo_final):
    igualdade = np.greater_equal(teste_final, modelo_final)
    contador_false = 0
    for c in igualdade:
        if c == False:
            contador_false += 1
    return ((len(igualdade) - contador_false) / len(igualdade)) * 100

def converter_unico_array(entrada):
    saida_final = []
    for i in entrada:
        for c in i:
            saida_final = saida_final + c
    return saida_final

def registrar_pagina_html(html):
    gravar_pagina = "atual.txt"
    with open(gravar_pagina, "a+", encoding="UTF-8") as arquivo:   
        arquivo.write("{}".format(html))
    arquivo.close()
    return True

def remover_arquivo(entrada):
    return os.remove(entrada)

def arredondar_valores(valores, arredondamento):
    return round(valores, arredondamento)

def iniciar_comparacoes(url):

    if conferir_status(url) == 200:

        try:
            #html
            html_analise = ler_pagina_html(url)
            html_para_leitura = BeautifulSoup(html_analise, 'html.parser')
            html_para_leitura_texto1 = html_para_leitura.get_text(separator=' ')
            html_para_leitura_texto1 = html_para_leitura_texto1.split()
            html_para_leitura_texto = ' '.join(html_para_leitura_texto1)

            #Imagens
            html_para_imagens = html_para_leitura.find_all('img')
            imagens_html_base = []
            o = quebrar_link(url)
            pagina = "{}//{}".format(o[0], o[2])
            for k in html_para_imagens:
                if 'http' not in str(k['src']):
                    imagens_html_base.append("{}{}".format(pagina, k['src']))
                else:
                    imagens_html_base.append(k['src'])

            criar_diretorio("imagem_base")
            contador=0
            for c in imagens_html_base:
                download_tratamento_imagem(c, "imagem_base", contador)
                dormir(1)
                contador=contador+1

            ##tfid
            vectorizer = TfidfVectorizer()
            vectorizer.fit_transform([html_para_leitura_texto])
            vector10 = vectorizer.fit_transform([html_para_leitura_texto])
            vector10 = vector10.toarray()
            vector10 = vector10[0].tolist()
            vector1 = vectorizer.get_feature_names()


        except:
            sys.exit("Erro ao ler a página alvo")


        for i in todos_modelos():

            #try:
            pasta_modelo = "{}_{}".format(i[0], i[1])
            print("-+"*24)
            print("Página alvo: {}\nModelo Base: {} com {} páginas".format(url, i[1], len(quebrar_ids(i[2]))))

            #HTML
            paginas_modelo = []
            paginas_modelo = np.array(paginas_modelo)
            for j in quebrar_ids(i[2]):
                with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                    html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                    html_modelo = html_modelo.get_text(separator=' ')
                    html_modelo = html_modelo.split()
                    html_modelo = ' '.join(html_modelo)
                    html_modelo = np.array(html_modelo)
                    paginas_modelo = np.concatenate((paginas_modelo, html_modelo), axis=None)
                pagina_atual_modelo.close()
            
            #Fuzzy - Comprimento de cordas diferentes 
            valor = fuzz.token_set_ratio(html_para_leitura_texto, paginas_modelo)
            print("Precisão Fuzzy: {}%".format(arredondar_valores(float(valor),2)))

            #Predição de imagens
            for j in quebrar_ids(i[2]):
                with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                    html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                    html_para_imagens = html_modelo.find_all('img')
                    imagens_modelo = []
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
            
            imagens_modelos = []
            for c in retorno_glob("imagem_modelo_{}".format(pasta_modelo)):
                imagens_modelos.append(ler_imagem(c))
            imagens_base = []
            for c in retorno_glob("imagem_base"):
                imagens_base.append(c)

            if len(imagens_modelos) != 0 and len(imagens_base) != 0:
                a = []
                for x in range(0,6):
                    a.append(retorno_predicao_imagem(imagens_base, imagens_modelos, modelos_regressao(imagens_modelos, x)))
                print("Total predição de imagens: \n\t* Mediana: {}%\n\t* Média: {}%".format(arredondar_valores(statistics.median(a),2), arredondar_valores((sum(a)/6),2)))
            else:
                if len(imagens_modelos) == 0 and len(imagens_base) == 0:
                    print("Ambos base e modelo não possuem imagens para realizar a predição")
                elif len(imagens_modelos) == 0 and len(imagens_base) != 0:
                    print("Não a imagens modelo para realizar a predição")
                elif len(imagens_modelos) != 0 and len(imagens_base) == 0:
                    print("Não a imagens base para realizar a predição")
                else:
                    pass

            #TFID
            paginas_modelo_tfid1 = []
            paginas_modelo_tfid2 = []
            for j in quebrar_ids(i[2]):
                with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                    html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                    html_modelo = html_modelo.get_text(separator=' ')
                    html_modelo = html_modelo.split()
                    html_modelo = ' '.join(html_modelo)

                    vectorizer = TfidfVectorizer()
                    vector_pagina = vectorizer.fit_transform([html_modelo])

                    t = vectorizer.get_feature_names()
                    o = vector_pagina.toarray()

                    paginas_modelo_tfid1.append(t)
                    paginas_modelo_tfid2.append(o)

                pagina_atual_modelo.close()

            vector2 = np.concatenate(paginas_modelo_tfid1, axis=None).tolist() #Fuzzy
            vector20 = np.concatenate(paginas_modelo_tfid2, axis=None).tolist() #Frequencia

            medianas_token1 = fuzz.token_set_ratio(vector1, vector2)
            medianas_token10 = fuzz.token_set_ratio(vector10, vector20)

            print("Predição por banco de palavras TFID: \n\t* Dicionário Fuzzy: {}%\n\t* Modelo TFID: {}%".format(medianas_token1, medianas_token10))

        print("-+"*24)

        eliminar_conteudo_diretorio("imagem_base")
        destruir_diretorio("imagem_base")

    else:
        print("Pagina não está repondendo ou não encontrada")


#python -W ignore iniciar_analise.py <link>
if __name__ == "__main__":
    iniciar_comparacoes(sys.argv[1])