import sqlite3

#Escolhe onde conecta
conn = sqlite3.connect('clientes.db')
cursor = conn.cursor()

# criando a tabela (schema)

#Execute a instrução
cursor.execute("""
CREATE TABLE if not exists clientes (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        cpf VARCHAR(11) NOT NULL,
        email TEXT NOT NULL,
        fone TEXT,
        cidade TEXT,
        uf VARCHAR(2) NOT NULL,
        criado_em DATE NOT NULL
);
""")

#Msg
print('Tabela criada com sucesso.')

#Execute a instrução
cursor.execute("""
INSERT INTO clientes (nome, idade, cpf, email, fone, cidade, uf, criado_em)
VALUES ('Matheus', 19, '33333333333', 'matheus@email.com', '11-98765-4324', 'Campinas', 'SP', '2014-06-08')
""")

# gravando no bd - Efetivando
conn.commit()

#Msg
print('Dados inseridos com sucesso.')


# lendo os dados
cursor.execute("""
SELECT * FROM clientes;
""")

for linha in cursor.fetchall():
    print(linha)

# desconectando...
conn.close()
