#Esse file é só funcao geral para todos os outros files

#Libs necessarias
import os
import shutil
import re
import replace
import glob
import replace
from datetime import datetime

"""
Funcoes simples de python
"""

#Alterar para string
def converte_string(entrada):
    return str(entrada)

#Alterar para inteiro
def converte_inteiro(entrada):
    return int(entrada)

#Ler quantidade de caracteres
def ler_caracteres(entrada):
    return len(entrada)

#Arredondar valores
def arredondar_valores(valores, arredondamento):
    return round(valores, arredondamento)

#Zipar arrays
def zip_arrays(entrada1, entrada2):
    return zip(entrada1, entrada2)

#soma de array
def soma_array(entrada):
    return sum(entrada)



"""
Demais funcoes python
"""

#Uso de join
def juntar_join(entrada):
    return ''.join(entrada)

#Dar um strip
def dar_strip(entrada):
    return entrada.strip()



"""
Tratamento sobre arquivos
"""

#Renomear arquivo
def renomear_arquivo(entrada):
    return os.rename(entrada, "csv/{}".format(entrada))

#Retorna o que esta dentro do diretorio
def retorno_arquivos_diretorio(entrada):
    return os.listdir(entrada)

#Para HTTP protocol
def re_findall_http(entrada):
    return converte_string(entrada).rfind("http://") >= 0 or converte_string(entrada).rfind("https://") >= 0

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

#Deletar arquivo
def deletar_arquivo(arquivo):
    if os.path.isfile(arquivo):
        os.remove(arquivo)    
    return True

#Retorno de glob
def retorno_glob(entrada):
    return glob.glob("{}/*".format(entrada))

#Retorno dos csvs glob
def retorno_glob_csv():
    return glob.glob("*.csv")

#Concatenando arquivos
def concatenar(diretorio, file):
    file.save(os.path.join(diretorio, file.filename))
    return True



"""
Tratamento de arays
"""

#Limpeza de arrays
def limpar_repetidos_array(entrada):
    saida = []
    for i in entrada:
        try:
            saida.index(i)
        except ValueError:
            saida.append(i) 
    return saida

#Limpeza de dominios
def limpeza_dominios(entrada):
    saida = None
    for i in entrada:
        saida = i
    return saida


"""
uso de split
"""

#Da split simples
def split_simples(entrada):
    return entrada.split()

#Da split no valor
def split_geral(entrada, tipo):
    return entrada.split(tipo)



"""
Ajuste de horas
"""

#Retorno da hora
def retorno_hora_atual():
    return datetime.now()

#Retorno de data ajustada
def retorno_data_ajustada():
    now = retorno_hora_atual()
    return now.strftime("%Y-%m-%d %H:%M:%S")



"""
Ajuste de texto usando expressao regular
"""

#Somente valores
def limpeza_somente_valores(entrada):
    return re.sub('[^0-9]', '', converte_string(entrada))

#Limpeza string simples
def limpeza_string_simples(entrada):
    return re.sub('[^0-9a-zA-Z]', '', converte_string(entrada))

#Aceitando alguns coisas
def limpeza_string_com_adicionais(entrada):
    return re.sub('[^0-9a-zA-Z_-]', '', converte_string(entrada))



"""
Escrever log
"""

#Normais
def registrar_log_comuns(entrada):
    criar_diretorio("logs")
    with open("logs/logs_geral.txt", "a+") as arquivo:
        agora = retorno_hora_atual()
        arquivo.write("{} - {}\n".format(agora, entrada))
    arquivo.close()
    return True

#Erros
def registrar_log_erros(entrada):
    criar_diretorio("logs")
    with open("logs/logs_geral_erros.txt", "a+") as arquivo:
        agora = retorno_hora_atual()
        arquivo.write("{} - {}\n".format(agora, entrada))
    arquivo.close()
    return True



"""
Funcoes de replace
"""

#Replace de links
def replace_links(entrada):
    return replace.replace(entrada, {"..":"", "/\/\/\/":""})

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

#Limpeza do header das tabelas
def limpeza_header_tabelas(entrada, quebrador_csv):
    entrada = entrada.replace(",", "")
    entrada = entrada.replace("[('", "")
    entrada = entrada.replace("')]", quebrador_csv)
    entrada = entrada.replace("') ('", quebrador_csv)
    return entrada

#Limpaze de conteudo para os csv's
#Ta bem na mao isso
def limpeza_conteudos_tabelas(entrada, tabela):
    entrada = entrada.replace(";", "__")
    entrada = entrada.replace("\"", "'")
    entrada = entrada.replace("['", "\"")
    entrada = entrada.replace("]'", "\"")
    entrada = entrada.replace("']", "\"")
    entrada = entrada.replace("[\"", "\"")
    entrada = entrada.replace("', '", " ")
    return entrada

#Busca por imagem parecida
def re_findall_imagens_extracao(entrada):
    return re.findall(r'[^"]+', str(entrada))