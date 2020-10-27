import requests #Lib para request http
from bs4 import BeautifulSoup #Lib para trabalhar com HTML 
from selenium import webdriver #Chamando o webdriver
import socket #Lib para sockets
import sys #Lib para os parametros
import spicy #Lib para funcoes matematicas
from fuzzywuzzy import fuzz #Lib para processos de fuzzy
from fuzzywuzzy import process #Lib para processos de fuzzy
import cv2 #Lib para opencv
import numpy as np #Lib para funcoes matematicas completas
import statistics #Lib para funcoes de estatistica
from PIL import Image #Lib para tratamento de imagens
import wget #Lib para funcoes de wget

#Libs para sckit-learn
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

#Libs de funcoes pessoais
import funcoes_sql
import funcoes_gerais

#Variaveis globais
global modelo_paginas_html

#Atribuindo valores as variaveis globais
modelo_paginas_html = "teste_paginas"
    
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

#Download das imagens do source-code
def download_tratamento_imagem(imagem, pasta, contador):
    #Diretorio 
    diretorio_temporario = "img_temporario_temporario_{}".format(funcoes_gerais.retorno_data_para_pasta())
    #Testa - No momento que falha o try, ele aciona o except
    try:
        #Cria o diretorio - Se existe, deixa quieto
        funcoes_gerais.criar_diretorio(diretorio_temporario)
        #Download de forma oculta
        wget.download(imagem, "{}/".format(diretorio_temporario), bar=None)
        #Iniciando NONE na img para seguranca
        img = None
        for c in funcoes_gerais.retorno_arquivos_diretorio(diretorio_temporario):
            #Pega a imagem do diretorio temporario e converte para escala de cinza
            img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('L')
            #Salva a alteracao
            img.save('{}/{}.jpeg'.format(pasta, contador))
            #Confirma se alterou e ja fecha a imagem
            img.verify()
            img.close()
    except:
        #Caso falhe, faca nada
        pass
    
    #Eliminar todas os arquivos temporarios
    funcoes_gerais.eliminar_conteudo_diretorio(diretorio_temporario)
    funcoes_gerais.destruir_diretorio(diretorio_temporario)

#Confirma se a pagina existe
def conferir_status(url):
    pagina = requests.get(url) #Faz um request para confirmar o url
    return pagina.status_code #Pega o status da pagina

#Treinamento sobre as imagens
def modelos_regressao(modelos, teste_modelos_regressao):
    #Colocando as imagens em uma matriz classificativa
    #Ex: X -> IMG_1, Y -> 0
    X = np.concatenate((modelos), axis=0)
    y = []
    for i in range(0, len(modelos)):
        y.append(i)
    y = np.array(y)
    Y = y.reshape(-1)
    X = X.reshape(len(y), -1)
    classifier_linear = None #Iniciar variavel no nivel superior
    np.random.seed(20) #Define a semente
    #Selecione o metodo de treinamento
    if teste_modelos_regressao == 0:
        classifier_linear = LinearSVC()
    elif teste_modelos_regressao == 1:
        classifier_linear = LinearSVR()
    elif teste_modelos_regressao == 2:
        classifier_linear = DecisionTreeRegressor()
    else:
        pass
    return classifier_linear.fit(X,Y) #Retorno do treinamento

#Alterar o tamanho da imagem no momento de leitura
def ler_imagem(entrada):
    img_tamanho = 10 #Tamanho em px
    return cv2.resize(cv2.imread(entrada), (img_tamanho, img_tamanho)) #Resize da imagem 

#Verificar a predicao da imagem
def retorno_predicao_imagem(imagens_alvo_temporario, imagens_modelos, classifier_linear):
    #Array dos valores obtidos
    somador = []
    #Todas as imagens do alvo
    for i in imagens_alvo_temporario:
        teste = ler_imagem(i) #Ler a imagem
        #Passar a imagem no modelo treinado para trazer a imagem de maior igualdade
        #O retorno é o numero da imagem no array de treino
        valor = int(classifier_linear.predict(teste.reshape(1,-1)))
        try: #Teste de ufncionamento
            teste = teste.tolist() #Converte a imagem atual em list
            modelo = imagens_modelos[valor] #Pega a imagem do modelo 
            modelo = modelo.tolist() #Converte a imagem do modelo em list
            teste_final = funcoes_gerais.converter_unico_array(teste) #Convert em array o temporaria
            modelo_final = funcoes_gerais.converter_unico_array(modelo) #Converr em array o modelo
            #Faz a comparacao dos arrays e traz a igualdade entre os arrays de 0 a 100
            somador.append(funcoes_gerais.retorno_para_somador_modelos(teste_final, modelo_final))
        except: #Caso der tudo erro com a funcao
            somador.append(0) #Em pior caso zere
    #Retorno
    return float("{:.2}".format(sum(somador) / len(somador)))

#Registrar a pagina em txt -> A temporaria
def registrar_pagina_html(html):
    gravar_pagina = "atual.txt"
    with open(gravar_pagina, "a+", encoding="UTF-8") as arquivo:   
        arquivo.write("{}".format(html))
    arquivo.close()
    return True

#Iniciar funcao principal
def iniciar_comparacoes(arquivo):
    #Abrir arquivo de paginas alvo
    with open(arquivo, "r", encoding="utf-8") as urls:
        #Ler linha por linha
        for url in urls:
            url = funcoes_gerais.limpar_n(url) #Limpeza do url
            if conferir_status(str(url)) == 200: #Confirmar se a pagina esta disponivel
                #Teste o funcionamento
                try:

                    #Aqui se refere ao url alvo do momento
                    #-----------------------------------

                    #Parte html -> Extrair todo o texto da pagina
                    html_analise = ler_pagina_html(url) #ler a pagina 
                    #Transformar a pagina em algo trabalhavel
                    html_para_leitura = BeautifulSoup(html_analise, 'html.parser')
                    #Pegar todo o texto da pagina e colocar um separador
                    html_para_leitura_texto1 = html_para_leitura.get_text(separator=' ')
                    html_para_leitura_texto1 = html_para_leitura_texto1.lower() #Passar tudo em casa baixa
                    html_para_leitura_texto1 = html_para_leitura_texto1.split() #Quebrar em um list
                    html_para_leitura_texto = ' '.join(html_para_leitura_texto1) #Juntar a lista

                    #Imagens -> Obter imagens do alvo
                    html_para_imagens = html_para_leitura.find_all('img') #Todas as tag imagens 
                    imagens_html_base = [] #Array das imagens para download
                    o = funcoes_gerais.quebrar_link(url) #Limpar os links
                    pagina = "{}//{}".format(o[0], o[2]) #URL da pagina
                    #Ler todos os links das imagens para download
                    for k in html_para_imagens:
                        if 'http' not in str(k['src']):
                            imagens_html_base.append("{}{}".format(pagina, k['src']))
                        else:
                            imagens_html_base.append(k['src'])
                    #Criar diretorio para o temporario
                    funcoes_gerais.criar_diretorio("imagem_base")
                    contador=0
                    #Processo de download das imagens
                    for c in imagens_html_base:
                        download_tratamento_imagem(c, "imagem_base", contador)
                        funcoes_gerais.dormir(1)
                        contador=contador+1
                    #Colocar as imagens em array para trabalho
                    #Array para se trabalhar com o modelo
                    imagens_base = []
                    for c in funcoes_gerais.retorno_glob("imagem_base"):
                        imagens_base.append(c)

                    ##tfid
                    vectorizer = TfidfVectorizer() #Inicializar o tfidf
                    vectorizer.fit_transform([html_para_leitura_texto]) #Treinar alvo 
                    vector10 = vectorizer.fit_transform([html_para_leitura_texto]) #Buscar termos sobre ele mesmo
                    vector10 = vector10.toarray() #Buscar os array de valores do resultado treinado
                    vector10 = vector10[0].tolist() #Converte esse array em list
                    vector1 = vectorizer.get_feature_names() #Pega todos os termos que o tfidf considerou
                    #Buscar as 10 palavras de mais relevancia do alvo
                    top10_palavras_tfidf_alvo = funcoes_gerais.pegar_top_10_palavras(vector1, vector10)
                    #-----------------------------------

                    #Iniciar comparacao dos modelos sobre 
                    for i in funcoes_sql.todos_modelos(): #Buscar todos os modelos

                        pasta_modelo = "{}_{}".format(i[0], i[1]) #Pasta do modelo
                        #Demonstrativo
                        print("-+"*24)
                        print("Página alvo: {}\nModelo Base: {} com {} páginas".format(url, i[1], len(funcoes_gerais.quebrar_ids(i[2]))))


                        #HTML do modelos
                        #Obtencao da paginas dos moodelos
                        paginas_modelo = []
                        paginas_modelo = np.array(paginas_modelo)
                        for j in funcoes_gerais.quebrar_ids(i[2]):
                            with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                                html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                                html_modelo = html_modelo.get_text(separator=' ')
                                html_modelo = html_modelo.split()
                                html_modelo = ' '.join(html_modelo)
                                html_modelo = np.array(html_modelo)
                                paginas_modelo = np.concatenate((paginas_modelo, html_modelo), axis=None)
                            pagina_atual_modelo.close()
                        
                        #Parte da predição de imagens
                        #-----------------------------------
                        #Aqui e o mesmo esquema de busca das imagens para download do alvo
                        for j in funcoes_gerais.quebrar_ids(i[2]):
                            with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                                html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser')
                                html_para_imagens = html_modelo.find_all('img')
                                imagens_modelo = []
                                url_modelo = None
                                ids_urls = funcoes_sql.select_url_pagina(j)
                                for x in ids_urls:
                                    url_modelo = x[0]
                                o = funcoes_gerais.quebrar_link(url_modelo)
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

                        #Ler as imagens do modelo atual
                        for c in funcoes_gerais.retorno_glob("imagem_modelo_{}".format(pasta_modelo)):
                            imagens_modelos.append(ler_imagem(c))

                        #Apresentar resultados
                        if len(imagens_modelos) != 0 and len(imagens_base) != 0:
                            a = []
                            #Fazer operacoes de classificacao de imagens
                            for x in range(0,3):
                                #Colocar resultados de medias em array
                                a.append(retorno_predicao_imagem(imagens_base, imagens_modelos, modelos_regressao(imagens_modelos, x)))
                            #Apresenta resultado via mediana da junção do array
                            print("Total predição de imagens - Resultado pela mediana: {}%".format(funcoes_gerais.arredondar_valores(statistics.median(a),2)))
                        #Caso nao exista imagens de qualquer parte
                        else:
                            if len(imagens_modelos) == 0 and len(imagens_base) == 0:
                                print("Ambos base e modelo não possuem imagens para realizar a predição")
                            elif len(imagens_modelos) == 0 and len(imagens_base) != 0:
                                print("Não a imagens modelo para realizar a predição")
                            elif len(imagens_modelos) != 0 and len(imagens_base) == 0:
                                print("Não a imagens base para realizar a predição")
                            else:
                                pass
                        #-----------------------------------


                        #TFID
                        #Iniciando arrays
                        paginas_modelo_tfid1 = []
                        paginas_modelo_tfid2 = []
                        top10_palavras_tfidf_modelo = []
                        #Limpar os IDS para trabalho - > Todos os ID do modelo
                        for j in funcoes_gerais.quebrar_ids(i[2]):
                            #ler as pagina do j[ID] atual -> Abrir a pagina em txt
                            with open("teste_paginas/{}.txt".format(j), "r",encoding="UTF-8") as pagina_atual_modelo:
                                html_modelo = BeautifulSoup(pagina_atual_modelo, 'html.parser') #ler o HTML da pagina e deixar trabalhavel
                                html_modelo = html_modelo.get_text(separator=' ') #Pegar todo o texto e quebrar com espaco
                                html_modelo = html_modelo.lower() #Transformar todo o texto em caixa baixa
                                html_modelo = html_modelo.split() #Transformar em list o texto -> Limpeza
                                html_modelo = ' '.join(html_modelo) #Juntar list 
                                vectorizer = TfidfVectorizer() #iniciar a operacao de tfidf
                                vector_pagina = vectorizer.fit_transform([html_modelo]) #Treinar o tfidf com o modelo
                                t = vectorizer.get_feature_names() #Obter os termos
                                o = vector_pagina.toarray() #Obter os valores ja em array
                                o = o[0].tolist() #Converter o array em um list
                                #Pegar o top 10 com base em alinhamento dos arrays
                                top10_palavras_tfidf_modelo.append(funcoes_gerais.pegar_top_10_palavras(t, o))
                                paginas_modelo_tfid1.append(t) #Arrays das palavras - Termos
                                paginas_modelo_tfid2.append(o) #Arrays dos valores - frequencias resultantes
                            pagina_atual_modelo.close() #Fechar a pagina
                        #Transforma todas as listas obtidas em um unico array
                        vector2 = np.concatenate(paginas_modelo_tfid1, axis=None).tolist()
                        #Iniciando comparacoes via fuzzy
                        #Todas as palavras do alvo sobre o modelo
                        medianas_token1 = fuzz.token_set_ratio(vector1, vector2) 
                        medianas_token11 = fuzz.partial_token_set_ratio(vector1, vector2)
                        #Todas as palavras do alvo sobre o modelo 10 sobre x modelos * 10
                        medianas_token21 = fuzz.token_set_ratio(top10_palavras_tfidf_alvo, top10_palavras_tfidf_modelo)
                        medianas_token31 = fuzz.partial_token_set_ratio(top10_palavras_tfidf_alvo, top10_palavras_tfidf_modelo) 
                        
                        #Print dos resultados
                        print("Predição por banco de palavras TFID: - Dicionário Fuzzy total - Token set Ratio: {}%".format(medianas_token1))
                        print("Predição por banco de palavras TFID: - Dicionário Fuzzy total - Partial Token set Ratio: {}%".format(medianas_token11))
                        print("Predição por banco de palavras TFID: - Dicionário Fuzzy limitado top 10 - Token set Ratio: {}%".format(medianas_token21))
                        print("Predição por banco de palavras TFID: - Dicionário Fuzzy limitado top 10 - Partial Token set Ratio: {}%".format(medianas_token31))
                    
                    #Destruir temporario
                    funcoes_gerais.eliminar_conteudo_diretorio("imagem_base")
                    funcoes_gerais.destruir_diretorio("imagem_base")

                except: #Erro ao ler arquivo de alvos
                    sys.exit("Erro ao ler a página alvo")
            else: #Saida caso o alvo nao esteja respondendo
                print(requests.get(str(url)))
                print("Pagina não está repondendo / não encontrada ou empregou meio ante extração simples: {}".format(url))

    #Fechando o arquivo das urls alvo sobre o modelo
    urls.close()

"""
DEMONSTRAÇÃO DE MEIOS DE EXTRAÇÃO/CLASSIFICAÇÃO DE CONTEUDOS DA WEB E SEU POSSÍVEL EMPREGO EM SISTEMAS DE BLOQUEIO DE ACESSO A CONTEÚDO EXTERNO.
"""

#python -W ignore iniciar_analise.py <arquivo>
#python -W ignore iniciar_analise.py C:\Users\guilhermebrechot\Desktop\TCC\TCC_Pratico\links_teste\alvo.txt
if __name__ == "__main__":
    iniciar_comparacoes(sys.argv[1])