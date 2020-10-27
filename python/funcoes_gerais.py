#libs necessarias
import os #Lib para trablhar com o S.O
import shutil #Funcoes de gerenciamento no sistema de arquivo
from datetime import datetime #Funcao para o datetime
import time #Lib para tempo
import replace #Import de RE
import glob #lib para leitura de diretorio

#
def criar_diretorio(diretorio):
    if os.path.exists(diretorio) == False:
        os.mkdir(diretorio)
    return True

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

def retorno_arquivos_diretorio(entrada):
    return os.listdir(entrada)

def eliminar_conteudo_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        shutil.rmtree(diretorio)
    return True

def destruir_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        os.rmdir(diretorio)
    return True

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

def dormir(tempo):
    time.sleep(tempo)
    return True

def retorno_hora_atual():
    return datetime.now()

def retorno_data_para_pasta():
    x = retorno_hora_atual()
    return "{}{}{}{}{}{}".format(x.year,x.month,x.day,x.hour,x.minute,x.second)

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

def remover_arquivo(entrada):
    return os.remove(entrada)

def arredondar_valores(valores, arredondamento):
    return round(valores, arredondamento)

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
