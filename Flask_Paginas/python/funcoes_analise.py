#Link: https://www.datacamp.com/community/tutorials/fuzzy-string-python
from fuzzywuzzy import fuzz
import pandas
import re

import sqlite_funcoes

#Retorno global 
global retorno_global
retorno_global = 0

#Usando logica de fuzzy para analise de conteudo da pagina
def analise_por_texto_parecido(nome_temporario_para_processo, modelos):

    #Tabelas as serem analisar
    tabelas = ["palavras"]

    #Retorno dos modelos
    retorno_modelos = []

    #Capturando ids para fazer o select dos modelos
    contador_modelos = modelos.split("-")
    modelos_listados = [] 
    for i in contador_modelos:
        if len(i) > 0:
            modelos_listados.append(i)

    nomes_modelos = []
    for valores in modelos_listados:
        for nome in sqlite_funcoes.selecionar_modelos_analise(valores):
            nome = re.sub('[^a-zA-Z0-9]', '', str(nome))
            nomes_modelos.append(nome)

    for modelo in nomes_modelos:
        for tabela in tabelas:

            tabela_temporaria = "csv/{}-{}.csv".format(nome_temporario_para_processo, tabela)
            tabela_modelo = "modelos/{}-{}.csv".format(modelo, tabela)

            tabela_temporaria = pandas.read_csv(tabela_temporaria, sep=';')
            tabela_modelo = pandas.read_csv(tabela_modelo, sep=';')

            #Arrays de palavras
            palavras_modelos = tabela_modelo["palavras"].values;
            palavras_temporario = tabela_temporaria["palavras"].values;

            #Arrays de valores
            palavras_qtd_modelos = tabela_modelo["Qtd"].values;
            palavras_qtd_temporario = tabela_temporaria["Qtd"].values;

            #Quantidade de vezes que havera iterações entre os valores
            quantidade_interacoes = len(palavras_qtd_modelos) + len(palavras_qtd_temporario)

            somador = 0.0
            for i in palavras_modelos:
                for t in palavras_temporario:
                    if int(fuzz.ratio(i,t)) == 100:
                        somador = somador + 1

            retorno_modelos.append(somador / (quantidade_interacoes / 2) * 100)
            
    return retorno_modelos

def escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos):
    if tipo_analise_modelo == "fuzzy":
        retorno_global = analise_por_texto_parecido(nome_temporario_para_processo, modelos)
    return retorno_global