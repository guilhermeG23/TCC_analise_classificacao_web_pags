#Funcoes para analise bruta

#Libs para o funcionamento
#Especifica
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas
import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.svm import SVR
from sklearn.svm import LinearSVC
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from PIL import Image
import wget
import time
import timeit

#Outros arquivos
import sqlite_funcoes
import funcoes_gerais

#Retorno global 
global retorno_global



"""
Criando diretorios
"""

#criar somente modelos
def criar_diretorio_extraidas():
    funcoes_gerais.criar_diretorio("imagens_extraidas")
    return True

#Criar somente modelos
def criar_diretorio_modelos():
    funcoes_gerais.criar_diretorio("imagens_modelos")
    return True

#Eliminar conteudo do diretorio
def eliminar_conteudo_diretorio_modelos():
    funcoes_gerais.eliminar_conteudo_diretorio("imagens_modelos")
    return True

def eliminar_conteudo_diretorio_extraidos():
    funcoes_gerais.eliminar_conteudo_diretorio("imagens_extraidas")
    return True

#Criar diretorios
def criar_diretorio_imagens():
    criar_diretorio_extraidas()
    criar_diretorio_modelos()
    return True



"""
Outros
"""

#Pegando nome dos modelos com base no id
def capturando_nome_modelos(modelos):
    #Capturando ids para fazer o select dos modelos
    contador_modelos = funcoes_gerais.split_geral(modelos, "-")
    modelos_listados = [] 
    for i in contador_modelos:
        if funcoes_gerais.ler_caracteres(i) > 0:
            modelos_listados.append(i)
    nomes_modelos = []
    #Realizando os selects
    for valores in modelos_listados:
        for nome in sqlite_funcoes.selecionar_modelos_analise(valores):
            nome = funcoes_gerais.limpeza_string_simples(nome)
            nomes_modelos.append(nome)
    #Retorno dos selects
    return nomes_modelos

#Capturando a aprovacao dos modelos
def capturando_aprovacao(modelos):
    #Capturando ids para fazer o select dos modelos
    contador_modelos = funcoes_gerais.split_geral(modelos, "-")
    modelos_listados = [] 
    for i in contador_modelos:
        if funcoes_gerais.ler_caracteres(i) > 0:
            modelos_listados.append(i)
    aprovacoes = []
    #Realizando os selects
    for valores in modelos_listados:
        for provas_modelos in sqlite_funcoes.select_aprovacoes(valores):
            provas_modelos = funcoes_gerais.limpeza_string_simples(provas_modelos)
            aprovacoes.append(provas_modelos)
    #Retorno dos selects
    return aprovacoes

#Decisão sobre precisao do modelos
def calcular_aprovacao(valores_retorno, modelos):

    #Select para buscar estados do modelo
    todos_valores = []
    modelos_ids = funcoes_gerais.split_geral(modelos, "-")
    for id in modelos_ids:
        for t in sqlite_funcoes.select_aprovacoes(id):
            todos_valores.append(funcoes_gerais.limpeza_string_simples(t))

    #Valores gerais e iniciais
    somador_total_aprovado = 0
    somador_total_desaprovado = 0
    contador_total_aprovado = 0
    contador_total_desaprovado = 0

    #Definir a quantidade de aprovados
    for i in range(0, funcoes_gerais.ler_caracteres(todos_valores)):
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
        porcentagem_aprovado = funcoes_gerais.arredondar_valores(porcentagem_aprovado, 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado = 0 
    if todos_valores.count("Bloqueado") >= 1:
        porcentagem_desaprovado = somador_total_desaprovado / contador_total_desaprovado
        porcentagem_desaprovado = funcoes_gerais.arredondar_valores(porcentagem_desaprovado, 2)

    #Valores classificados com aprovacao com base em todos
    porcentagem_aprovado_total = funcoes_gerais.arredondar_valores((somador_total_aprovado / funcoes_gerais.ler_caracteres(todos_valores)), 2)

    #valores classificados com desaprovacao
    porcentagem_desaprovado_total = funcoes_gerais.arredondar_valores((somador_total_desaprovado / funcoes_gerais.ler_caracteres(todos_valores)), 2)

    #Valores não classificados    
    porcentagem_desclassificado = 100 - (porcentagem_aprovado_total + porcentagem_desaprovado_total)
    porcentagem_desclassificado = funcoes_gerais.arredondar_valores(porcentagem_desclassificado, 2)

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
    medias = [funcoes_gerais.ler_caracteres(todos_valores), contador_total_aprovado, porcentagem_aprovado, contador_total_desaprovado, porcentagem_desaprovado, porcentagem_aprovado_total, porcentagem_desaprovado_total, porcentagem_desclassificado, classificacao_analise]

    #retorno das medias das operacoes
    return medias

#Quebrando o dominio para melhor analise
def quebrando_dominio(entrada):
    valores = funcoes_gerais.split_geral(entrada, "/")
    valores = funcoes_gerais.split_geral(valores[2], ".") 
    return valores

#Removendo valores do array de dominios
#E realmente importante nao remover ele, assim, garante menos relacao indesejada entre comparacoes
def remover_valores_array_dominio(entrada):
    #Alterar isso e ler arquivo com extensoes
    extensoes_desnecesarias = open("extensoes/extensoes_uri.txt", "r")
    tudo = entrada
    for i in extensoes_desnecesarias:
        c = "{}".format(funcoes_gerais.split_simples(funcoes_gerais.converte_string(i)))
        try:
            tudo.remove(c)
        except:
            pass
    return tudo

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
            #Puxando as tabelas
            tabela_temporaria_extraida = "csv/{}-{}.csv".format(nome_temporario_para_processo, tabela)
            tabela_modelo = "modelos/{}-{}.csv".format(modelo, tabela)
            #Lendo CSV
            tabela_temporaria_extraida = pandas.read_csv(tabela_temporaria_extraida, sep=';')
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')
            #Arrays de coluna
            coluna_temporario_extraida = tabela_temporaria_extraida[tabela].values
            coluna_modelo = tabela_modelo[tabela].values
            #Limpando repeticoes nas tabelas de modelos e temporarias
            #Ignorando repeticao
            temporario_colunas = funcoes_gerais.limpar_repetidos_array(coluna_temporario_extraida)
            modelo_colunas = funcoes_gerais.limpar_repetidos_array(coluna_modelo)
            
            if dominios:
                modelo_colunas = remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(modelo_colunas)))
                temporario_colunas = remover_valores_array_dominio(quebrando_dominio(funcoes_gerais.limpeza_dominios(temporario_colunas)))

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

#Leitura da imagem 
def ler_imagem(entrada):
    img_tamanho = 10
    return cv2.resize(cv2.imread(entrada), (img_tamanho, img_tamanho))

#Download da imagem
def download_tratamento_imagem(arquivo, pasta, contador, tipo_tratamento_img):
    #Diretorio temporario
    diretorio_temporario = "img_temporario"
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

#Teste dos modelos de regressao
#classificacao binaria
def teste_modelos_regressao(modelos, teste_modelos_regressao, precisao_semente): 
    #Concatenando os valores
    X = np.concatenate((modelos), axis=0)
    #Quantidade de imagens para o index do arra y
    y = []
    for i in range(0, funcoes_gerais.ler_caracteres(modelos)):
        y.append(i)
    y = np.array(y)
    Y = y.reshape(-1)
    # Reshape X with length of y
    X = X.reshape(funcoes_gerais.ler_caracteres(y), -1)
    #Inicializando o classificador
    classifier_linear = None
    #Definindo semente padrão para as operacoes
    if funcoes_gerais.converte_inteiro(precisao_semente) == 0:
        np.random.seed()
    else:
        np.random.seed(funcoes_gerais.converte_inteiro(precisao_semente))
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
    return float("{:.2}".format(funcoes_gerais.soma_array(somador) / funcoes_gerais.ler_caracteres(somador)))

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
    return ((funcoes_gerais.ler_caracteres(igualdade) - contador_false) / funcoes_gerais.ler_caracteres(igualdade)) * 100

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
    imagens_extracao = []
    for i in temporario_colunas:
        #Download da imagem
        download_tratamento_imagem(i, diretorio_extraidas, contador, cinza)
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
    if funcoes_gerais.ler_caracteres(imagens_modelos) > 0 and funcoes_gerais.ler_caracteres(imagens_extracao) > 0:
        classificacao_regressao = teste_modelos_regressao(imagens_modelos, metodo_analise, precisao_semente)
        valor = comparacao_modelo_teste(classificacao_regressao, imagens_modelos, "imagens_extraidas")
        somador = valor
    else:
        somador = 0
    return somador

#Modelo de comparacao de imagens
def processamento_extraidos_modelos(nome_temporario_para_processo, modelos, tabelas, metodo_analise, precisao_semente, cinza):
    #Final
    somador = []
    #Temporarios
    tabela = funcoes_gerais.limpeza_dominios(tabelas)
    #Download imagem
    realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, "imagens_extraidas")
    #Modelos a serem usados
    nomes_modelos = capturando_nome_modelos(modelos)
    #Loop para comparacao dos modelos
    for modelo in nomes_modelos:
        realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, "imagens_modelos")
        somador.append(retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), metodo_analise, precisao_semente))
        eliminar_conteudo_diretorio_modelos()
        criar_diretorio_modelos()
    eliminar_conteudo_diretorio_extraidos()
    return somador


#Uso de funcoes brutais para pegar media geral de varios modelos
def arredondamento_para_modelo_multi_operacoes(entrada_zip, quantidade_operacoes):    
    retorno = []
    for i in entrada_zip:
        retorno.append(funcoes_gerais.arredondar_valores(funcoes_gerais.soma_array(i) / quantidade_operacoes, 2))
    return retorno

#Arrumar tempo
def arrumar_tempo(tempo):
    if tempo > 60:
        tempo = tempo / 60
        tempo = "{:.4}".format(funcoes_gerais.converte_string(tempo))
        tempo = "{} - Minuto\s".format(tempo)
    else:
        tempo = "{:.4}".format(funcoes_gerais.converte_string(tempo))
        tempo = "{} - Segundo\s".format(tempo)
    return tempo 
    
#Funcao para escolher o analisador 
def escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_semente, cinza):

    #Hora atual - Inicio operacao
    inicio = timeit.default_timer()

    #Criar diretorio de imagens por garantia
    criar_diretorio_imagens()

    #Uso de fuzzy para palavras da pagina
    if tipo_analise_modelo == "fuzzy_ratio_palavra":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "ratio", False)

    #Fuzzy parcial para decidir a string
    elif tipo_analise_modelo == "fuzzy_palavra":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "parcial", False)

    #Fuzzy tokenset para analise de frase
    elif tipo_analise_modelo == "fuzzy_tokenset_frase":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_set", False)

    #Fuzzy tokensort para analise de frase
    elif tipo_analise_modelo == "fuzzy_tokensort_frase":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_sort", False)

    #Uso de fuzzy ratio para bater dominio
    elif tipo_analise_modelo == "dominio_ratio":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "ratio", True)    

    #Uso de fuzzy parcial para dominio
    elif tipo_analise_modelo == "dominio_partial":
        retorno_global = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "parcial", True)

    #Uso total dos fuzzys em mais de uma operacao por vez 
    elif tipo_analise_modelo == "uso_total_fuzzy":
        #Inicio do array brutal para qualquer um dos metodos ignorantes
        #a = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "ratio", False)
        b = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "parcial", False)
        c = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_set", False)
        d = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_sort", False)
        #e = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "ratio", True)
        f = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "parcial", True)
        #Retorno comum para o calculo final
        #retorno_global = arredondamento_para_modelo_multi_operacoes(zip(a, b, c, d, e, f), 6)
        retorno_global = arredondamento_para_modelo_multi_operacoes(zip(b, c, d, f), 4)
    
    #Somente funcoes de método ratio
    elif tipo_analise_modelo == "uso_total_fuzzy_ratio":
        #Inicio do array brutal para qualquer um dos metodos ignorantes
        a = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "ratio", False)
        b = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "ratio", True)
        #Retorno comum para o calculo final
        retorno_global = arredondamento_para_modelo_multi_operacoes(zip(a, b), 2)

    #Somente uso de funcoes de parcial
    elif tipo_analise_modelo == "uso_total_fuzzy_parcial":
        #Inicio do array brutal para qualquer um dos metodos ignorantes 
        a = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["palavras"], "parcial", False)
        b = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["dominios"], "parcial", True)
        #Retorno comum para o calculo final
        retorno_global = arredondamento_para_modelo_multi_operacoes(zip(a, b), 2)

    #Somente uso de funcoes de token
    elif tipo_analise_modelo == "uso_total_fuzzy_frase":
        #Inicio do array brutal para qualquer um dos metodos ignorantes
        a = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_set", False)
        b = funcao_decisao_com_fuzzy(nome_temporario_para_processo, modelos, ["frases"], "token_sort", False)
        #Retorno comum para o calculo final
        retorno_global = arredondamento_para_modelo_multi_operacoes(zip(a, b), 2)

    #Analise de imagens
    #Classificação de vetores de suporte linear.
    #Regressao linear
    elif tipo_analise_modelo == "LinearRegression_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 0, precisao_semente, cinza)
    elif tipo_analise_modelo == "VectorLinearRegression_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 1, precisao_semente, cinza)
    elif tipo_analise_modelo == "VectorLinearC_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 2, precisao_semente, cinza)
    elif tipo_analise_modelo == "VectorLinearEpsilon_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 3, precisao_semente, cinza)
    elif tipo_analise_modelo == "TreeDecisionClass_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 4, precisao_semente, cinza)
    elif tipo_analise_modelo == "TreeDecisionRegre_imagens":
        retorno_global = processamento_extraidos_modelos(nome_temporario_para_processo, modelos, ["imagens"], 5, precisao_semente, cinza)

    #Brutal predicao imagens
    elif tipo_analise_modelo == "Uso_total_processamento_imagens":
        somador = []
        #Temporarios
        tabela = funcoes_gerais.limpeza_dominios(["imagens"])
        #Download imagem
        realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, "imagens_extraidas")
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, "imagens_modelos")
            a = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 0, precisao_semente) #Linearregression
            b = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 1, precisao_semente) #LinearVection
            c = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 2, precisao_semente) #Classificacao vetores nao linear
            d = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 3, precisao_semente) #Regressao vetores nao linear
            e = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 4, precisao_semente) #Classifier tree
            f = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 5, precisao_semente) #Regression tree
            somador.append(funcoes_gerais.arredondar_valores(((a+b+c+d+e+f)/6), 2))
            eliminar_conteudo_diretorio_modelos()
            criar_diretorio_modelos()
        retorno_global = somador

    #Somente lineares
    elif tipo_analise_modelo == "Uso_total_funcoes_lineares_imagens":
        somador = []
        #Temporarios
        tabela = funcoes_gerais.limpeza_dominios(["imagens"])
        #Download imagem
        realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, "imagens_extraidas")
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, "imagens_modelos")
            a = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 0, precisao_semente) #Linearregression
            b = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 1, precisao_semente) #LinearVection
            somador.append(funcoes_gerais.arredondar_valores(((a+b)/2), 2))
            eliminar_conteudo_diretorio_modelos()
            criar_diretorio_modelos()
        retorno_global = somador

    #Somente nao lineares
    elif tipo_analise_modelo == "Uso_total_funcoes_nao_lineares_imagens":
        somador = []
        #Temporarios
        tabela = funcoes_gerais.limpeza_dominios(["imagens"])
        #Download imagem
        realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, "imagens_extraidas")
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, "imagens_modelos")
            a = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 2, precisao_semente) #Classificacao vetores nao linear
            b = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 3, precisao_semente) #Regressao vetores nao linear
            somador.append(funcoes_gerais.arredondar_valores(((a+b)/2),2))
            eliminar_conteudo_diretorio_modelos()
            criar_diretorio_modelos()
        retorno_global = somador

    #Somente arvore
    elif tipo_analise_modelo == "Uso_total_funcoes_arvore_imagens":
        somador = []
        #Temporarios
        tabela = funcoes_gerais.limpeza_dominios(["imagens"])
        #Download imagem
        realizando_operacao_extracao_imagens_download("csv", nome_temporario_para_processo, tabela, cinza, "imagens_extraidas")
        #Modelos a serem usados
        nomes_modelos = capturando_nome_modelos(modelos)
        #Loop para comparacao dos modelos
        for modelo in nomes_modelos:
            realizando_operacao_extracao_imagens_download("modelos", modelo, tabela, cinza, "imagens_modelos")
            a = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 4, precisao_semente) #Classifier tree
            b = retorno_somador(lendo_imagens_diretorios("imagens_modelos"), lendo_imagens_diretorios("imagens_extraidas"), 5, precisao_semente) #Regression tree
            somador.append(funcoes_gerais.arredondar_valores(((a+b)/2), 2))
            eliminar_conteudo_diretorio_modelos()
            criar_diretorio_modelos()
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