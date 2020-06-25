#Link: https://www.datacamp.com/community/tutorials/fuzzy-string-python

#Funcoes para analise bruta

#Libs para o funcionamento
#Especifica
from fuzzywuzzy import fuzz
import pandas
import nltk
import numpy
import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.svm import LinearSVC
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeClassifier
from PIL import Image
import wget
import time
import timeit

#Geral
import re
import glob
import os
import shutil

#Outros arquivos
import sqlite_funcoes
import funcoes_gerais

#Retorno global 
global retorno_global

#Pegando nome dos modelos com base no id
def capturando_nome_modelos(modelos):
    #Capturando ids para fazer o select dos modelos
    contador_modelos = modelos.split("-")
    modelos_listados = [] 
    for i in contador_modelos:
        if len(i) > 0:
            modelos_listados.append(i)
    nomes_modelos = []
    #Realizando os selects
    for valores in modelos_listados:
        for nome in sqlite_funcoes.selecionar_modelos_analise(valores):
            nome = re.sub('[^a-zA-Z0-9]', '', str(nome))
            nomes_modelos.append(nome)
    #Retorno dos selects
    return nomes_modelos

#Capturando a aprovacao dos modelos
def capturando_aprovacao(modelos):
    #Capturando ids para fazer o select dos modelos
    contador_modelos = modelos.split("-")
    modelos_listados = [] 
    for i in contador_modelos:
        if len(i) > 0:
            modelos_listados.append(i)
    aprovacoes = []
    #Realizando os selects
    for valores in modelos_listados:
        for provas_modelos in sqlite_funcoes.select_aprovacoes(valores):
            provas_modelos = re.sub('[^a-zA-Z0-9]', '', str(provas_modelos))
            aprovacoes.append(provas_modelos)
    #Retorno dos selects
    return aprovacoes

#Decisão sobre precisao do modelos
def calcular_aprovacao(valores_retorno, modelos):

    #Select para buscar estados do modelo
    todos_valores = []
    modelos_ids = modelos.split("-")
    for id in modelos_ids:
        for t in sqlite_funcoes.select_aprovacoes(id):
            todos_valores.append(re.sub('[^a-zA-Z0-9]', '', str(t)))

    #Valores gerais e iniciais
    somador_total_aprovado = 0
    somador_total_desaprovado = 0
    contador_total_aprovado = 0
    contador_total_desaprovado = 0

    #Definir a quantidade de aprovados
    for i in range(0, len(todos_valores)):
        if "Aprovado" == todos_valores[i]:
            somador_total_aprovado = valores_retorno[i] + somador_total_aprovado
            contador_total_aprovado = todos_valores.count("Aprovado")
        elif "Bloqueado" == todos_valores[i]:
            somador_total_desaprovado = valores_retorno[i] + somador_total_desaprovado
            contador_total_desaprovado = todos_valores.count("Bloqueado")
        else:
            pass

    #Valores classificados com aprovacao
    porcentagem_aprovado = 0
    if todos_valores.count("Aprovado") >= 1:
        porcentagem_aprovado = somador_total_aprovado / contador_total_aprovado
        porcentagem_aprovado = round(porcentagem_aprovado, 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado = 0 
    if todos_valores.count("Bloqueado") >= 1:
        porcentagem_desaprovado = somador_total_desaprovado / contador_total_desaprovado
        porcentagem_desaprovado = round(porcentagem_desaprovado, 2)

    #Valores classificados com aprovacao com base em todos
    porcentagem_aprovado_total = round((somador_total_aprovado / len(todos_valores)), 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado_total = round((somador_total_desaprovado / len(todos_valores)), 2)

    #Valores não classificados    
    porcentagem_desclassificado = 100 - (porcentagem_aprovado_total + porcentagem_desaprovado_total)
    porcentagem_desclassificado = round(porcentagem_desclassificado, 2)

    #Decisão de saida:
    classificacao_analise = ""
    if porcentagem_desclassificado <= (porcentagem_aprovado_total + porcentagem_desaprovado_total):
        if porcentagem_aprovado_total > porcentagem_desaprovado_total:
            classificacao_analise = "Aprovado"
        elif porcentagem_aprovado_total < porcentagem_desaprovado_total:
            classificacao_analise = "Desaprovado"
        elif porcentagem_aprovado_total == porcentagem_desaprovado_total:
            classificacao_analise = "Empate"
        else:
            pass
    else:
        classificacao_analise = "Desclassificado"

    #Medias
    medias = [len(todos_valores), contador_total_aprovado, porcentagem_aprovado, contador_total_desaprovado, porcentagem_desaprovado, porcentagem_aprovado_total, porcentagem_desaprovado_total, porcentagem_desclassificado, classificacao_analise]

    #retorno das medias das operacoes
    return medias

#Quebrando o dominio para melhor analise
def quebrando_dominio(entrada):
    valores = entrada.split("/")
    valores = valores[2].split(".")
    return valores

#Removendo valores do array de dominios
#E realmente importante nao remover ele, assim, garante menos relacao indesejada entre comparacoes
def remover_valores_array_dominio(entrada):
    #Alterar isso e ler arquivo com extensoes
    extensoes_desnecesarias = open("extensoes/extensoes_uri.txt", "r")
    tudo = entrada
    for i in extensoes_desnecesarias:
        c = "{}".format(str(i).strip())
        try:
            tudo.remove(c)
        except:
            pass
    return tudo

#Usando logica de fuzzy ratio para determinar a precisao
#Busca de forma retangular X * Y operações
def funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, tabelas, tipo_modelo, precisao_partial):
    precisao_partial = int(precisao_partial)
    #Retorno dos modelos
    retorno_modelos = []
    #Modelos a serem usados
    nomes_modelos = capturando_nome_modelos(modelos)
    #Loop para comparacao dos modelos
    for modelo in nomes_modelos:
        for tabela in tabelas:
            #Puxando as tabelas
            tabela_temporaria = "csv/{}-{}.csv".format(nome_temporario_para_processo, tabela)
            tabela_modelo = "modelos/{}-{}.csv".format(modelo, tabela)
            #Lendo CSV
            tabela_temporaria = pandas.read_csv(tabela_temporaria, sep=';')
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')
            #Arrays de coluna
            coluna_modelo = tabela_modelo[tabela].values
            coluna_temporario = tabela_temporaria[tabela].values
            #Temporarios
            lista_colunas = []
            temporario_colunas = []
            #Limpando repeticoes nas tabelas de modelos e temporarias
            #Ignorando repeticao
            for i in coluna_modelo:
                try:
                    lista_colunas.index(i)
                except ValueError:
                    lista_colunas.append(i) 
            for i in coluna_temporario:
                try:
                    temporario_colunas.index(i)
                except ValueError:
                    temporario_colunas.append(i) 
            #Aplicando fuzzy ratio
            somador = 0.0
            iteracoes = 0

            #Funcao N^Y comparacoes
            for i in lista_colunas:
                for t in temporario_colunas:

                    #Possui seguranca
                    if tipo_modelo == 1:
                        i = str(i)
                        t = str(t)
                        if int(fuzz.ratio(i,t)) == 100:
                            somador = somador + 1

                    #Nao possui seguranca
                    elif tipo_modelo == 2:
                        i = str(i)
                        t = str(t)
                        valor_fuzzy = int(fuzz.partial_ratio(i,t))
                        if  valor_fuzzy >= precisao_partial:
                            somador = somador + (valor_fuzzy / 100)
                            iteracoes = iteracoes + 1
                    
                    #token1
                    elif tipo_modelo == 3:
                        i = str(i)
                        t = str(t)
                        valor_fuzzy = int(fuzz.token_sort_ratio(i,t))
                        if  valor_fuzzy >= precisao_partial:
                            somador = somador + (valor_fuzzy / 100)
                            iteracoes = iteracoes + 1

                    #token2
                    elif tipo_modelo == 4:
                        i = str(i)
                        t = str(t)
                        valor_fuzzy = int(fuzz.token_set_ratio(i,t))
                        if  valor_fuzzy >= precisao_partial:
                            somador = somador + (valor_fuzzy / 100)
                            iteracoes = iteracoes + 1


                    #possui seguranca
                    elif tipo_modelo == 5:
                        
                        tt = remover_valores_array_dominio(quebrando_dominio(t))
                        ii = remover_valores_array_dominio(quebrando_dominio(i))

                        for iii in ii:
                            for ttt in tt:
                                iii = str(iii)
                                ttt = str(ttt)
                                if int(fuzz.ratio(iii,ttt)) == 100:
                                    somador = somador + 1

                    #Não possui seguranca
                    elif tipo_modelo == 6:

                        tt = remover_valores_array_dominio(quebrando_dominio(t))
                        ii = remover_valores_array_dominio(quebrando_dominio(i))

                        for iii in ii:
                            for ttt in tt:
                                iii = str(iii)
                                ttt = str(ttt)
                                valor_fuzzy = int(fuzz.partial_ratio(iii,ttt))
                                if  valor_fuzzy >= precisao_partial:
                                    somador = somador + (valor_fuzzy / 100)
                                    iteracoes = iteracoes + 1

                    #Erros
                    else:
                        pass

            #Adicionaod ao append o valor de comparacao

            #Seguranca na iteracoes
            #Se for 0 da erro de divisao
            if iteracoes == 0:
                iteracoes = 1

            #ratio
            if tipo_modelo == 1:
                saida = round((somador / len(coluna_temporario)) * 100, 2)
                retorno_modelos.append(saida)

            #parcial
            elif tipo_modelo == 2:
                saida = round((somador / iteracoes) * 100, 2)
                retorno_modelos.append(saida)
            
            #Pacial token
            elif tipo_modelo == 3:
                saida = round((somador / iteracoes) * 100, 2)
                retorno_modelos.append(saida)

            #Pacial token
            elif tipo_modelo == 4:
                saida = round((somador / iteracoes) * 100, 2)
                retorno_modelos.append(saida)

            #ratio
            if tipo_modelo == 5:
                saida = round((somador / len(coluna_temporario)) * 100, 2)
                retorno_modelos.append(saida)

            #parcial
            elif tipo_modelo == 6:
                saida = round((somador / iteracoes) * 100, 2)
                retorno_modelos.append(saida)

            #Aqui quer dizer que lascou tudo
            else:
                pass

    #Retorno dos valoers
    return retorno_modelos

#Leitura da imagem 
def ler_imagem(entrada):
    img_tamanho = 10
    return cv2.resize(cv2.imread(entrada), (img_tamanho, img_tamanho))

#Download da imagem
def download_tratamento_imagem(arquivo, pasta, contador, tipo_tratamento_img):
    #Download da imagem e garante e integridade da mesma
    try:
        #Baixa a imagem
        wget.download(arquivo, '{}/{}.jpeg'.format(pasta, contador))

        #Imagem inicial
        img = None

        #Decide se a imagem vai passar por tratamento
        #Passa pelo tratamento de cinza
        if tipo_tratamento_img == 0:
            #Converte para a escala de cinza
            img = Image.open('{}/{}.jpeg'.format(pasta, contador)).convert('L')
            #Salva a imagem
            img.save('{}/{}.jpeg'.format(pasta, contador))
        #Abre a imagem normal
        elif tipo_tratamento_img == 1:
            img = Image.open('{}/{}.jpeg'.format(pasta, contador))
        else:
            pass
        #Garante a integridade
        img.verify()
        #Fecha a imagem final
        img.close()
    except:
        #Confirma se imagem corrompida ainda existe e deleta ela caso possivel
        funcoes_gerais.arquivos_imagem(pasta, contador)
    
    #So para ter um retorno mesmo
    return True

#Teste dos modelos de regressao
#classificacao binaria
def teste_modelos_regressao(modelos, tipo_classificacao): 
    #Concatenando os valores
    X = np.concatenate((modelos), axis=0)
    #Quantidade de imagens para o index do arra y
    y = []
    for i in range(0, len(modelos)):
        y.append(i)
    y = np.array(y)
    Y = y.reshape(-1)
    # Reshape X with length of y
    X = X.reshape(len(y), -1)
    #Inicializando o classificador
    classifier_linear = None
    #Definindo semente padrão para as operacoes
    np.random.seed(20)
    #Iniciando o modelo de regressao
    if tipo_classificacao == 0:
        #Classificacao de vetores de suporte linear.
        classifier_linear = LinearSVC()
    elif tipo_classificacao == 1:
        #Regressao vetorial de suporte linear.
        classifier_linear = LinearSVR()
    #Regrssao nao linear
    elif tipo_classificacao == 2:
        #C-support
        #Classificacao de vetores de suporte não-linear e não tam inteligente
        #vale por causa do uso dos resize em imagens
        classifier_linear = SVC()
    elif tipo_classificacao == 3:
        #Epsilon-support
        #Classificacao de vetores de suporte não-linear e não tam inteligente
        #vale por causa do uso dos resize em imagens
        classifier_linear = SVR()
    #Arvore de decisao
    elif tipo_classificacao == 4:
        #Utilizando arvore de decisao
        classifier_linear = DecisionTreeClassifier()
    #Deu ruim
    else:
        #Aconteceu alguma coisa e a decisao passou
        pass
    #Retorno da regressao
    return classifier_linear.fit(X,Y)

def comparacao_modelo_teste(classifier_linear, imagens_modelos, diretorio_extracao):
    somador = []
    # Predict the category of image
    for i in glob.glob("{}/*".format(diretorio_extracao)):
        #Leia a imagem para teste
        teste = ler_imagem(i)
        #Prediz qual imagem parece mais com o atual teste
        valor = int(classifier_linear.predict(teste.reshape(1,-1)))

        #Converte os arrays em listas
        teste = teste.tolist()
        modelo = imagens_modelos[valor].tolist()

        #Conveter todos as listas com arrays de unica linha
        teste_final = []
        for i in teste:
            for c in i:
                teste_final = teste_final + c

        modelo_final = []
        for i in modelo:
            for c in i:
                modelo_final = modelo_final + c

        #Realiza a comparacao de valores entre o teste e o array de entrada e pega a quantidade de acerto entre os dois
        acertos = 0
        for i in range(0, len(teste_final)):
            if teste_final[i] == modelo_final[i]:
                acertos = acertos + 1

        #Calcula quanto o modelo teste e a predicao sao parecidos e adiciona dentro do array
        somador.append(float("{:.2}".format((acertos / len(modelo_final)) * 100)))

    #Retorna o valor final da precisao entre os modelos e a extracao
    return float("{:.2}".format(sum(somador) / len(somador)))

#Modelo de comparacao de imagens
def comparador_imagens(nome_temporario_para_processo, modelos, tabelas, precisao_partial, tipo_tratamento_img, tipo_classificacao):
    #Precisao parcial
    precisao_partial = int(precisao_partial)
    #Destruir diretorio
    destruir_diretorio_imagens()
    #Criar diretorio
    criar_diretorio_imagens()
    #Retorno dos modelos
    retorno_modelos = []
    #Modelos a serem usados
    nomes_modelos = capturando_nome_modelos(modelos)
    #Aprovacoes dos modelos
    aprovar = capturando_aprovacao(modelos)
    #Modelos juntar desc
    desc_imagens = []
    for c in zip(nomes_modelos, aprovar):
        desc_imagens.append("{}-{}".format(c[0], c[1]))
    #Temporarios
    lista_colunas = []
    temporario_colunas = []
    somador = []
    imagens_modelos = []
    imagens_extracao = []
    #Gatilho pagina
    gatilho = True
    #Loop para comparacao dos modelos
    for modelo in zip(nomes_modelos, desc_imagens):
        for tabela in tabelas:
            #Fazendo download da pagina de extracao somente uma vez
            #Evitando retrabalho e mais gasto de tempo
            if gatilho:
                #Puxando as tabelas
                tabela_temporaria = "csv/{}-{}.csv".format(nome_temporario_para_processo, tabela)
                #Lendo CSV
                tabela_temporaria = pandas.read_csv(tabela_temporaria, sep=';')
                #Arrays de coluna
                coluna_temporario = tabela_temporaria[tabela].values
                #Decisao
                for i in coluna_temporario:
                    try:
                        temporario_colunas.index(i)
                    except ValueError:
                        temporario_colunas.append(i)
                #Temporario
                contador=0
                for i in temporario_colunas:
                    #Download da imagem
                    download_tratamento_imagem(i, "imagens_extraidas", contador, tipo_tratamento_img)
                    contador=contador+1
                #Imagem de comparacao para o teste
                for i in glob.glob('imagens_extraidas/*'):
                    imagens_extracao.append(ler_imagem(i))
                #Alterar gatilho
                gatilho = False

            #Puxando paginas que estao nos modelos
            #Puxando as tabelas
            tabela_modelo = "modelos/{}-{}.csv".format(modelo[0], tabela)
            #Lendo CSV
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')
            #Arrays de coluna
            coluna_modelo = tabela_modelo[tabela].values
            #Limpando repeticoes nas tabelas de modelos e temporarias
            #Ignorando repeticao
            for i in coluna_modelo:
                try:
                    lista_colunas.index(i)
                except ValueError:
                    lista_colunas.append(i) 

            #Limpando a entradas de imagens dos erros de não foi possível fazer o download
            #CSV
            contador=0
            for i in lista_colunas:
                #Identificar imagem
                img_classifice = "{}-{}".format(contador, modelo[1])
                #Download da imagem
                download_tratamento_imagem(i, "imagens_modelos", img_classifice, tipo_tratamento_img)
                contador=contador+1

            #Imagem de comparacao modelos para o teste
            for i in glob.glob('imagens_modelos/*'):
                imagens_modelos.append(ler_imagem(i))

            #Confirmar que existem valores para iniciar a operacao
            if len(imagens_modelos) > 0 and len(imagens_extracao) > 0:
                classificacao_regressao = teste_modelos_regressao(imagens_modelos, tipo_classificacao)
                valor = comparacao_modelo_teste(classificacao_regressao, imagens_modelos, "imagens_extraidas")
                somador.append(valor)
            else:
                somador.append(0)

        #Destruindo as imagems após cada fim de modelo e reconstruindo o diretorio
        #Isso e feito para quando o proximo modelo e caso exista mais de um, nao ler arquivo que nao faz parte do csv dele
        reconstruir_diretorio_modelos()

    #Destruir diretorios imagens
    destruir_diretorio_imagens()
    #retorno
    return somador

#Uso de NLTK para a meio inteligente viastring
def processamento_nltk_frases():
    pass

#Criar diretorios
def criar_diretorio_imagens():
    funcoes_gerais.criar_diretorio("imagens_extraidas")
    funcoes_gerais.criar_diretorio("imagens_modelos")
    return True

#Destruir diretorios pos analise
def destruir_diretorio_imagens():
    funcoes_gerais.eliminar_conteudo_diretorio("imagens_extraidas")
    funcoes_gerais.destruir_diretorio("imagens_extraidas")
    funcoes_gerais.eliminar_conteudo_diretorio("imagens_modelos")
    funcoes_gerais.destruir_diretorio("imagens_modelos")
    return True

#Destruir somente modelos
def reconstruir_diretorio_modelos():
    funcoes_gerais.eliminar_conteudo_diretorio("imagens_modelos")
    funcoes_gerais.destruir_diretorio("imagens_modelos")
    funcoes_gerais.criar_diretorio("imagens_modelos")
    return True

#Uso de funcoes brutais para pegar media geral de varios modelos
def uso_funcoes_brutais(array_brutal, quantidade_operacoes, quantidade_modelos):
        array_retorno = []
        valor_modelo = 0
        #Ler como matriz e somar todos os valores de mesmo tipo, depois aplicar a divisão pelo valor total maximo
        for i in range(0, quantidade_modelos):
            for t in range(0, quantidade_operacoes):
                valor_momento = array_brutal[t][i]
                valor_modelo = valor_modelo + valor_momento
            valor_modelo = valor_modelo / quantidade_operacoes
            #Caso estrapole por causa do uso de float
            if valor_modelo > 100:
                    valor_modelo = 100.00
            array_retorno.append(valor_modelo)

        print("valores do array: {}\nQuantidade operacoes: {}\nQuantidade modelos: {}".format(array_brutal, quantidade_operacoes, quantidade_modelos))
        #Retorno
        return array_retorno

#Funcao para escolher o analisador 
def escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_partial):
    #Hora atual - Inicio operacao
    inicio = timeit.default_timer()
    #Uso de fuzzy para palavras da pagina
    if tipo_analise_modelo == "fuzzy_ratio_palavra":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["palavras"], 1, precisao_partial)
    #Fuzzy parcial para decidir a string
    elif tipo_analise_modelo == "fuzzy_partial_palavra":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["palavras"], 2, precisao_partial)
    #Uso de fuzzy para uma frase da pagina
    if tipo_analise_modelo == "fuzzy_ratio_frase":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 1, precisao_partial)
    #Fuzzy parcial para decidir a frase
    elif tipo_analise_modelo == "fuzzy_partial_frase":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 2, precisao_partial)
    #Fuzzy tokenset para analise de frase
    elif tipo_analise_modelo == "fuzzy_tokenset_partial_frase":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 3, precisao_partial)
    #Fuzzy tokensort para analise de frase
    elif tipo_analise_modelo == "fuzzy_tokensort_partial_frase":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 4, precisao_partial)
    #Uso de fuzzy ratio para bater dominio
    elif tipo_analise_modelo == "dominio_ratio":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["dominios"], 5, precisao_partial)    
    #Uso de fuzzy parcial para dominio
    elif tipo_analise_modelo == "dominio_partial":
        retorno_global = funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["dominios"], 6, precisao_partial)
    #Analise de imagens
    #Classificação de vetores de suporte linear.
    #Restricao linear
    elif tipo_analise_modelo == "ClassLinearRegressionGray":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 0)
    elif tipo_analise_modelo == "ClassLinearRegressionColor":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 0)
    elif tipo_analise_modelo == "VectorLinearRegressionGray":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 1)
    elif tipo_analise_modelo == "VectorLinearRegressionColor":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 1)
    #Sem restricao linear
    elif tipo_analise_modelo == "VectorLinearCGray":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 2)
    elif tipo_analise_modelo == "VectorLinearCColor":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 2)
    elif tipo_analise_modelo == "VectorLinearEpsilonGray":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 3)
    elif tipo_analise_modelo == "VectorLinearEpsilonColor":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 3)
    #Por arvore de descisao
    elif tipo_analise_modelo == "TreeDecisionGray":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 4)
    elif tipo_analise_modelo == "TreeDecisionColor":
        retorno_global = comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 4)
    #Tocando o terror
    #Brutal fuzzy
    elif tipo_analise_modelo == "brutal_Fuzzy_partial":
        #Inicio do array brutal para qualquer um dos metodos ignorantes
        array_brutal = []    
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["palavras"], 1, precisao_partial)) #fuzzy_ratio_palavra
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["palavras"], 2, precisao_partial)) #fuzzy_partial_palavra
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 1, precisao_partial)) #fuzzy_ratio_frase
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 2, precisao_partial)) #fuzzy_partial_frase
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 3, precisao_partial)) #fuzzy_tokenset_partial_frase
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["frases"], 4, precisao_partial)) #fuzzy_tokensort_partial_frase
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["dominios"], 5, precisao_partial)) #dominio_ratio
        array_brutal.append(funcao_decisao_fuzzy_ratio(nome_temporario_para_processo, modelos, ["dominios"], 6, precisao_partial)) #dominio_partial
        #Valores para executar a operacao
        quantidade_operacoes = len(array_brutal)
        quantidade_modelos = len(array_brutal[0])
        #Retorno comum para o calculo final
        retorno_global = uso_funcoes_brutais(array_brutal, quantidade_operacoes, quantidade_modelos)
    #Brutal predicao imagens
    elif tipo_analise_modelo == "brutal_Img":
        array_brutal = []    
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 0)) #ClassLinearRegressionGray
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 0)) #ClassLinearRegressionColor
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 1)) #VectorLinearRegressionGray
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 1)) #VectorLinearRegressionColor
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 2)) #VectorLinearCGray
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 2)) #VectorLinearCColor
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 3)) #VectorLinearEpsilonGray
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 3)) #VectorLinearEpsilonColor
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 0, 4)) #TreeDecisionGray
        array_brutal.append(comparador_imagens(nome_temporario_para_processo, modelos, ["imagens"], precisao_partial, 1, 4)) #TreeDecisionColor
        #Valores para executar a operacao
        quantidade_operacoes = len(array_brutal)
        quantidade_modelos = len(array_brutal[0])
        #Retorno comum para o calculo final
        retorno_global = uso_funcoes_brutais(array_brutal, quantidade_operacoes, quantidade_modelos)
    else:
        pass
    #Hora final - Final da operacao
    fim = timeit.default_timer()

    #Medias dos valores
    medias = calcular_aprovacao(retorno_global, modelos)

    #retorno do processamento
    #Retorno dos valores globais
    #Medias
    #Tempo para realizar a determinada operacao
    return retorno_global, medias, int(fim-inicio)