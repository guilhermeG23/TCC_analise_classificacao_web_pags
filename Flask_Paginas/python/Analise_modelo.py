import pandas
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import os
import re

"""
#Link:
#https://medium.com/@aasouzaconsult/seu-primeiro-projeto-de-machine-learning-em-python-passo-a-passo-78c5f7bce22d
"""

#Listar nomes dos csvs
def nomes_arquivos():
    arquivos = os.listdir("csv")
    ler_arquivos = []
    for arquivo in arquivos:
        ler_arquivos.append("csv/{}".format(arquivo))
    return ler_arquivos

#Ler arquivos csvs
def leitura_csvs():
    arquivos_csv = nomes_arquivos()

    #Criar dataset's
    dataset = []
    for i in arquivos_csv:
        grupo = i.split("-")
        tabelas = grupo[1].split(".")
        
        if tabelas[0] == "dominios":
            atual = pandas.read_csv(i, sep=';', index_col=0)
        else:
            atual = pandas.read_csv(i, sep=';', index_col=1)

        #Limpar coluna que não deve aparecer
        atual = atual.loc[:, ~atual.columns.str.contains('^Unnamed')]
        dataset.append(atual)

    return dataset

def acionar_IA_classificacao():

    dataset = leitura_csvs()

    for i in dataset:
        print(i)

    return True


#Ordem de leitura
"""
sasageyo-audio.csv
sasageyo-dominios.csv
sasageyo-frases.csv
sasageyo-imagens.csv
sasageyo-links.csv
sasageyo-paginas.csv
sasageyo-palavras.csv
sasageyo-tags.csv
sasageyo-videos.csv
"""