#Libs necessarias para fazer o banco
#Especifico
import sqlite3
#Geral
import pandas

#Import de funcoes
import funcoes_gerais

#variaveis globais
global banco
global quebrador_csv
banco = "teste.db"
quebrador_csv = ";"



"""
Criando o banco
"""

#Conectar o banco
def contactar_banco():
    #garantir que vai abrir o banco
    try:
        #Conexao
        return sqlite3.connect(banco)
    except:
        #Erro ao conectar ao banco, vai oa log
        funcoes_gerais.registrar_log_erros("Nao foi possivel conectar ao banco")
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
        CREATE TABLE IF NOT EXISTS dominios (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            dominios TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL
        );
        """)
        conn.commit()

        #tabela dos classificados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS classificados (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Uri TEXT(10000) NOT NULL,
            Id_modelos TEXT(1000) NOT NULL,
            Tipo_analise_modelo TEXT(1000) NOT NULL,
            Tempo_medio_operacao TEXT(1000) NOT NULL, 
            Semente_necessaria TEXT(10) NOT NULL,
            Aprovacao TEXT(100) NOT NULL
        );
        """)
        conn.commit()

        #tabela de paginas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS paginas (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_Ext_Dominio INTEGER NOT NULL,
            Url_pagina TEXT(255) NOT NULL,
            Endereco_IP TEXT(255) NOT NULL,
            Titulo_pagina TEXT(255) NOT NULL,
            qtd_linhas_Pagina INTERGER NOT NULL,
            Idioma_pagina TEXT(255) NOT NULL,
            Data DATETIME NOT NULL,
            FOREIGN KEY (Id_Ext_Dominio) REFERENCES dominios(ids)
        );
        """)
        conn.commit()

        #Frases
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS frases (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            frases TEXT(10000) NOT NULL,
            Qtd INTERGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Palavras
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS palavras (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            palavras TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #tags
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            tags TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Images
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagens (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            imagens TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Videos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            videos TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #audio
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            audios TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #links
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            Id_pagina_ex INTEGER NOT NULL,
            links TEXT(10000) NOT NULL,
            Qtd INTEGER NOT NULL,
            FOREIGN KEY (Id_pagina_ex) REFERENCES paginas(ids)
        );
        """)
        conn.commit()

        #Modelos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            ids INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            nome TEXT(10000) NOT NULL,
            Ids_gerados TEXT(10000) NOT NULL,
            aprovacao TEXT(100) NOT NULL,
            descricao TEXT(10000)
        );
        """)
        conn.commit()

        #Terminar as operações
        conn.close()

    #Deu errado vem para ca
    except:
        #Log
        funcoes_gerais.registrar_log_erros("Falha ao construir o banco")
    
    #Fechar operacoes
    return True



"""
Operacoes totais com as querys
"""

#Modelo select
def select_banco_sem_parametros(entrada):
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        saida = cursor.execute(entrada).fetchall()
        conn.commit()
        conn.close()
        return saida
    except:
        funcoes_gerais.registrar_log_erros("Select sem entradas falhou")

#Modelo select
def select_banco_com_parametros(chamada, parametros):
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        saida = cursor.execute(chamada, parametros).fetchall()
        conn.commit()
        conn.close()
        return saida
    except:
        funcoes_gerais.registrar_log_erros("Select sem entradas falhou")

#Modelo para outras funcoes sem paramentros
def banco_sem_parametros(entrada):
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        saida = cursor.execute(entrada)
        conn.commit()
        conn.close()
        return saida
    except:
        funcoes_gerais.registrar_log_erros("Operacao em banco sem entradas falhou")

#Modelo com paramentros
def banco_com_paramentros(chamada, parametros):
    try:
        conn = contactar_banco()
        cursor = conn.cursor()
        saida = cursor.execute(chamada, parametros)
        conn.commit()
        conn.close()
        return saida
    except:
        funcoes_gerais.registrar_log_erros("Operacao em banco com entradas falhou")



"""
Funcoes para operacoes mais especificas
"""

#Insert de dominios
def insert_banco_dominio(dominio):
    #Confere se o dominio ja existe registrado, se não existe, registra, e se existe, pega o valor do dominio e da insert no atual insert
    Id_Ext_Dominio_Existe = select_banco_nome(dominio)

    saida = 0
    for i in Id_Ext_Dominio_Existe:
        saida = i

    if saida == 0:
        #Inserir o dominio caso o mesmo nao exista
        banco_com_paramentros("""INSERT INTO dominios (dominios, Qtd) values (?, ?);""", [dominio, 1])
    else:
        #Atualizar a quantidade de vezes que o dominio é listado
        saida = select_banco_com_parametros("""SELECT ids, Qtd FROM dominios where dominios = ?;""", [dominio])
        Id_Dominio = ""
        contador_dominio = ""
        for i in saida:
            Id_Dominio, contador_dominio = i
        banco_com_paramentros("""UPDATE dominios SET Qtd = ? WHERE ids = ?;""", [contador_dominio+1, Id_Dominio])

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

#Subtrair ou deletar dominio
def subtrair_dominio(dominio_id):
    retorno_dominio = banco_com_paramentros("""select Qtd FROM dominios where ids = ?;""", dominio_id)
    for i in retorno_dominio:
        retorno_dominio = funcoes_gerais.converte_inteiro(i[0])
    if retorno_dominio == 1:
        banco_com_paramentros("""delete from dominios where ids = ?;""", dominio_id)
    else:
        banco_com_paramentros("""UPDATE dominios SET Qtd = ? WHERE ids = ?;""", [retorno_dominio-1, dominio_id[0]])
    return True



"""
Operacoes de select
"""

"""
Select com parametros
"""

#selecionar os modelos
def selecionar_modelos_analise(id_entrada):
    return select_banco_com_parametros("""select nome from modelos where ids = ?;""", [id_entrada])

#selecionar os modelos e sua aprovacao
def selecionar_modelos_aprovados(id_entrada):
    return select_banco_com_parametros("""select nome, aprovacao from modelos where ids = ?;""", [id_entrada])

#selecionar os modelos e sua aprovacao
def select_aprovacoes(id_entrada):
    return select_banco_com_parametros("""select aprovacao from modelos where ids = ?;""", [id_entrada])

#selecionar os modelos
def selecionar_modelos_detalhes(id_entrada):
    return select_banco_com_parametros("""select * from modelos where ids = ?;""", [id_entrada])

#selecionar os modelos
def selecionar_modelos_detalhes_paginas(id_entrada):
    return select_banco_com_parametros("""select Ids_gerados from modelos where ids = ?;""", [id_entrada])

#selecionar os modelos
def select_paginas_url(id_entrada):
    return select_banco_com_parametros("""select Url_pagina from paginas where ids = ?;""", [id_entrada])

def select_paginas_limit(limite):
    return select_banco_com_parametros("""select ids from paginas order by ids desc limit ?""", [limite])

#Retorno do dominio ID via o nome do dominio
def select_banco_nome(dominio):
    return select_banco_com_parametros("""select ids from dominios where dominios = ?;""", [dominio])

def select_varios_bancos(id_entrada, tabela):
    return select_banco_com_parametros("""select fr.{}, fr.Qtd from paginas as pag inner join {} as fr on pag.ids = fr.Id_pagina_ex where fr.Id_pagina_ex = ?;""".format(tabela, tabela), [id_entrada])

#Retorno via ID da página
def select_banco_paginas(id_entrada):
    return select_banco_com_parametros("""select pag.ids, dom.dominios, pag.Url_pagina, pag.Endereco_IP, pag.Titulo_pagina, pag.qtd_linhas_Pagina, pag.Idioma_pagina, pag.data from paginas as pag inner join dominios as dom on pag.Id_Ext_Dominio = dom.ids where pag.ids = ? limit 1;""", [id_entrada])


"""
Select sem parametros
"""

#Selecao dos modelos
def select_modelos():
    return select_banco_sem_parametros("""select * from modelos order by ids desc;""")

#Ultimo insert de pagina no banco
def select_ultimo_insert_paginas():
    return select_banco_sem_parametros("""select ids from paginas order by ids desc limit 1;""")

#Buscar idiomas das paginas acessadas
def select_idiomas_extraidos():
    return select_banco_sem_parametros("""select Idioma_pagina from paginas group by Idioma_pagina;""")

#Todos os modelos ids
#selecionar os modelos
def selecionar_ids_modelos():
    return select_banco_sem_parametros("""select ids from modelos;""")

#Select tudo
#Select dos extraidos
def select_banco_all():
    return select_banco_sem_parametros("""select * from paginas;""")

#Select dos extraidos
def select_banco_extraidos():
    return select_banco_sem_parametros("""select paginas.ids, dominios.dominios, paginas.Url_pagina from paginas inner join dominios on paginas.Id_Ext_Dominio = dominios.ids order by paginas.ids desc limit 100;""")

#Top 10 dominios mais acessados
def select_count_domain():
    return select_banco_sem_parametros("""select dominios, Qtd from dominios order by Qtd desc limit 10;""")

#Top 10 ultimos classificados
def select_count_classificados():
    return select_banco_sem_parametros("""select Uri, Id_modelos, Tipo_analise_modelo, Tempo_medio_operacao, Semente_necessaria, Aprovacao from classificados order by ids desc limit 10;""")

#Selecao dos modelos
def select_modelos():
    return select_banco_sem_parametros("""select * from modelos order by ids desc;""")

#Top 10 ultimos classificados
def select_count_classificados_somente_id():
    return select_banco_sem_parametros("""select Id_modelos from classificados order by ids desc limit 10;""") 



"""
Insert
"""
    
#Insert paginas classificadas 
def insert_pagina_classificada(uri, modelos, tipo_analise_modelo, Tempo_medio_operacao, Semente_necessaria, aprovacao):
    return banco_com_paramentros("""INSERT INTO classificados (Uri, Id_modelos, Tipo_analise_modelo, Tempo_medio_operacao, Semente_necessaria, Aprovacao) values (?,?,?,?,?,?);""", [uri, modelos, tipo_analise_modelo, Tempo_medio_operacao, Semente_necessaria, aprovacao])

#Insert na tabela de modelos
def insert_modelos_comparativos(nome, Ids_gerados, aprovacao, descricao):
    return banco_com_paramentros("""INSERT INTO modelos (nome, Ids_gerados, aprovacao, descricao) values (?,?,?,?);""", [nome, Ids_gerados, aprovacao, descricao])

#Insert geral em varios bancos diferentes dependente a entrada
def insert_geral_para_tabelas_secudarias(id_pagina, tabela, entrada):
    for i in range(0, funcoes_gerais.ler_quantidade_variavel(entrada)):
        banco_com_paramentros("""INSERT INTO {} (Id_pagina_ex, {}, Qtd) values (?,?,?);""".format(tabela, tabela), [id_pagina, funcoes_gerais.converte_string(entrada[i][0]), entrada[i][1]])
    return True

#Insert no banco
def insert_banco_pagina(Id_Ext_Dominio, Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data):
    Id_Ext_Dominio = insert_banco_dominio(Id_Ext_Dominio)
    return banco_com_paramentros("""INSERT INTO paginas (Id_Ext_Dominio, Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data) values (?,?,?,?,?,?,?);""", [Id_Ext_Dominio,  Url_pagina, Endereco_IP, Titulo_pagina, qtd_linhas_Pagina, Idioma_pagina, Data])



"""
Funcoes de delet
"""

#Deleta um extraido da tabela
def delete_banco(id_entrada):
    data_tuple = [id_entrada]
    for i in select_banco_com_parametros("""SELECT Id_Ext_Dominio FROM paginas where ids = ?;""", data_tuple):
        retorno_dominio = i
    subtrair_dominio(retorno_dominio)
    banco_com_paramentros("""delete from paginas where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from frases where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from palavras where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from tags where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from imagens where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from videos where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from audios where ids = ?;""", data_tuple)
    banco_com_paramentros("""delete from links where ids = ?;""", data_tuple)
    return True

#Destruir modelos
def destruir_modelos_classificados():
    return banco_sem_parametros("""delete from modelos;""")

#Deletar valor classificado
def deletar_url_classificada(entrada):
    banco_com_paramentros("""delete from classificados where Id_modelos like ?;""", [entrada])

#Deletar todos os classificados
def deletar_classificada():
    banco_sem_parametros("""delete from classificados;""")

#Deletar modelos 
#Deleta um extraido da tabela
def delete_modelo_banco(id_entrada):
    return select_banco_com_parametros("""delete from modelos where ids = ?;""", [id_entrada])



"""
Gerando os CSV's para o trabalho nos modelos
"""

#Listar nomes dos csvs
def nomes_arquivos():
    arquivos =funcoes_gerais.retorno_arquivos_diretorio("csv")
    ler_arquivos = []
    for arquivo in arquivos:
        ler_arquivos.append("csv/{}".format(arquivo))
    return ler_arquivos

#Extracao de banco para CSV I.A
def extracao_csv(modelo, dominios):
    #Criar diretorio para os csv's
    funcoes_gerais.criar_diretorio("csv")
    #Tabelas
    tabelas_bases = ["paginas", "dominios"]
    tabelas_secundarias = ["frases", "palavras", "tags", "imagens", "videos", "audios", "links"]
    tabelas_todas = tabelas_bases + tabelas_secundarias

    #Dominios
    saida_dominios = []
    for i in funcoes_gerais.split_geral(dominios, "-"):
        if funcoes_gerais.ler_quantidade_variavel(i) != 0:
            saida_dominios.append(i)
    dominios = saida_dominios

    #Escrever header da tabelas nos csv's
    for tabela in tabelas_todas:
        #File CSV
        arquivo = "{}-{}.csv".format(modelo, tabela)
        arquivo_csv = open(arquivo, "a+", encoding="utf-8")

        #Nome das colunas
        colunas = []
        for i in select_banco_sem_parametros("""SELECT name FROM PRAGMA_TABLE_INFO('{}');""".format(tabela)):
            colunas.append(i)
        colunas = funcoes_gerais.limpeza_header_tabelas(funcoes_gerais.converte_string(colunas), quebrador_csv)
        #Escrever em um arquivo
        arquivo_csv.write("{}\n".format(colunas))
        arquivo_csv.close()

    #Tabela de páginas
    pesquisa_valores_dominios = []
    for valor_id in dominios:
        valor_id = funcoes_gerais.split_simples(valor_id)

        for tabela in tabelas_bases:
            #Primeiro executa o pagina para ter os valores e depois executa o de dominios
            if tabela == "paginas":
                #File CSV
                arquivo = "{}-{}.csv".format(modelo, tabela)
                arquivo_csv = open(arquivo, "a+", encoding="utf-8")

                #Extrair valores da coluna
                for linhas in select_banco_com_parametros("""SELECT * FROM paginas where ids = ? limit 1;""", valor_id):
                    saida_coluna = ""
                    contador = 0
                    for coluna in linhas:
                        arquivo_csv.write("{};".format(funcoes_gerais.converte_string(coluna)))
                        if contador == 1:
                            saida_coluna = funcoes_gerais.converte_string(coluna)
                        contador = contador + 1

                    arquivo_csv.write("\n")
                    #Contagem de dominios
                pesquisa_valores_dominios.append(saida_coluna)

                arquivo_csv.close()

    #CSV de dominios
    pesquisa_valores_dominios = sorted(set(pesquisa_valores_dominios))
    for pesquisa_select in pesquisa_valores_dominios:
        pesquisa_select = funcoes_gerais.split_simples(pesquisa_select)

        for tabela in tabelas_bases:
            #Primeiro executa o pagina para ter os valores e depois executa o de dominios
            if tabela == "dominios": 
                #File CSV
                arquivo = "{}-{}.csv".format(modelo, tabela)
                arquivo_csv = open(arquivo, "a+", encoding="utf-8")
                #Extrair valores da coluna
                for linhas in select_banco_com_parametros("""select * from dominios where ids = ? group by ids;""", pesquisa_select):
                    for coluna in linhas:
                        arquivo_csv.write("{};".format(funcoes_gerais.converte_string(coluna)))
                    arquivo_csv.write("\n")
                arquivo_csv.close()

    #Tabela secundarias
    for ids in dominios:
        ids = funcoes_gerais.split_simples(ids)

        for tabela in tabelas_secundarias:
            arquivo = "{}-{}.csv".format(modelo, tabela)
            arquivo_csv = open(arquivo, "a+", encoding="utf-8")
            for linhas in select_banco_com_parametros("""select * from {} where Id_pagina_ex = ?;""".format(tabela), ids):
                for coluna in linhas:
                    coluna = funcoes_gerais.limpeza_conteudos_tabelas(funcoes_gerais.converte_string(coluna), tabela)
                    arquivo_csv.write("{};".format(funcoes_gerais.converte_string(coluna)))
                arquivo_csv.write("\n")
            arquivo_csv.close()

    #Mover csv
    for i in funcoes_gerais.retorno_glob_csv():
        funcoes_gerais.renomear_arquivo(i)
    #Saida
    return True

#Ler arquivos csvs
#Limpar os arquivos para criar os modelos
def gerar_modelos_csv():
    #Confirmar consistencia
    try:
        arquivos_csv = nomes_arquivos()
        #Criar dataset's
        #dataset = []
        for i in arquivos_csv:
            grupo = funcoes_gerais.split_geral(i, "-")
            arquivo_modelo = funcoes_gerais.split_geral(i, "/")
            tabelas = funcoes_gerais.split_geral(grupo[1], ".")
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
    except:
        #Log de erro
        funcoes_gerais.registrar_log_erros("Nao foi gerado o csv de modelos")
    return True



"""
Funcoes de destruir arquivos e diretorios
"""

#Destruir todas os dados das tabelas
def destruir_banco_atual():
    try:
        #Cria uma conexao para fechar o banco e dai conseguir deletar o arquivo
        conn = contactar_banco()
        conn.commit()
        conn.close()
        #Delete o arquivo caso exista
        funcoes_gerais.deletar_arquivo(banco)
    except:
        #Erro
        funcoes_gerais.registrar_log_erros("Falha ao destruir o banco") 
    return True

#Destruir modelos csv pos analise
def destruir_modelos_csv():
    try:
        funcoes_gerais.eliminar_conteudo_diretorio("csv")
        funcoes_gerais.destruir_diretorio("csv")
    except:
        funcoes_gerais.registrar_log_erros("Falha ao destruir diretorio CSV")
    return True