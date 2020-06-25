#Esse file é só funcao geral para todos os outros files

#Libs necessarias
import os
import shutil
import re
import replace

#Somente valores
def limpeza_somente_valores(entrada):
    return re.sub('[^0-9]', '', str(entrada))

#Limpeza string simples
def limpeza_string_simples(entrada):
    return re.sub('[^0-9a-zA-Z]', '', str(entrada))

#Limpar entrada para ser mostrada nas frases do detalhes da pagina
def limpar_apresentacao_frases(entrada):
    
    #Limpando a entrada
    t = entrada
    t = t.replace("', '", " ")
    t = t.replace("(\"['", "")
    t = t.replace("']\",", " -")
    t = t.replace("('[]',", "[] -")

    #Capturando o valor
    valor = t.split(" - ")
    tratado = str(valor[1:]).replace("['", "")
    tratado = tratado.replace("', '", " - ")
    tratado = tratado.replace(")']", "")
    #Montando a saida
    saida = "{} - {}".format(valor[0], tratado)
    #Retorno
    return saida

#Limpeza da pagina de detalhamento de modelos
def limpar_detalhes_modelos(entrada):
    t = str(entrada)
    t = t.replace("('", "")
    t = t.replace("',)", "")
    t = t.replace("\\", "")
    t = t.replace("/n", "/")
    return t

#limpeza simples de valores array
def limpar_entrada_array(entrada):
    valor = str(entrada)
    valor = valor.replace("['", "")
    valor = valor.replace("']", "")
    valor = valor.replace("[]", "")
    return valor

#Limpeza da data
def limpar_data(entrada):
    #Entrada
    t = entrada
    #Limpeza simples
    t = t.replace("')]", "")
    t = t.replace("'", "")
    #Quebrando o valor
    t = t.split(" ")
    #Quebrando o valor da data
    data = t[1].split("-")
    #Montando a data 
    data = "{}/{}/{}".format(data[2], data[1], data[0])
    #Montando a data final
    t = "{} - {}".format(t[2], data)
    #Return da data
    return t

#Criar diretorio modelo para arquivos csv modelos
def criar_diretorio(diretorio):
    if os.path.exists(diretorio) == False:
        os.mkdir(diretorio)
    return True

#Destruir diretorio caso necessitar
def destruir_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        os.rmdir(diretorio)
    return True

#Eliminar conteudo de um diretorio
def eliminar_conteudo_diretorio(diretorio):
    if os.path.exists(diretorio) == True:
        shutil.rmtree(diretorio)
    return True

#Eliminar arquivo de imagem
def arquivos_imagem(pasta, contador):
    if os.path.isfile('{}/{}.jpeg'.format(pasta, contador)):
        os.remove('{}/{}.jpeg'.format(pasta, contador))
    else:
        pass
    return True