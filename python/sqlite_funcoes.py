#Libs necessarias para fazer o banco
#Especifico
import sqlite3
#Geral
import os
import glob
import shutil
import replace
import re
import pandas

#Import de funcoes
import funcoes_gerais

#variaveis globais
global banco
global quebrador_csv
banco = "teste.db"
quebrador_csv = ";"

#Conectar o banco
def contactar_banco():
    #garantir que vai abrir o banco
    try:
        return sqlite3.connect(banco)
    except:
        contactar_banco()

#Criar o banco
def criar_banco():

    #Tenta coenctar
    try:
        #Escolhe onde conecta
        conn = contactar_banco()
        cursor = conn.cursor()

        #tabela de dominios
        cursor.execute("""
        CREATE TABLE if not exists dominios (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            dominios varchar(10000) not null,
            Qtd int(11) not null
        );
        """)
        conn.commit()

        #tabela dos classificados
        cursor.execute("""
        CREATE TABLE if not exists classificados (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Uri varchar(10000) not null,
            Id_modelos varchar(1000) not null,
            Aprovacao varchar(100) not null
        );
        """)
        conn.commit()

        #tabela de paginas
        cursor.execute("""
        CREATE TABLE if not exists paginas (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_Ext_Dominio int(11) not null,
            Url_pagina varchar(255) NOT NULL,
            Endereco_IP varchar(255) NOT NULL,
            Titulo_pagina varchar(255) not null,
            qtd_linhas_Pagina int(11) not null,
            Idioma_pagina varchar(255) not null,
            Data datetime not null,
            FOREIGN KEY (Id_Ext_Dominio) REFERENCES dominios(ids)
        );
        """)
        conn.commit()

        #Frases
        cursor.execute("""
        CREATE TABLE if not exists frases (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            frases varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Palavras
        cursor.execute("""
        CREATE TABLE if not exists palavras (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            palavras varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #tags
        cursor.execute("""
        CREATE TABLE if not exists tags (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            tags varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Images
        cursor.execute("""
        CREATE TABLE if not exists imagens (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            imagens varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Videos
        cursor.execute("""
        CREATE TABLE if not exists videos (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            videos varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #audio
        cursor.execute("""
        CREATE TABLE if not exists audios (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            audios varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #links
        cursor.execute("""
        CREATE TABLE if not exists links (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            links varchar(10000) NOT NULL,
            Qtd int not null,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Modelos
        cursor.execute("""
        CREATE TABLE if not exists modelos (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            nome varchar(10000) NOT NULL,
            Ids_gerados varchar(10000) not null,
            aprovacao varchar(20) not null,
            descricao varchar(255)
        );
        """)
        conn.commit()

        #Terminar as operações
        conn.close()
        #Fechar operacoes
        return True
    #Deu errado vem para ca
    except:
        pass

#Selecao dos modelos
def select_modelos():
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute("""select * from modelos order by ids desc;""").fetchall()
    conn.commit()
    conn.close()
    return saida

#Destruir todas os dados das tabelas
def destruir_banco_atual():
    #Cria uma conexao para fechar o banco e dai conseguir deletar o arquivo
    conn = contactar_banco()
    conn.commit()
    conn.close()
    #Delete o arquivo caso exista
    if os.path.isfile(banco):
        os.remove(banco)    
    return True

#Destruir modelos csv pos analise
def destruir_modelos_csv():
    if os.path.isdir("csv"):
        shutil.rmtree("csv")
    return True

#Destruir modelos
def destruir_modelos_classificados():
    conn = contactar_banco()
    cursor = conn.cursor()
    cursor.execute("""delete from modelos;""")
    conn.commit()
    conn.close()
    if os.path.isdir("modelos"):
        shutil.rmtree("modelos")
    return True

#Ultimo insert de pagina no banco
def select_ultimo_insert_paginas():
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute("""select ids from paginas order by ids desc limit 1;""").fetchall()
    conn.commit()
    conn.close()
    return saida

#Buscar idiomas das paginas acessadas
def select_idiomas_extraidos():
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute("""select Idioma_pagina from paginas group by Idioma_pagina;""").fetchall()
    conn.commit()
    conn.close()
    return saida

#Todos os modelos ids
#selecionar os modelos
def selecionar_ids_modelos():
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT ids FROM modelos;"""
    saida = cursor.execute(sqlite_insert_with_param).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos
def selecionar_modelos_analise(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT nome FROM modelos where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos e sua aprovacao
def selecionar_modelos_aprovados(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT nome, aprovacao FROM modelos where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos e sua aprovacao
def select_aprovacoes(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT aprovacao FROM modelos where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos
def selecionar_modelos_detalhes(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT * FROM modelos where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos
def selecionar_modelos_detalhes_paginas(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT Ids_gerados FROM modelos where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#selecionar os modelos
def select_paginas_url(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT Url_pagina FROM paginas where ids = ?;"""
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

def select_paginas_limit(limite):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """SELECT ids FROM paginas order by ids desc limit ?"""
    entrada = [limite]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#Insert paginas classificadas 
def insert_pagina_classificada(uri, modelos, aprovacao):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """INSERT INTO classificados (Uri, Id_modelos, Aprovacao) values (?,?,?);"""
    data_tuple = [uri, modelos, aprovacao]
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

#Insert na tabela de modelos
def insert_modelos_comparativos(nome, Ids_gerados, aprovacao, descricao):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """INSERT INTO modelos (nome, Ids_gerados, aprovacao, descricao) values (?,?,?,?);"""
    data_tuple = [nome, Ids_gerados, aprovacao, descricao]
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

#Insert geral em varios bancos diferentes dependente a entrada
def insert_geral_para_tabelas_secudarias(id_pagina, tabela, entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """INSERT INTO {} (Id_pagina_ex, {}, Qtd) values (?,?,?);""".format(tabela, tabela)
    for i in range(0, len(entrada)):
        data_tuple = [id_pagina, str(entrada[i][0]), entrada[i][1]]
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
    conn.close()
    return True

#Insert de dominios
def insert_banco_dominio(dominio):
    #Conexao banco
    conn = contactar_banco()
    cursor = conn.cursor()

    #Confere se o dominio ja existe registrado, se não existe, registra, e se existe, pega o valor do dominio e da insert no atual insert
    Id_Ext_Dominio_Existe = select_banco_nome(dominio)

    saida = 0
    for i in Id_Ext_Dominio_Existe:
        saida = i

    if saida == 0:
        #Inserir o dominio caso o mesmo nao exista
        sqlite_insert_with_param = """INSERT INTO dominios (dominios, Qtd) values (?, ?);"""
        data_tuple = [dominio, 1]
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
    else:

        #Atualizar a quantidade de vezes que o dominio é listado
        sqlite_insert_with_param = """SELECT ids, Qtd FROM dominios where dominios = ?;"""
        entrada = [dominio]
        saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
        conn.commit()

        Id_Dominio = ""
        contador_dominio = ""
        for i in saida:
            Id_Dominio, contador_dominio = i

        data_tuple = [contador_dominio+1, Id_Dominio]

        sqlite_insert_with_param = """UPDATE dominios SET Qtd = ? WHERE ids = ?;"""
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()

    conn.close()

    #Execute a instrução
    #Traz o ID do dominio
    saida = select_banco_nome(dominio)
    filtro_saida = 0
    valor_saida = 0
    for i in saida:
        filtro_saida = i

    for i in filtro_saida:
        valor_saida = i

    return valor_saida 

#Insert no banco
def insert_banco_pagina(Id_Ext_Dominio, Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """INSERT INTO paginas (Id_Ext_Dominio, Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data) values (?,?,?,?,?,?,?);"""
    Id_Ext_Dominio = insert_banco_dominio(Id_Ext_Dominio)
    data_tuple = [Id_Ext_Dominio,  Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data]
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

#Subtrair ou deletar dominio
def subtrair_dominio(dominio_id):
    conn = contactar_banco()
    cursor = conn.cursor()

    sqlite_insert_with_param = """select Qtd FROM dominios where ids = ?;"""
    retorno_dominio = cursor.execute(sqlite_insert_with_param, dominio_id).fetchall()
    conn.commit()

    for i in retorno_dominio:
        retorno_dominio = int(i[0])

    if retorno_dominio == 1:
        sqlite_insert_with_param = """delete from dominios where ids = ?;"""
        cursor.execute(sqlite_insert_with_param, dominio_id)
    else:
        data_tuple = [retorno_dominio-1, dominio_id[0]]
        sqlite_insert_with_param = """UPDATE dominios SET Qtd = ? WHERE ids = ?;"""
        cursor.execute(sqlite_insert_with_param, data_tuple)
    
    conn.commit()
    conn.close()
    return True

#Deletar modelos 
#Deleta um extraido da tabela
def delete_modelo_banco(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    data_tuple = [id_entrada]
    sqlite_insert_with_param = """delete from modelos where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

#Deleta um extraido da tabela
def delete_banco(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()

    data_tuple = [id_entrada]

    sqlite_insert_with_param = """SELECT Id_Ext_Dominio FROM paginas where ids = ?;"""
    retorno_dominio = cursor.execute(sqlite_insert_with_param, data_tuple)

    for i in retorno_dominio:
        retorno_dominio = i

    subtrair_dominio(retorno_dominio)

    #Execute a instrução
    sqlite_insert_with_param = """delete from paginas where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from frases where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from palavras where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from tags where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from imagens where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from videos where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from audios where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from links where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    conn.close()
    return True

#Select tudo
#Select dos extraidos
def select_banco_all():
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute("""select * from paginas;""").fetchall()
    conn.commit()
    conn.close()
    return saida

#Select dos extraidos
def select_banco_extraidos():
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute("""select pag.ids, dom.dominios, pag.Url_pagina from paginas as pag inner join dominios as dom on pag.Id_Ext_Dominio = dom.ids order by pag.ids desc limit 100;""").fetchall()
    conn.commit()
    conn.close()
    return saida

#Retorno do dominio ID via o nome do dominio
def select_banco_nome(dominio):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT ids FROM dominios where dominios = ?;"""
    entrada = [dominio]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#Top 10 dominios mais acessados
def select_count_domain():
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT dominios, Qtd FROM dominios order by Qtd desc limit 10;"""
    saida = cursor.execute(sqlite_insert_with_param).fetchall()
    conn.commit()
    conn.close()
    return saida

#Top 10 ultimos classificados
def select_count_classificados():
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT Uri, Id_modelos, Aprovacao FROM classificados order by ids desc limit 10;"""
    saida = cursor.execute(sqlite_insert_with_param).fetchall()
    conn.commit()
    conn.close()
    return saida

#Top 10 ultimos classificados
def select_count_classificados_somente_id():
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT Id_modelos FROM classificados order by ids desc limit 10;"""
    saida = cursor.execute(sqlite_insert_with_param).fetchall()
    conn.commit()
    conn.close()
    return saida

#Retorno via ID da página
def select_banco_paginas(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """
    SELECT pag.ids, dom.dominios, pag.Url_pagina, pag.Endereco_IP, pag.Titulo_pagina, pag.qtd_linhas_Pagina, pag.Idioma_pagina, pag.data
    from paginas as pag inner join dominios as dom on pag.Id_Ext_Dominio = dom.ids
    where pag.ids = ? limit 1;""" 
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

def select_varios_bancos(id_entrada, tabela):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """
    select fr.{}, fr.Qtd 
    from paginas as pag inner join {} as fr on pag.ids = fr.Id_pagina_ex 
    where fr.Id_pagina_ex = ?;""".format(tabela, tabela) 
    entrada = [id_entrada]
    saida = cursor.execute(sqlite_insert_with_param, entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#Limpeza do header das tabelas
def limpeza_header_tabelas(entrada):
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

#Extracao de banco para CSV I.A
def extracao_csv(modelo, dominios):
    #Banco conexao
    conn = contactar_banco()
    cursor = conn.cursor()

    #Criar diretorio para os csv's
    funcoes_gerais.criar_diretorio("csv")

    #Tabelas
    tabelas_bases = ["paginas", "dominios"]
    tabelas_secundarias = ["frases", "palavras", "tags", "imagens", "videos", "audios", "links"]
    tabelas_todas = tabelas_bases + tabelas_secundarias

    saida_dominios = []
    for i in dominios.split('-'):
        if len(i) != 0:
            saida_dominios.append(i)
    dominios = saida_dominios

    #Escrever header da tabelas nos csv's
    for tabela in tabelas_todas:
        #File CSV
        arquivo = "{}-{}.csv".format(modelo, tabela)
        arquivo_csv = open(arquivo, "a+", encoding="utf-8")

        #Nome das colunas
        sqlite_insert_with_param = """SELECT name FROM PRAGMA_TABLE_INFO('{}');""".format(tabela)
        saida = cursor.execute(sqlite_insert_with_param).fetchall()
        colunas = []
        for i in saida:
            colunas.append(i)
        
        colunas = limpeza_header_tabelas(str(colunas))

        arquivo_csv.write("{}\n".format(colunas))
        arquivo_csv.close()

    #Tabela de páginas
    pesquisa_valores_dominios = []
    for valor_id in dominios:
        valor_id = valor_id.split()

        for tabela in tabelas_bases:
            #Primeiro executa o pagina para ter os valores e depois executa o de dominios
            if tabela == "paginas":
                #File CSV
                arquivo = "{}-{}.csv".format(modelo, tabela)
                arquivo_csv = open(arquivo, "a+", encoding="utf-8")

                #Extrair valores da coluna
                sqlite_insert_with_param = """SELECT * FROM paginas where ids = ? limit 1;"""
                saida = cursor.execute(sqlite_insert_with_param, valor_id).fetchall()
                conn.commit()

                for linhas in saida:
                    saida_coluna = ""
                    contador = 0
                    for coluna in linhas:
                        arquivo_csv.write("{};".format(str(coluna)))
                        if contador == 1:
                            saida_coluna = str(coluna)
                        contador = contador + 1

                    arquivo_csv.write("\n")
                    #Contagem de dominios
                pesquisa_valores_dominios.append(saida_coluna)

                arquivo_csv.close()

    #CSV de dominios
    pesquisa_valores_dominios = sorted(set(pesquisa_valores_dominios))
    for pesquisa_select in pesquisa_valores_dominios:
        pesquisa_select = pesquisa_select.split()

        for tabela in tabelas_bases:
            #Primeiro executa o pagina para ter os valores e depois executa o de dominios
            if tabela == "dominios": 
                #File CSV
                arquivo = "{}-{}.csv".format(modelo, tabela)
                arquivo_csv = open(arquivo, "a+", encoding="utf-8")
                #Extrair valores da coluna
                sqlite_insert_with_param = """SELECT * FROM dominios where ids = ? group by ids;"""
                saida = cursor.execute(sqlite_insert_with_param, pesquisa_select).fetchall()
                conn.commit()

                for linhas in saida:
                    for coluna in linhas:
                        arquivo_csv.write("{};".format(str(coluna)))
                    arquivo_csv.write("\n")
                arquivo_csv.close()

    #Tabela secundarias
    for ids in dominios:
        ids = ids.split()

        for tabela in tabelas_secundarias:
            arquivo = "{}-{}.csv".format(modelo, tabela)
            arquivo_csv = open(arquivo, "a+", encoding="utf-8")
            sqlite_insert_with_param = """SELECT * FROM {} where Id_pagina_ex = ?;""".format(tabela)
            saida = cursor.execute(sqlite_insert_with_param, ids).fetchall()
            for linhas in saida:
                for coluna in linhas:
                    coluna = limpeza_conteudos_tabelas(str(coluna), tabela)
                    arquivo_csv.write("{};".format(str(coluna)))
                arquivo_csv.write("\n")
            arquivo_csv.close()

    #Fecha banco
    conn.close()

    #Mover csv
    for i in glob.glob("*.csv"):
        os.rename(i, "csv/{}".format(i))

    #Saida
    return True

#Listar nomes dos csvs
def nomes_arquivos():
    arquivos = os.listdir("csv")
    ler_arquivos = []
    for arquivo in arquivos:
        ler_arquivos.append("csv/{}".format(arquivo))
    return ler_arquivos

#Ler arquivos csvs
#Limpar os arquivos para criar os modelos
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