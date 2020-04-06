import sqlite3

def criar_banco():
    #Escolhe onde conecta
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE if not exists paginas (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            dominio varchar(255) not null,
            url varchar(255) NOT NULL,
            frases varchar(10000) NOT NULL,
            palavras varchar(10000) NOT NULL,
            tags varchar(10000) not null,
            imagens varchar(10000) not null,
            qtd_linhas int(11) not null,    
            classificacao varchar(255)
    );
    """)
    conn.close()
    return True

def insert_banco(dominio, url, frases, palavras, tags, imagens, qtd_tags, classificacao):
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """INSERT INTO paginas (dominio, url, frases, palavras, tags, imagens, qtd_linhas, classificacao) values (?, ?, ?, ?, ?, ?, ?, ?);"""
    data_tuple = (dominio, url, frases, palavras, tags, imagens, qtd_tags, classificacao)
    cursor.execute(sqlite_insert_with_param, data_tuple)
    # gravando no bd - Efetivando
    conn.commit()
    conn.close()
    return True

def delete_banco(id_entrada):
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """delete from paginas where id = ?;"""
    data_tuple = [id_entrada]
    cursor.execute(sqlite_insert_with_param, data_tuple)
    # gravando no bd - Efetivando
    conn.commit()
    conn.close()
    return True

def delete_banco_all():
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """delete from paginas;"""
    cursor.execute(sqlite_insert_with_param)
    # gravando no bd - Efetivando
    conn.commit()
    conn.close()
    return True

def select_banco_all():
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    valor = cursor.execute("""SELECT * FROM paginas;""")
    return valor

def select_banco(id_entrada):
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT * FROM paginas where id = ?;"""
    entrada = [id_entrada]
    valor = cursor.execute(sqlite_insert_with_param, entrada)
    return valor

def select_count_domain():
    conn = sqlite3.connect("teste.db")
    cursor = conn.cursor()
    #Execute a instrução
    sqlite_insert_with_param = """SELECT dominio, count(dominio) FROM paginas group by dominio;"""
    return cursor.execute(sqlite_insert_with_param)