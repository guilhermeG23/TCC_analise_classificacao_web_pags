import sqlite3
import os
import glob
import shutil
import replace
import re

global banco
banco = "teste.db"

global quebrador_csv
quebrador_csv = ";"

def contactar_banco():
    return sqlite3.connect(banco)

def criar_banco():
    #Escolhe onde conecta
    conn = contactar_banco()
    cursor = conn.cursor()

    #tabela de dominios
    cursor.execute("""
    CREATE TABLE if not exists dominios (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Dominio varchar(10000) not null,
            Qtd_dominio int(11) not null
    );
    """)
    conn.commit()
    #tabela de paginas
    cursor.execute("""
    CREATE TABLE if not exists paginas (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_Ext_Dominio int(11) not null,
            Url_pagina varchar(255) NOT NULL,
            Titulo_pagina varchar(255) not null,
            qtd_linhas_Pagina int(11) not null,
            Idioma_pagina varchar(255) not null,
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
    CREATE TABLE if not exists audio (
        ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Id_pagina_ex INTEGER NOT NULL,
        audio varchar(10000) NOT NULL,
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
        sqlite_insert_with_param = """INSERT INTO dominios (Dominio, Qtd_dominio) values (?, ?);"""
        data_tuple = [dominio, 1]
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
    else:

        #Atualizar a quantidade de vezes que o dominio é listado
        sqlite_insert_with_param = """SELECT ids, Qtd_dominio FROM dominios where Dominio = ?;"""
        entrada = [dominio]
        saida = cursor.execute(sqlite_insert_with_param, entrada)

        Id_Dominio = ""
        contador_dominio = ""
        for i in saida:
            Id_Dominio, contador_dominio = i

        data_tuple = [contador_dominio+1, Id_Dominio]

        sqlite_insert_with_param = """UPDATE dominios SET Qtd_dominio = ? WHERE ids = ?;"""
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
def insert_banco_pagina(Id_Ext_Dominio, Url_pagina, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina):
    conn = contactar_banco()
    cursor = conn.cursor()
    sqlite_insert_with_param = """INSERT INTO paginas (Id_Ext_Dominio, Url_pagina, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina) values (?,?,?,?,?);"""
    Id_Ext_Dominio = insert_banco_dominio(Id_Ext_Dominio)
    data_tuple = [Id_Ext_Dominio,  Url_pagina, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina]
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

#Subtrair ou deletar dominio
def subtrair_dominio(dominio_id):
    conn = contactar_banco()
    cursor = conn.cursor()

    sqlite_insert_with_param = """select Qtd_dominio FROM dominios where ids = ?;"""
    retorno_dominio = cursor.execute(sqlite_insert_with_param, dominio_id)

    for i in retorno_dominio:
        retorno_dominio = int(i[0])

    if retorno_dominio == 1:
        sqlite_insert_with_param = """delete from dominios where ids = ?;"""
        cursor.execute(sqlite_insert_with_param, dominio_id)
    else:
        data_tuple = [retorno_dominio-1, dominio_id[0]]
        sqlite_insert_with_param = """UPDATE dominios SET Qtd_dominio = ? WHERE ids = ?;"""
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

    sqlite_insert_with_param = """delete from audio where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    sqlite_insert_with_param = """delete from links where ids = ?;"""
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()

    conn.close()
    return True

#Destruir todas os dados das tabelas
def destruir_banco_atual():
    return os.remove(banco)

def select_ultimo_insert_paginas():
    conn = contactar_banco()
    cursor = conn.cursor()
    return cursor.execute("""select ids from paginas order by ids desc limit 1;""")

#Select tudo
#Select dos extraidos
def select_banco_all():
    conn = contactar_banco()
    cursor = conn.cursor()
    return cursor.execute("""select * from paginas;""")

#Select dos extraidos
def select_banco_extraidos():
    conn = contactar_banco()
    cursor = conn.cursor()
    return cursor.execute("""select pag.ids, dom.Dominio, pag.Url_pagina from paginas as pag inner join dominios as dom on pag.Id_Ext_Dominio = dom.ids order by pag.ids desc limit 100;""")

#Retorno do dominio ID via o nome do dominio
def select_banco_nome(dominio):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT ids FROM dominios where Dominio = ?;"""
    entrada = [dominio]
    return cursor.execute(sqlite_insert_with_param, entrada)

#Top 10 dominios mais acessados
def select_count_domain():
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT Dominio, Qtd_dominio FROM dominios order by Qtd_dominio desc limit 10;"""
    return cursor.execute(sqlite_insert_with_param)

#Retorno via ID da página
def select_banco_paginas(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """
    SELECT pag.ids, dom.Dominio, pag.Url_pagina, pag.Titulo_pagina, pag.qtd_linhas_Pagina, pag.Idioma_pagina
    from paginas as pag inner join dominios as dom on pag.Id_Ext_Dominio = dom.ids
    where pag.ids = ? limit 1;""" 
    entrada = [id_entrada]
    return cursor.execute(sqlite_insert_with_param, entrada)

def select_varios_bancos(id_entrada, tabela):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """
    select fr.{}, fr.Qtd 
    from paginas as pag inner join {} as fr on pag.ids = fr.Id_pagina_ex 
    where fr.Id_pagina_ex = ?;""".format(tabela, tabela) 
    entrada = [id_entrada]
    return cursor.execute(sqlite_insert_with_param, entrada)

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
    os.mkdir("csv")

    #Tabelas
    tabelas_bases = ["paginas", "dominios"]
    tabelas_secundarias = ["frases", "palavras", "tags", "imagens", "videos", "audio", "links"]
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

                for linhas in cursor.execute(sqlite_insert_with_param, valor_id).fetchall():
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

#Destruir modelos csv pos analise
def destruir_modelos_csv():
    return shutil.rmtree("csv")