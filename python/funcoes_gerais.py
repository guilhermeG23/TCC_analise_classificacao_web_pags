#libs necessarias
import os #Lib para trablhar com o S.O
import shutil #Funcoes de gerenciamento no sistema de arquivo
from datetime import datetime #Funcao para o datetime
import time #Lib para tempo
import replace #Import de RE
import glob #lib para leitura de diretorio

"""
Funcoes gerais
"""

#Criar um diretorio
def criar_diretorio(diretorio):
    if os.path.exists(diretorio) == False:
        os.mkdir(diretorio)
    return True

#Quebrar string de ids
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

#Listar arquivos de um diretorio
def retorno_arquivos_diretorio(entrada):
    return os.listdir(entrada)

#Eliminar conteudo do diretorio
def eliminar_conteudo_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        shutil.rmtree(diretorio)
    return True

#Eliminar o diretorio
def destruir_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        os.rmdir(diretorio)
    return True


#---------------------------------------
#Limpeza
#---------------------------------------
def limpar_n(entrada):
    t = str(entrada)
    t = t.replace("\n", "")
    return t

def limpar_barra(entrada):
    t = str(entrada)
    t = t.replace("//", "/")
    return t

def quebrar_link(url):
    t = str(url)
    t = t.split("/")
    return t
#---------------------------------------

#Aplicar sleep
def dormir(tempo):
    time.sleep(tempo)
    return True

#Data atual
def retorno_hora_atual():
    return datetime.now()

#Retorno da data
def retorno_data_para_pasta():
    x = retorno_hora_atual()
    return "{}{}{}{}{}{}".format(x.year,x.month,x.day,x.hour,x.minute,x.second)

#Listar conteudo do diretorio
def retorno_glob(entrada):
    return glob.glob("{}/*".format(entrada))

def retorno_para_somador_modelos(teste_final, modelo_final):
    igualdade = np.greater_equal(teste_final, modelo_final)
    contador_false = 0
    for c in igualdade:
        if c == False:
            contador_false += 1
    return ((len(igualdade) - contador_false) / len(igualdade)) * 100

#Juntar arrays 
def converter_unico_array(entrada):
    saida_final = []
    for i in entrada:
        for c in i:
            saida_final = saida_final + c
    return saida_final

#Apagar arquivo
def remover_arquivo(entrada):
    return os.remove(entrada)

#Arredondar o valor
def arredondar_valores(valores, arredondamento):
    return round(valores, arredondamento)

#Pegar o top 10 do array
def pegar_top_10_palavras(palavras, valores):
    modelo_matriz = {}
    for i in range(0, len(palavras)):
        modelo_matriz[palavras[i]] = valores[i]
    sort_orders = sorted(modelo_matriz.items(), key=lambda x: x[1], reverse=True)
    saida = []
    top_10 = sort_orders[:10]
    for i in top_10:
        saida.append(i[0])
    return saida
