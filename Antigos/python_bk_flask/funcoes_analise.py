#Funcoes para analise bruta

#Libs para o funcionamento

#Especifica
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas
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
from PIL import Image
import wget
import time
import timeit
import threading

#compartilhada
import funcoes_gerais

"""
Variaveis
"""

#Retorno global 
global retorno_global
global imagens_modelos_diretorio
global imagens_extraidas_diretorio

#varaiveis gerais
imagens_extraidas_diretorio = "imagens_extraidas"
imagens_modelos_diretorio = "imagens_modelos"


"""
Criando diretorios
"""

#criar somente modelos
def criar_diretorio_extraidas():
    funcoes_gerais.criar_diretorio(imagens_extraidas_diretorio)
    return True

#Criar somente modelos
def criar_diretorio_modelos():
    funcoes_gerais.criar_diretorio(imagens_modelos_diretorio)
    return True

#Eliminar conteudo do diretorio
def eliminar_conteudo_diretorio_modelos():
    funcoes_gerais.eliminar_conteudo_diretorio(imagens_modelos_diretorio)
    return True

def eliminar_conteudo_diretorio_extraidos():
    funcoes_gerais.eliminar_conteudo_diretorio(imagens_extraidas_diretorio)
    return True

#Criar diretorios
def criar_diretorio_imagens():
    criar_diretorio_extraidas()
    criar_diretorio_modelos()
    return True


"""
Operacoes de extracao
"""

#Capturando ids para fazer o select dos modelos
def capturando_com_base_modelos(modelos):
    contador_modelos = funcoes_gerais.split_geral(modelos, "-")
    modelos_listados = [] 
    for i in contador_modelos:
        if funcoes_gerais.ler_quantidade_variavel(i) > 0:
            modelos_listados.append(i)
    return modelos_listados

#Pegando nome dos modelos com base no id
def capturando_nome_modelos(modelos):
    #Variavel
    nomes_modelos = []
    #Realizando os selects
    for valores in capturando_com_base_modelos(modelos):
        for nome in funcoes_sql.selecionar_modelos_analise(valores):
            nome = funcoes_gerais.limpeza_string_simples(nome)
            nomes_modelos.append(nome)
    #Retorno dos selects
    return nomes_modelos

#Capturando a aprovacao dos modelos
def capturando_aprovacao(modelos):
    #Variavel
    aprovacoes = []
    #Realizando os selects
    for valores in capturando_com_base_modelos(modelos):
        for provas_modelos in funcoes_sql.select_aprovacoes(valores):
            provas_modelos = funcoes_gerais.limpeza_string_simples(provas_modelos)
            aprovacoes.append(provas_modelos)
    #Retorno dos selects
    return aprovacoes

#Quebrando o dominio para melhor analise
def quebrando_dominio(entrada):
    valores = funcoes_gerais.split_geral(entrada, "/")
    valores = funcoes_gerais.split_geral(valores[2], ".") 
    return valores

#Todas as extensoes de dominios que achei
def dominios_url():
    extensoes_desnecesarias = open("extensoes/extensoes_uri.txt", "r", encoding="UTF-8")
    t = extensoes_desnecesarias.readlines()
    c = []
    for x in t:
        c.append(funcoes_gerais.limpar_quebra_linha(x))
    extensoes_desnecesarias.close()
    return c

#Removendo valores do array de dominios
#E realmente importante nao remover ele, assim, garante menos relacao indesejada entre comparacoes
def remover_valores_array_dominio(entrada):
    #Alterar isso e ler arquivo com extensoes
    extensoes_desnecesarias = dominios_url()
    tudo = entrada
    for i in extensoes_desnecesarias:
        try:
            tudo.remove(i)
        except:
            pass
    return tudo

#Extrair valores do CSV
def retirando_valores_csv(nome_temporario_para_processo, modelo, tabela, dominios):
    #Puxando as tabelas
    tabela_temporaria_extraida = "csv/{}-{}.csv".format(nome_temporario_para_processo, tabela)
    tabela_modelo = "modelos/{}-{}.csv".format(modelo, tabela)
    #Lendo CSV
    tabela_temporaria_extraida = pandas.read_csv(tabela_temporaria_extraida, sep=';')
    tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')

    #print("{}-{}-{}-{}".format(nome_temporario_para_processo, modelo, tabela, dominios))

    #Arrays de coluna
    coluna_temporario_extraida = tabela_temporaria_extraida[tabela].values
    coluna_modelo = tabela_modelo[tabela].values
    #Limpando repeticoes nas tabelas de modelos e temporarias
    #Ignorando repeticao

    temporario_colunas = funcoes_gerais.limpar_repetidos_array(coluna_temporario_extraida)
    modelo_colunas = funcoes_gerais.limpar_repetidos_array(coluna_modelo)
    
    if dominios:
        #remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(modelo_colunas)))
        #remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(temporario_colunas)))
        
        modelo_colunas = remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(modelo_colunas)))
        temporario_colunas = remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(temporario_colunas)))    
        
    return modelo_colunas, temporario_colunas

"""
Capturando modelos
"""

#Decisão sobre precisao do modelos
def calcular_aprovacao(valores_retorno, modelos):

    #Select para buscar estados do modelo
    todos_valores = []
    modelos_ids = funcoes_gerais.split_geral(modelos, "-")
    for i in modelos_ids:
        for t in funcoes_sql.select_aprovacoes(i):
            todos_valores.append(funcoes_gerais.limpeza_string_simples(t))

    #Valores gerais e iniciais
    somador_total_aprovado = []
    somador_total_desaprovado = []
    contador_total_aprovado = todos_valores.count("Aprovado")
    contador_total_desaprovado = todos_valores.count("Bloqueado")

    #Definir a quantidade de aprovados
    for i in range(0, funcoes_gerais.ler_quantidade_variavel(todos_valores)):
        if "Aprovado" == todos_valores[i]:
            somador_total_aprovado.append(valores_retorno[i])
        elif "Bloqueado" == todos_valores[i]:
            somador_total_desaprovado.append(valores_retorno[i])
        else:
            pass

    #Valores classificados com aprovacao
    porcentagem_aprovado = 0
    if contador_total_aprovado >= 1:
        porcentagem_aprovado = statistics.median(somador_total_aprovado)
        porcentagem_aprovado = funcoes_gerais.arredondar_valores(porcentagem_aprovado, 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado = 0 
    if contador_total_desaprovado >= 1:
        porcentagem_desaprovado = statistics.median(somador_total_desaprovado)
        porcentagem_desaprovado = funcoes_gerais.arredondar_valores(porcentagem_desaprovado, 2)

    #Valores classificados com aprovacao com base em todos
    porcentagem_aprovado_total = funcoes_gerais.arredondar_valores((len(todos_valores) * porcentagem_aprovado) / len(todos_valores), 2)
    #funcoes_gerais.arredondar_valores(((len(contador_total_aprovado) * porcentagem_aprovado) / len(todos_valores)), 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado_total = funcoes_gerais.arredondar_valores((len(todos_valores) * porcentagem_desaprovado) / len(todos_valores),2)
    #funcoes_gerais.arredondar_valores(((len(contador_total_desaprovado) * porcentagem_desaprovado) / len(todos_valores)), 2)

    #Valores não classificados
    #Os teoricos 100 de imprecisao dos modelos contra o alvo
    porcentagem_desclassificado = funcoes_gerais.arredondar_valores((100 - ((porcentagem_aprovado_total + porcentagem_desaprovado_total) / len(todos_valores))),2)

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
    medias = [funcoes_gerais.ler_quantidade_variavel(todos_valores), contador_total_aprovado, porcentagem_aprovado, contador_total_desaprovado, porcentagem_desaprovado, porcentagem_aprovado_total, porcentagem_desaprovado_total, porcentagem_desclassificado, classificacao_analise]

    #retorno das medias das operacoes
    return medias


#Usando logica de fuzzy ratio para determinar a precisao
#Busca de forma retangular X * Y operações
def funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, tabelas, tipo_modelo, dominios):
    #Retorno dos modelos
    retorno_modelos = []
    #Modelos a serem usados
    nomes_modelos = capturando_nome_modelos(modelos)
    #Loop para comparacao dos modelos
    for modelo in nomes_modelos:
        for tabela in tabelas:
            #Capturando os valores
            modelo_colunas, temporario_colunas = retirando_valores_csv(nome_temporario_para_processo, modelo, tabela, dominios)
            #Decisoes
            if tipo_modelo == "ratio":
                valor = fuzz.ratio(modelo_colunas, temporario_colunas)
            elif tipo_modelo == "parcial":
                valor = fuzz.partial_ratio(modelo_colunas, temporario_colunas)
            elif tipo_modelo == "token_set":
                valor = fuzz.token_set_ratio(modelo_colunas, temporario_colunas)
            elif tipo_modelo == "token_sort":
                valor = fuzz.token_sort_ratio(modelo_colunas, temporario_colunas)
            retorno_modelos.append(valor)
    #Retorno dos valoers
    return retorno_modelos


"""
Procedimento sobre imagens
"""

#Leitura e reforma da imagem
def ler_imagem(entrada):
    img_tamanho = 10
    return cv2.resize(cv2.imread(entrada), (img_tamanho, img_tamanho))

#Download da imagem
#def download_tratamento_imagem(arquivo, pasta, contador, tipo_tratamento_img=1):
#Deixa viciado para os testes
def download_tratamento_imagem(arquivo, pasta, contador, tipo_tratamento_img):
    #Diretorio temporario
    diretorio_temporario = "img_temporario_{}".format(funcoes_gerais.retorno_data_para_pasta())
    funcoes_gerais.criar_diretorio(diretorio_temporario)
    #Decisao
    try:
        #Download
        wget.download(arquivo, "{}/".format(diretorio_temporario))
        #Inicializador da variavel
        img = None
        #Listagem
        for c in funcoes_gerais.retorno_arquivos_diretorio(diretorio_temporario):
            #Decide se a imagem vai passar por tratamento
            #Escala de cinza
            if tipo_tratamento_img == "1":
                img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('L')
            #Colorida
            elif tipo_tratamento_img == "0":
                img = Image.open("{}/{}".format(diretorio_temporario, c)).convert('RGB')
            #Chabu
            else:
                pass
            #salvar
            img.save('{}/{}.jpeg'.format(pasta, contador))
            #Garante a integridade
            img.verify()
            #Fecha a imagem final
            img.close()
    except:
        #Confirma se imagem corrompida ainda existe e deleta ela caso possivel
        funcoes_gerais.arquivos_imagem(pasta, contador)
    
    #Diretorio temporario
    funcoes_gerais.eliminar_conteudo_diretorio(diretorio_temporario)
    funcoes_gerais.destruir_diretorio(diretorio_temporario)

    #So para ter um retorno mesmo
    return True

#Modelo de comparacao de imagens
def processamento_extraidos_modelos(nome_temporario_para_processo, modelos, tabelas, metodo_analise, precisao_semente, cinza):
    #Final
    somador = []
    #Temporarios
    tabela = funcoes_gerais.limpeza_dominios(tabelas)
    #Download imagem
    realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, imagens_extraidas_diretorio)
    #Modelos a serem usados
    nomes_modelos = capturando_nome_modelos(modelos)
    #Loop para comparacao dos modelos
    for modelo in nomes_modelos:
        realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, imagens_modelos_diretorio)
        somador.append(retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), metodo_analise, precisao_semente))
        eliminar_conteudo_diretorio_modelos()
        criar_diretorio_modelos()
    eliminar_conteudo_diretorio_extraidos()
    return somador

#Teste dos modelos de regressao
#classificacao binaria
def modelos_regressao(modelos, teste_modelos_regressao, precisao_semente): 
    #Concatenando os valores
    X = np.concatenate((modelos), axis=0)
    #Quantidade de imagens para o index do arra y
    y = []
    for i in range(0, funcoes_gerais.ler_quantidade_variavel(modelos)):
        y.append(i)
    y = np.array(y)
    Y = y.reshape(-1)
    # Reshape X with length of y
    X = X.reshape(funcoes_gerais.ler_quantidade_variavel(y), -1)
    #Inicializando o classificador
    classifier_linear = None
    #Definindo semente padrão para as operacoes
    #if funcoes_gerais.converte_inteiro(precisao_semente) == 0:
    #    np.random.seed()
    #else:
    np.random.seed(20)
    #Iniciando o modelo de regressao
    if teste_modelos_regressao == 0:
        #Classificacao de vetores de suporte linear.
        classifier_linear = LinearSVC()
    elif teste_modelos_regressao == 1:
        #Regressao vetorial de suporte linear.
        classifier_linear = LinearSVR()
    #Regrssao nao linear
    elif teste_modelos_regressao == 2:
        #C-support
        #Classificacao de vetores de suporte não-linear e não tam inteligente
        #vale por causa do uso dos resize em imagens
        classifier_linear = SVC()
    elif teste_modelos_regressao == 3:
        #Epsilon-support
        #Regressão de vetores de suporte não-linear e não tam inteligente
        #vale por causa do uso dos resize em imagens
        classifier_linear = SVR()
    #Arvore de decisao por classificacao de valores
    elif teste_modelos_regressao == 4:
        #Utilizando arvore de decisao
        classifier_linear = DecisionTreeClassifier()
    #Arvore de decisao por regressao de valores
    elif teste_modelos_regressao == 5:
        #Utilizando arvore de decisao
        classifier_linear = DecisionTreeRegressor()
    #Deu ruim
    else:
        #Aconteceu alguma coisa e a decisao passou
        pass
    #Retorno da regressao
    return classifier_linear.fit(X,Y)

#Comparar os modelos 
def comparacao_modelo_teste(classifier_linear, imagens_modelos, diretorio_extracao):
    #Array
    somador = []
    # Predict the category of image
    for i in funcoes_gerais.retorno_glob(diretorio_extracao):
        #Leia a imagem para teste
        teste = ler_imagem(i)
        #Prediz qual imagem parece mais com o atual teste
        valor = funcoes_gerais.converte_inteiro(classifier_linear.predict(teste.reshape(1,-1)))
        #Caso escape do range da lista = Não tem valor compativel na lista
        try:
            #Converte os arrays em listas
            teste = teste.tolist()
            modelo = imagens_modelos[valor]
            modelo = modelo.tolist()
            #Conveter todos as listas com arrays de unica linha
            teste_final = converter_unico_array(teste)
            modelo_final = converter_unico_array(modelo)
            #Realiza a comparacao de valores entre o teste e o array de entrada e pega a quantidade de acerto entre os dois
            somador.append(retorno_para_somador_modelos(teste_final, modelo_final))
        except:
            somador.append(0)
    #Retorna o valor final da precisao entre os modelos e a extracao
    return float("{:.2}".format(funcoes_gerais.soma_array(somador) / funcoes_gerais.ler_quantidade_variavel(somador)))

#converter a unico array
def converter_unico_array(entrada):
    saida_final = []
    for i in entrada:
        for c in i:
            saida_final = saida_final + c
    return saida_final

#Retorno da comparacao de matrizes
def retorno_para_somador_modelos(teste_final, modelo_final):
    igualdade = np.greater_equal(teste_final, modelo_final)
    contador_false = 0
    for c in igualdade:
        if c == False:
            contador_false += 1
    #Quanto em porcentagem da imagem é verdadeira durante a comparacao
    return ((funcoes_gerais.ler_quantidade_variavel(igualdade) - contador_false) / funcoes_gerais.ler_quantidade_variavel(igualdade)) * 100

def realizando_operacao_extracao_imagens_download(diretorio_csv, nome_da_tabela, tipo_tabela, cinza, diretorio_extraidas):
    #Puxando as tabelas
    tabela_temporaria = "{}/{}-{}.csv".format(diretorio_csv, nome_da_tabela, tipo_tabela)
    #Lendo CSV
    tabela_temporaria = pandas.read_csv(tabela_temporaria, sep=';')
    #Arrays de coluna
    coluna_temporario = tabela_temporaria[tipo_tabela].values
    #Decisao se ja existe o arquivo repetido
    #temporario_colunas = funcoes_gerais.limpar_repetidos_array(coluna_temporario)
    temporario_colunas = []
    for i in coluna_temporario:
        try:
            temporario_colunas.index(i)
        except ValueError:
            temporario_colunas.append(i)
    
    #Temporario
    contador=0
    for i in temporario_colunas:
        #Download da imagem
        #download_tratamento_imagem(i, diretorio_extraidas, contador, cinza)
        threading.Thread(target=download_tratamento_imagem,args=(i, diretorio_extraidas, contador, cinza)).start()
        funcoes_gerais.dormir(1)
        contador=contador+1
    #So um returne por graca
    return True

#Lendo diretorios
def lendo_imagens_diretorios(diretorio_extraidas):
    imagens_extracao = []
    #Imagem de comparacao para o teste
    for i in funcoes_gerais.retorno_glob(diretorio_extraidas):
        imagens_extracao.append(ler_imagem(i))
    #Retorno
    return imagens_extracao

#Retorno da operacao de somador
def retorno_somador(imagens_modelos, imagens_extracao, metodo_analise, precisao_semente):
    somador = None
    #Confirmar que existem valores para iniciar a operacao
    if funcoes_gerais.ler_quantidade_variavel(imagens_modelos) > 0 and funcoes_gerais.ler_quantidade_variavel(imagens_extracao) > 0:
        classificacao_regressao = modelos_regressao(imagens_modelos, metodo_analise, precisao_semente)
        valor = comparacao_modelo_teste(classificacao_regressao, imagens_modelos, imagens_extraidas_diretorio)
        somador = valor
    else:
        somador = 0
    return somador


#Uso de funcoes brutais para pegar media geral de varios modelos
def arredondamento_para_modelo_multi_operacoes(entrada_zip, quantidade_operacoes):    
    retorno = []
    for i in entrada_zip:
        retorno.append(funcoes_gerais.arredondar_valores(funcoes_gerais.soma_array(i) / quantidade_operacoes, 2))
    return retorno

#Arrumar tempo da saida
def arrumar_tempo(tempo):
    if tempo > 60:
        tempo = tempo / 60
        tempo = "{:.4} - Minuto/s".format(funcoes_gerais.converte_string(tempo))
    else:
        tempo = "{:.4} - Segundo/s".format(funcoes_gerais.converte_string(tempo))
    return tempo 
    
#Funcao para escolher o analisador 
def escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_semente, cinza):

    #Hora atual - Inicio operacao
    inicio = timeit.default_timer()

    #Criar diretorio de imagens por garantia
    criar_diretorio_imagens()

    #Uso total dos fuzzys em mais de uma operacao por vez 
    if tipo_analise_modelo == "uso_total_fuzzy":
        b = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "parcial", False)
        c = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_set", False)
        f = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "parcial", True)
        #Media 1
        primeira_saida = arredondamento_para_modelo_multi_operacoes(zip(b, c, f), 3)
        
        #Temporarios
        coluna_temporario_extraida = None
        coluna_modelo = None
        somador_teste = []
    
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
    
        #Pagina alvo
        tabela_temporaria_extraida = "csv/{}-paginas.csv".format(nome_temporario_para_processo)
        tabela_temporaria_extraida = pandas.read_csv(tabela_temporaria_extraida, sep=';')
        coluna_temporario_extraida = tabela_temporaria_extraida["ids"].values
        coluna_temporario_extraida = coluna_temporario_extraida.tolist()
        todas_paginas_temporario = funcoes_gerais.ler_todas_paginas(coluna_temporario_extraida)
    
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            #Puxando as tabelas
            tabela_modelo = "modelos/{}-paginas.csv".format(modelo)
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')
            coluna_modelo = tabela_modelo["ids"].values
            coluna_modelo = coluna_modelo.tolist()
            todas_paginas_modelo = funcoes_gerais.ler_todas_paginas(coluna_modelo)

            somadores = []
            for k in todas_paginas_modelo:
                a = fuzz.partial_ratio(todas_paginas_temporario, k)
                b = fuzz.token_set_ratio(todas_paginas_temporario, k)
                valor = (a+b)/2
                somadores.append(valor) 
                #print("{}-{}-{}\n".format(a,b,valor))
            somador_teste.append(funcoes_gerais.arredondar_valores(sum(somadores)/len(todas_paginas_modelo),2))
        
        #Media 2
        segunda_saida = somador_teste

        #Medias
        retorno_global = arredondamento_para_modelo_multi_operacoes(zip(primeira_saida, segunda_saida), 2)
        
    #Brutal predicao imagens
    elif tipo_analise_modelo == "uso_total_processamento_imagens":
        somador = []
        tabela = funcoes_gerais.limpeza_dominios(["imagens"])
        realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, imagens_extraidas_diretorio)
        nomes_modelos = capturando_nome_modelos(modelos)
        for modelo in nomes_modelos:
            realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, imagens_modelos_diretorio)
            a = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 0, precisao_semente) #Linearregression
            b = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 1, precisao_semente) #LinearVection
            c = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 2, precisao_semente) #Classificacao vetores nao linear
            d = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 3, precisao_semente) #Regressao vetores nao linear
            e = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 4, precisao_semente) #Classifier tree
            f = retorno_somador(lendo_imagens_diretorios(imagens_modelos_diretorio), lendo_imagens_diretorios(imagens_extraidas_diretorio), 5, precisao_semente) #Regression tree
            somador.append(funcoes_gerais.arredondar_valores(((a+b+c+d+e+f)/6), 2))
            criar_diretorio_modelos()
        retorno_global = somador

    #Processamento de banco de palavras
    elif tipo_analise_modelo == "predicao_processamento_banco_palavras":
        
        #Temporarios
        coluna_temporario_extraida = None
        coluna_modelo = None
        somador = []
    
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
    
        #Pagina alvo
        tabela_temporaria_extraida = "csv/{}-frases.csv".format(nome_temporario_para_processo)
        tabela_temporaria_extraida = pandas.read_csv(tabela_temporaria_extraida, sep=';')
        coluna_temporario_extraida = tabela_temporaria_extraida["frases"].values

        vectorizer = TfidfVectorizer()
        vectorizer.fit_transform(coluna_temporario_extraida)
        total_valores_extraido = len(vectorizer.get_feature_names())
    
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            #Puxando as tabelas
            tabela_modelo = "modelos/{}-frases.csv".format(modelo)
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')
            coluna_modelo = tabela_modelo["frases"].values
            
            # create the transform
            vectorizer = TfidfVectorizer()

            # tokenize and build vocab
            vectorizer.fit(coluna_modelo)
            
            # encode document
            vector = vectorizer.transform(coluna_temporario_extraida)

            #Mandando para uma matriz
            somador.append(funcoes_gerais.arredondar_valores(((sum(sum(vector.toarray())) / total_valores_extraido) * 100),2))
                
        #Medias
        retorno_global = somador

    else:
        pass

    #Destruir diretorios imagens
    eliminar_conteudo_diretorio_extraidos()
    eliminar_conteudo_diretorio_modelos()

    #Medias dos valores
    medias = calcular_aprovacao(retorno_global, modelos)

    #Hora final - Final da operacao
    fim = timeit.default_timer()

    #tempo final
    tempo_final = arrumar_tempo(fim-inicio)

    #gravar no log
    funcoes_gerais.registrar_log_comuns("{}-{}-{}".format(retorno_global, medias, tempo_final))

    #retorno do processamento
    #Retorno dos valores globais
    return retorno_global, medias, tempo_final