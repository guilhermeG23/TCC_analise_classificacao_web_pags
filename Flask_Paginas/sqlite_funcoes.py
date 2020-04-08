import sqlite3

global banco
banco = "teste.db"

def contactar_banco():
    return sqlite3.connect(banco)

def criar_banco():
    #Escolhe onde conecta
    conn = contactar_banco()
    cursor = conn.cursor()

    #tabela de dominios
    cursor.execute("""
            CREATE TABLE if not exists dominios (
            ID_Domi INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Dominio varchar(10000) not null
    );
    """)
    conn.commit()
    #tabela de paginas
    cursor.execute("""
    CREATE TABLE if not exists paginas (
            Id_pagina INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_Ext_Dominio varchar(255) not null,
            Url_pagina varchar(255) NOT NULL,
            Titulo_pagina varchar(255) not null,
            Frases varchar(10000) NOT NULL,
            Palavras varchar(10000) NOT NULL,
            Tags varchar(10000) not null,
            Imagens_Nome varchar(10000) not null,
            Videos_Nome varchar(10000) not null,
            Audios_Nome varchar(10000) not null,
            Todos_links varchar(10000) not null,
            qtd_linhas_Pagina int(11) not null
    );
    """)
    #Tabela de imagens
    conn.commit()
    cursor.execute("""
            CREATE TABLE if not exists imagens (
            ID_Imagem INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            ID_Ext_Pagina_Url_Acesso integer not null,
            Imagem varchar(10000) not null
    );
    """)
    conn.commit()
    #Tabela de videos
    cursor.execute("""
            CREATE TABLE if not exists videos (
            ID_Videos INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            ID_Ext_Pagina_Url_Acesso integer not null,
            Video varchar(10000) not null
    );
    """)
    conn.commit()
    #Tabela de audios
    cursor.execute("""
            CREATE TABLE if not exists audios (
            ID_Audio INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            ID_Ext_Pagina_Url_Acesso integer not null,
            Audio varchar(10000) not null
    );
    """)
    conn.commit()
    conn.close()
    return True

#Insert no banco
def insert_banco(Id_Ext_Dominio, Url_pagina, Titulo_pagina, Frases, Palavras, Tags, Imagens_Nome, Videos_Nome, Audios_Nome, Todos_links, qtd_linhas_Pagina):
    #Criando conector e cria o cursor
    conn = contactar_banco()
    cursor = conn.cursor()
    
    #Confere se o dominio ja existe registrado, se não existe, registra, e se existe, pega o valor do dominio e da insert no atual insert
    Id_Ext_Dominio_Existe = select_banco_nome(Id_Ext_Dominio)

    saida = 0
    for i in Id_Ext_Dominio_Existe:
        saida = i

    print(saida)

    if saida == 0:
        sqlite_insert_with_param = """INSERT INTO dominios (Dominio) values (?);"""
        data_tuple = (Id_Ext_Dominio)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
    else:
        Id_Ext_Dominio = Id_Ext_Dominio_Existe

    #Execute a instrução na tabela de paginas
    #Insert de todos os valores dentro da tabela pagina
    sqlite_insert_with_param = """INSERT INTO paginas (Id_Ext_Dominio, Url_pagina, Titulo_pagina, Frases, Palavras, Tags, Imagens_Nome, Videos_Nome, Audios_Nome, Todos_links, qtd_linhas_Pagina) values (?,?,?,?,?,?,?,?,?,?,?);"""
    data_tuple = (Id_Ext_Dominio, Url_pagina, Titulo_pagina, Frases, Palavras, Tags, Imagens_Nome, Videos_Nome, Audios_Nome, Todos_links, qtd_linhas_Pagina)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    
    # gravando no bd - Efetivando
    conn.commit()
    conn.close()
    
    #Finaliza
    return True

def delete_banco(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """delete from paginas where id = ?;"""
    data_tuple = (id_entrada)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    conn.commit()
    conn.close()
    return True

def delete_banco_all():
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()

    sqlite_insert_with_param = """delete from paginas;"""
    cursor.execute(sqlite_insert_with_param)
    conn.commit()

    sqlite_insert_with_param = """delete from dominios;"""
    cursor.execute(sqlite_insert_with_param)
    conn.commit()

    sqlite_insert_with_param = """delete from audios;"""
    cursor.execute(sqlite_insert_with_param)
    conn.commit()

    sqlite_insert_with_param = """delete from videos;"""
    cursor.execute(sqlite_insert_with_param)
    conn.commit()

    sqlite_insert_with_param = """delete from imagens;"""
    cursor.execute(sqlite_insert_with_param)
    conn.commit()

    conn.close()
    return True

def select_banco_all():
    conn = contactar_banco()
    cursor = conn.cursor()
    return cursor.execute("""SELECT * FROM paginas;""")

def select_banco_nome(dominio):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT ID_Domi FROM dominios where Dominio = ?;"""
    entrada = [dominio]
    return cursor.execute(sqlite_insert_with_param, entrada)

def select_banco_id(id_entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT * FROM paginas where Id_pagina = ?;"""
    entrada = [id_entrada]
    return cursor.execute(sqlite_insert_with_param, entrada)

def select_count_domain():
    conn = contactar_banco()
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT Dominio, count(Dominio) FROM dominios group by Dominio order by count(Dominio) desc limit 10;"""
    return cursor.execute(sqlite_insert_with_param)