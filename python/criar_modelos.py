#Lib necessarias
import requests #para fazer request HTTP
from bs4 import BeautifulSoup #trabalhar com source-code
from selenium import webdriver #Chamar o webdriver
import socket #leitura de socket
import os #Lib para trabalhar com o S.O
import sys #Entrada de parametros
from PIL import Image #Trabalhar com imagem
import wget #Import da funcao wget

#Imports pessoais
import funcoes_sql
import funcoes_gerais

#varaiveis globais
global modelo_paginas_html
global todos_paginas_registras

modelo_paginas_html = "teste_paginas"

todos_paginas_registras = []

#Iniciar leitura da URL do momento
def ler_pagina_html(url_pagina):
    #Testa - No momento que falha o try, ele aciona o except
    try:
        #Chamar chromedriver
        #Configurar as options
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ['enable-logging'])
        #Chamando o driver
        driver = webdriver.Chrome("chromium/chromedriver.exe", chrome_options=options)
        #Deleta os antigos cookies se existirem
        driver.delete_all_cookies()
        driver.set_page_load_timeout(30)
        #Abrir a pagina
        driver.get(url_pagina)
        driver.implicitly_wait(30)
        #Pega o source-code (Mais importante)
        html = driver.page_source
        #Fecha o driver
        driver.close()
        #Retorno do source-code
        return html
    except:
        #Caso der errado, chame o request
        saida = requests.get(url_pagina, headers={'User-Agent': 'Custom'})
        #Para ler o source code, passa o text para leitura de string
        return saida.text()

def registrar_pagina_html(html, id_pagina): #Registrar página
    funcoes_gerais.criar_diretorio(modelo_paginas_html) #Criar
    gravar_pagina = "{}/{}.txt".format(modelo_paginas_html, id_pagina)
    with open(gravar_pagina, "a+", encoding="UTF-8") as arquivo:   
        arquivo.write("{}".format(html))
    arquivo.close()
    return True

def conferir_status(url):
    pagina = requests.get(url)
    return pagina.status_code

def download_tratamento_imagem(imagem, pasta, contador):
    diretorio_temporario = "img_temporario_temporario_{}".format(funcoes_gerais.retorno_data_para_pasta())
    try:
        funcoes_gerais.criar_diretorio(diretorio_temporario)
        wget.download(imagem, "{}/".format(diretorio_temporario), bar=None)
        for c in funcoes_gerais.retorno_arquivos_diretorio(diretorio_temporario):
            img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('L')
            img.save('{}/{}.jpeg'.format(pasta, contador))
            img.verify()
            img.close()  
    except:
        pass
    funcoes_gerais.eliminar_conteudo_diretorio(diretorio_temporario)

#Criacao do modelo
def ler_arquivo(arquivo, nome_modelo):
    paginas_modelo = "" #Criar a pagina a ser armazenada
    with open(arquivo, encoding="utf-8") as arquivo: #Abrir o arquivo de links
        for c in arquivo: #Ler as lista do arquivo linha por linhas
            c = funcoes_gerais.limpar_n(c) #Limpeza do link 
            if conferir_status(c) == 200: #Confirma o URL da para ser acessado
                try: #Confirma se tudo esta funcionado
                    funcoes_sql.inserir_pagina_banco(c) #Insira pagina no banco
                    todos_paginas_registras.append(c) #Pega a pagina
                    ultima_pagina = funcoes_sql.selecionar_ultimo_id_pagina_modelo() #Pega o ultimo id do banco para registrar a pagina em txt
                    for t in ultima_pagina[0]:
                        html = ler_pagina_html(c) #Capture o source-code
                        html = BeautifulSoup(html, 'html.parser') #Transforme o extraido em algo trabalhavel
                        registrar_pagina_html(html.prettify(), t) #Grava pagina em um arquivo
                        paginas_modelo = "{}-{}".format(t,paginas_modelo) #Incremento para finalizar o modelo
                except: #Faca nada caso o try der errado
                    pass
    arquivo.close() #Fechar arquivo
    funcoes_sql.inserir_modelo_banco(nome_modelo, paginas_modelo) #Insert novo modelo ao banco

    #Buscando imagens que pertencem ao modelo
    #Pegar os IDS do ultimo modelo
    for i in funcoes_sql.selecionar_ultimo_modelo():
        imagens_modelo = [] #Arrya das imagens
        for j in funcoes_gerais.quebrar_ids(i[1]): #Quebrar os ids
            with open("teste_paginas/{}.txt".format(j), "r", encoding="UTF-8") as pagina_atual_modelo: #Ler as paginas dos ids
                html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser') #Transformar a pagina em algo trabalhavel
                html_para_imagens = html_modelo.find_all('img') #Buscar todas as tags imagens
                url_modelo = None #Inciando a variavel num nivel acima
                ids_urls = funcoes_sql.select_url_pagina(j) #Pegar o URK da pagina para realizar o tratamento de download
                for x in ids_urls: #Limpeza do select
                    url_modelo = x[0]
                o = funcoes_gerais.quebrar_link(url_modelo) #Limpeza
                pagina = "{}//{}".format(o[0], o[2]) #Link da pagina
                for k in html_para_imagens: #Passar pelo loop para confirmar se a pagina tem um endereco legivel para extracao
                    try: #Confirma o funcionamento da operacao
                        if 'http' not in str(k['src']): #Se tem HTTP no endereco da imagem -> blz , se nao adicione
                            imagens_modelo.append("{}{}".format(pagina, k['src']))
                        else:
                            imagens_modelo.append(k['src'])
                    except:
                        pass
            #Fechar a pagina pos leitura
            pagina_atual_modelo.close()

        #Download das imagens achadas
        #Diretorio para o download das imagens do modelo
        diretorio_modelo = "imagem_modelo_{}_{}".format(i[0], nome_modelo)
        if os.path.exists(diretorio_modelo) == False: #Confirma se o diretorio existe
            funcoes_gerais.criar_diretorio(diretorio_modelo) #Cria o diretorio se ele nao existir
            contador=0
            for i in imagens_modelo: #Inicia o loop de download das imagens com base no extraido acima
                download_tratamento_imagem(i, diretorio_modelo, contador)
                funcoes_gerais.dormir(1)
                contador=contador+1

"""
DEMONSTRAÇÃO DE MEIOS DE EXTRAÇÃO/CLASSIFICAÇÃO DE CONTEUDOS DA WEB E SEU POSSÍVEL EMPREGO EM SISTEMAS DE BLOQUEIO DE ACESSO A CONTEÚDO EXTERNO.
"""

#python -W ignore criar_modelos.py <txt> <nome modelo>
#python -W ignore criar_modelos.py C:\Users\guilhermebrechot\Desktop\TCC\TCC_Pratico\links_teste\modelo.txt modeloteste
if __name__ == "__main__":
    funcoes_sql.criar_banco()
    ler_arquivo(sys.argv[1], sys.argv[2])
    print("Criado modelo: {}\nCom: {} de páginas registradas\nSendo estas: {}".format(sys.argv[2], len(todos_paginas_registras), todos_paginas_registras))