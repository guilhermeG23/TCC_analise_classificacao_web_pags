#Lib para o banco
import sqlite3

#Banco
global banco
banco = "modelo_teste.db"

#Conectar ao banco
#Tentar se conectar até conseguir
def contactar_banco():
    try:
        return sqlite3.connect(banco)
    except:
        contactar_banco()

#Criar o banco
def criar_banco():
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id_modelo INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Nome varchar(10000) NOT NULL,
            Paginas varchar(10000) NOT NULL
        );
        """)
        conn.commit()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paginas (
            id_pagina INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            URL varchar(10000) NOT NULL
        );
        """)
        conn.commit()
        conn.close()
    except:
        pass    
    return True

#Realizar selects sem parametros
def select_banco_sem_parametros(entrada):
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute(entrada).fetchall()
    conn.commit()
    conn.close()
    return saida

#Realizar operacoes com parametros no banco
def banco_com_paramentros(chamada, parametros):
    conn = contactar_banco()
    cursor = conn.cursor()
    saida = cursor.execute(chamada, parametros)
    conn.commit()
    conn.close()
    return saida
        
def selecionar_ultimo_id_pagina_modelo():
    return select_banco_sem_parametros("""select id_pagina from paginas order by id_pagina desc limit 1;""")

def todas_paginas():
    return select_banco_sem_parametros("""select * from paginas order by id_pagina desc;""")

def todos_modelos():
    return select_banco_sem_parametros("""select * from modelos order by id_modelo desc;""")

def selecionar_ultimo_modelo():
    return select_banco_sem_parametros("""select id_modelo, Paginas from modelos order by id_modelo desc limit 1;""")

def select_url_pagina(id_pagina):
    return select_banco_sem_parametros("""select URL from paginas where id_pagina = {};""".format(id_pagina))

def inserir_pagina_banco(url):
    banco_com_paramentros("""insert into paginas (URL) values (?);""", [url])
    return True

def inserir_modelo_banco(nome_modelo, paginas):
    banco_com_paramentros("""insert into modelos (Nome, Paginas) values (?, ?);""", [nome_modelo, paginas])
    return True