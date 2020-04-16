import pandas
from pandas.plotting import scatter_matrix
import os
import re

"""
#Link:
#https://medium.com/@aasouzaconsult/seu-primeiro-projeto-de-machine-learning-em-python-passo-a-passo-78c5f7bce22d
#https://medium.com/@lucasoliveiras/regress%C3%A3o-linear-do-zero-com-python-ef74a81c4b84
"""

#Listar nomes dos csvs
def nomes_arquivos():
    arquivos = os.listdir("csv")
    ler_arquivos = []
    for arquivo in arquivos:
        ler_arquivos.append("csv/{}".format(arquivo))
    return ler_arquivos

#Ler arquivos csvs
def gerar_modelos_csv():
    arquivos_csv = nomes_arquivos()
    #Criar dataset's
    #dataset = []
    for i in arquivos_csv:
        grupo = i.split("-")
        arquivo_modelo = i.split("/")
        tabelas = grupo[1].split(".")        
        if tabelas[0] == "dominios":
            atual = pandas.read_csv(i, sep=';', index_col=0)
        else:
            atual = pandas.read_csv(i, sep=';', index_col=1)
            #Deleta o ID do dataset das tabelas secundarias para avaliação
            if tabelas[0] != "paginas":
                atual = atual.drop('ids', axis=1)

        #Limpar coluna que não deve aparecer
        atual = atual.loc[:, ~atual.columns.str.contains('^Unnamed')]
        atual.to_csv("modelos/{}".format(arquivo_modelo[1]), sep=";", encoding='utf-8')

    return True

def acionar_IA_classificacao():
    pass