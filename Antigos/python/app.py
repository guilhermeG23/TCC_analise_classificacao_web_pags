#Bibliotecas importadas
#Especifico
from flask import Flask, render_template, request, redirect, url_for
 
#Outros arquivos python que contem as funcoes
import sqlite_funcoes
import extrair_Pagina
import funcoes_analise
import funcoes_gerais

#Global
#Retorno das analises
global retornos
retornos = []



"""
Funcoes
"""

#Versoes
#Todas as versoes
def todas_versoes_software():
    with open("./versoes/versoes.txt") as arquivo:
        saida = []
        for i in arquivo:
            saida.append(funcoes_gerais.split_geral(i, "|"))
        arquivo.close()
    return saida

#Retorno de versoa
def retorno_versao_icone():
    versoes = todas_versoes_software()
    versoes = versoes[-1]
    #Retorno das analises
    return "{} | {} | {}".format(versoes[0], versoes[1], versoes[2]), versoes[4]

#Criar diretorio modelo para arquivos csv modelos
def criar_diretorio_modelos():
    funcoes_gerais.criar_diretorio("modelos")

#Funcao para cirar os modelos
def funcao_criar_modelos(modelo_nome, pesquisar_dominios, aprovacao_do_modelo, descricao_do_modelo):
    #Nome do modelo reformado
    modelo_nome = funcoes_gerais.limpeza_string_com_adicionais(modelo_nome)
    #Gerar CSV
    sqlite_funcoes.extracao_csv(modelo_nome, pesquisar_dominios)
    #Implementar aqui no meio a I.A
    sqlite_funcoes.gerar_modelos_csv()
    #Insert no banco de modelos
    sqlite_funcoes.insert_modelos_comparativos(modelo_nome, funcoes_gerais.converte_string(pesquisar_dominios), funcoes_gerais.converte_string(aprovacao_do_modelo), funcoes_gerais.converte_string(descricao_do_modelo))
    #Destruir modelos apos a analise da I.A
    sqlite_funcoes.destruir_modelos_csv()
    #Retorno normal
    return True

#Registrar pagina
def registar_url(url, pagina):
    if funcoes_gerais.ler_caracteres(url) > 0:
    #Confirma se consegue capturar a pagina
        if pagina != False :
            #Confere o estado do URL
            if funcoes_gerais.converte_string(extrair_Pagina.status_url(pagina)) == "200":
                #Extracao e entrada no banco
                processar_url(url, pagina)
    return True

#Processar a entrada de uma URL
def processar_url(url, pagina):
    #Abrir o banco
    sqlite_funcoes.criar_banco()
    #Trazer o estado da página
    pagina = extrair_Pagina.capturar_pagina(pagina)
    #Titulo da página
    titulo = extrair_Pagina.extrar_titulo(pagina)
    #Quantidade de linhas do html
    qtd_linhas_pag = extrair_Pagina.qtd_linhas_pagina(pagina)
    #Idioma da página pelo titulo
    idioma = extrair_Pagina.detectar_idioma(titulo)
    #Ips da pagina se possivel
    ip_pagina = extrair_Pagina.endereco_ip_web(url)
    #Obter dominio da pagina
    dominio = extrair_Pagina.obter_dominio(url)
    #Insert principal da pagina
    sqlite_funcoes.insert_banco_pagina(dominio, url, ip_pagina, titulo, qtd_linhas_pag, idioma, extrair_Pagina.hora_atual_operacao())
    #Extrair ID da ultima página extraida
    id_pagina = sqlite_funcoes.select_ultimo_insert_paginas()
    for i in id_pagina:
        id_pagina = i
    id_pagina = id_pagina[0]
    #Todas as tags
    todas_tags = extrair_Pagina.tags_pagina(pagina)
    tags = extrair_Pagina.quantificar_palavras(extrair_Pagina.tags_pagina(pagina))
    #Todas as frases
    frases = extrair_Pagina.quantificar_palavras(extrair_Pagina.frases_listadas(funcoes_gerais.limpar_repetidos_array(extrair_Pagina.buscar_lista(todas_tags)), pagina))
    #Todas as palavras do html
    palavras = extrair_Pagina.quantificar_palavras(extrair_Pagina.palavras_listadas(funcoes_gerais.limpar_repetidos_array(extrair_Pagina.buscar_lista(todas_tags)), pagina))
    #Capturar imagens
    imagens = extrair_Pagina.quantificar_palavras(extrair_Pagina.tags_imagens(pagina, dominio))
    #Links da pagina
    links = extrair_Pagina.quantificar_palavras(extrair_Pagina.Extrair_links(pagina, dominio))
    #Links videos
    videos = extrair_Pagina.quantificar_palavras(extrair_Pagina.Extrair_videos(pagina, dominio))
    #Link audios
    audios = extrair_Pagina.quantificar_palavras(extrair_Pagina.Extrair_audios(pagina, dominio))
    #Realizar cadastros
    tabelas = ["tags", tags, "frases", frases, "palavras", palavras, "imagens", imagens, "videos", videos, "audios", audios, "links", links]
    for tabela in range(0, funcoes_gerais.ler_caracteres(tabelas), 2):
        sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, tabelas[funcoes_gerais.converte_inteiro(tabela)], tabelas[funcoes_gerais.converte_inteiro(tabela) + 1])
    #Retorno neutro após extracao
    return True

#Realizar upload de file txt
def upload_file(diretorio, file):
    #Cria a pastas
    funcoes_gerais.criar_diretorio(diretorio)
    #Faca o upload
    funcoes_gerais.concatenar(diretorio, file)
    #Caminho do arquivo
    return "{}/{}".format(diretorio, file.filename)

#Funcao para deletar os modelos pelo ID
def deleter_modelo_id(entrada):
    #Buscandos os nomes dos mdoelos
    saida = sqlite_funcoes.selecionar_modelos_analise(entrada)
    modelos_deletar = []
    for i in saida:
        modelos_deletar.append(funcoes_gerais.limpeza_string_simples(i))
    #Deletar valor em classificados
    sqlite_funcoes.deletar_url_classificada("%-{}-%".format(entrada))
    #Apagandos os arquivos
    csvs = ["audios", "dominios", "frases", "imagens", "links", "paginas", "palavras", "tags", "videos"]
    for modelo in modelos_deletar:
        for csv in csvs:
            funcoes_gerais.deletar_arquivo("modelos/{}-{}.csv".format(modelo, csv))
    #Realizar os deletes
    sqlite_funcoes.delete_modelo_banco(entrada)
    #Retorno verdadeiro
    return True



"""
Paginas apresentaveis
"""

#Flask
#Iniciando o flask
app = Flask(__name__, static_folder='../Static', template_folder='../templates')

#Pagina princiapl
@app.route("/index")
@app.route("/")
def index():
    try:
        #Criar banco caso tiver problemas
        sqlite_funcoes.criar_banco()
        #Fazer requisicao de dominios para apresentacao no index
        dominios = sqlite_funcoes.select_count_domain()
        #Classificados
        classificados = sqlite_funcoes.select_count_classificados()
        aprovacoes = sqlite_funcoes.select_count_classificados_somente_id()
        #Puxandos os nomes dos modelos
        saida_aprovados = []
        for i in aprovacoes:
            momento = []
            for t in funcoes_gerais.split_geral(funcoes_gerais.juntar_join(i), "-"):
                if t != "":
                    x = funcoes_gerais.limpeza_string_simples(sqlite_funcoes.selecionar_modelos_analise(t))
                    momento.append([x, t])
                else:
                    pass
            saida_aprovados.append(momento)

        #Retorno dos classificados de forma ajustada
        classificados = funcoes_gerais.zip_arrays(classificados, saida_aprovados)
        #Montar a pagina
        return render_template("index.html", versao=versao, css=css, js=js, titulo="Index - Página principal", icone=icone, links_menu=links_menu, dominios=dominios, classificados=classificados)
    except:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar no index")
        return redirect(url_for("erro"))

#Pagina dos já extraidos
@app.route("/extraidos")
def extraidos():
    #try:
    #Criar banco caso tiver problemas
    sqlite_funcoes.criar_banco()
    #Mostrar pagina das paginas extraidas
    tabela = sqlite_funcoes.select_banco_extraidos()
    #Render a pagina
    return render_template("extraidos.html", versao=versao, css=css, js=js, titulo="Paginas extraidas", icone=icone, links_menu=links_menu, linhas=tabela)

#Pagina para selecionar os que serao classificados
@app.route("/classificador_paginas")
def classificador_paginas():
    try:
        #Criar o banco
        sqlite_funcoes.criar_banco()
        #Select das paginas para extracao
        tabela = sqlite_funcoes.select_banco_extraidos()
        #Render na pagina
        return render_template("classificar_paginas.html", versao=versao, css=css, titulo="Classificador de páginas", icone=icone, js=js, links_menu=links_menu, linhas=tabela)
    except:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar na pagina de classificacao")
        return redirect(url_for("erro"))

#Pagina para selecionar os que serao classificados
@app.route("/modelos")
def modelos():
    try:
        #Criar o banco
        sqlite_funcoes.criar_banco()
        #Selecionar modelo
        tabela = sqlite_funcoes.select_modelos()
        #Render na pagina
        return render_template("modelos.html", versao=versao, css=css, js=js, titulo="Modelos", icone=icone, links_menu=links_menu, linhas=tabela)
    except:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar na pagina de modelos")
        return redirect(url_for("erro"))

#Arrumar esse
#Pagina para testar os modelos com as classificações já feitas
@app.route("/testar_modelos")
def testar_modelos():
    try:
        criar_diretorio_modelos()
        sqlite_funcoes.criar_banco() 
        valores_modelos = sqlite_funcoes.select_modelos()
        return render_template("testador_modelos.html", versao=versao, css=css, js=js, titulo="Testar modelos", icone=icone, links_menu=links_menu, linhas=valores_modelos)
    except:
        funcoes_gerais.registrar_log_erros("Erro ao criar testador de modelos")
        return redirect(url_for("erro"))

#Mostrar as versoes do software
@app.route("/versoes")
def versoes():
    try:
        return render_template("versoes.html", versao=versao, css=css, js=js, titulo="Versões", icone=icone, links_menu=links_menu, versoes=todas_versoes_software())
    except:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar em versoes")
        return redirect(url_for("erro"))



"""
Operacoes do flask executadas pelas paginas html
"""

#Criar CSV
@app.route("/criar_modelos", methods=['GET', 'POST'])
def criar_modelos():
    try:
        #Criar diretorio para os modelos
        criar_diretorio_modelos()
        #Confirma que a requisicao e post
        if request.method == "POST":
            #Requests post
            #Chamar funcao de classificacao
            funcao_criar_modelos(request.form.get("modelo_nome"), request.form.get("pesquisar_dominios"), request.form.get("aprovacao_do_modelo"), request.form.get("descricao"))
        #Retorno    
        return redirect(url_for("modelos"))
    except:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao criar modelos")
        return redirect(url_for("erro"))

#Criar modelo via TXT
@app.route("/criar_modelo_txt", methods=['GET', 'POST'])
def criar_modelo_txt():
    try:
        #Criar o diretorio modelo
        criar_diretorio_modelos()
        #Diretorio
        diretorio = "uploads"
        #Destruir diretorio
        funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
        funcoes_gerais.destruir_diretorio(diretorio)
        #Tipo de requisicao
        if request.method == "POST":
            arquivo = upload_file(diretorio, request.files["txt_classifica"])
            #Inicio do contador
            contador = 0
            #Leia arquivo do upload
            with open(arquivo) as saida:
                #Ler as linhas do arquivo
                for i in saida:
                    #Url atual
                    url = funcoes_gerais.dar_strip(i)
                    #Capturar a pagina
                    pagina = extrair_Pagina.capturar_pagina_url(url)
                    #Confirmar que esta extraindo a pagina e nao um false
                    try:
                        registar_url(url, pagina)
                        #Contador
                        contador = contador + 1
                    except:
                        funcoes_gerais.registrar_log_erros("Erro ao registrar alguma URL")
            #Fechando o txt
            saida.close()
            #Deleta uploads
            funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
            funcoes_gerais.destruir_diretorio(diretorio)
            #Jeito que deve ser
            #-123-122
            #Puxando os ultimos valores inseridos com uso do limitador para criar a chamada
            valores = sqlite_funcoes.select_paginas_limit(contador)
            ids_totais = ""
            for i in valores:
                i = funcoes_gerais.limpeza_somente_valores(i)
                ids_totais = "{}-{}".format(ids_totais, i)
            pesquisar_dominios = ids_totais
            #Requests post
            #Registrando modelo
            funcao_criar_modelos(request.form.get("modelo_nome"), pesquisar_dominios, request.form.get("aprovacao_do_modelo"), request.form.get("descricao"))

        #Caso der alguma coisa no post, passa reto
        else:
            pass
                
        #Retorno    
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao criar modelo txt")
        return redirect(url_for("erro"))

#Comparacao dos modelos com o url
@app.route("/processamento_modelos", methods=['GET', 'POST'])
def processamento_modelos():
    try:
        #Destruir csv por seguranca
        sqlite_funcoes.destruir_modelos_csv()
        #Criar modelos
        criar_diretorio_modelos()
        #Limpando os valores do array
        retornos.clear()
        #Pesquisa tipo post
        if request.method == "POST":
            #Obter valor do input
            url = request.form.get("url")
            modelos = request.form.get("pesquisar_dominios")
            tipo_analise_modelo = request.form.get("modelos_de_analise")
            #Obter aplicar de escala de cinza
            cinza = request.form.get("escala_cinza")

            #Valor da semente
            precisao_semente = request.form.get("precisao_semente")

            #Retorno no array para mostrar a saida
            retornos.append(tipo_analise_modelo)
            retornos.append(url)

            #Retorno do nomes dos modelo 
            saidas = modelos.split("-")
            saidona = []
            for saida in saidas:
                if funcoes_gerais.ler_caracteres(saida) > 0:
                    saidona.append(saida)
            saidas = saidona

            nome_modelos = []
            for i in saidas:
                for t in sqlite_funcoes.selecionar_modelos_aprovados(i):
                    nome_modelos.append(t)
            retornos.append(nome_modelos)
            
            #Capturar página -> Fazer comunicação
            pagina = extrair_Pagina.capturar_pagina_url(url)
            #Confirma se consegue capturar a pagina
            if pagina == False :
                #Deu errado volte para o index
                return redirect(url_for("testar_modelos"))
            else:
                #Confere o estado do URL
                if funcoes_gerais.converte_string(extrair_Pagina.status_url(pagina)) == "200":
                    try:
                        #Extracao e entrada no banco
                        registar_url(url, pagina)
                        #Variaveis para o trabalho do csv
                        id_pesquisa = sqlite_funcoes.select_ultimo_insert_paginas()
                        for i in id_pesquisa:
                            #Limpar
                            i = funcoes_gerais.limpeza_somente_valores(i)
                        id_pesquisa = i
                        id_pesquisa = "-{}".format(id_pesquisa)
                        nome_temporario_para_processo ="modelotemporario"
                        #Extracao da ultima pagina que fez entrada no banco
                        sqlite_funcoes.extracao_csv(nome_temporario_para_processo, id_pesquisa)
                        #Comparaca da extracao com os modelos fica bem aqui
                        retornos.append(funcoes_analise.escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_semente, cinza))
                        retornos.append(precisao_semente)
                        #Destruir modelos de csv
                        sqlite_funcoes.destruir_modelos_csv()
                        #Insert nos classificados
                        sqlite_funcoes.insert_pagina_classificada(url, modelos, tipo_analise_modelo, retornos[3][2], precisao_semente, retornos[3][1][8])
                    except:
                        funcoes_gerais.registrar_log_erros("Erro ao processador modelos")
        #Retorno
        return redirect(url_for("exibir_teste_modelos"))
    except:
        funcoes_gerais.registrar_log_erros("Erro durante o processamento de modelos")
        return redirect(url_for("erro"))        
    
#Detalhes dos modelos
@app.route("/exibir_teste_modelos", methods=['GET', 'POST'])
def exibir_teste_modelos():
    try:
        criar_diretorio_modelos()
        if retornos:
            return render_template("resultado_analise_modelo.html", versao=versao, css=css, js=js, titulo="Resultado da analise", icone=icone, links_menu=links_menu, linhas=retornos)
        else:
            return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao exibir teste de modelos")
        return redirect(url_for("erro"))  

#Detalhes dos modelos
@app.route("/detalhes_modelos", methods=['GET', 'POST'])
def detalhes_modelos():
    try:
        criar_diretorio_modelos()
        #log
        if request.method == "GET":
            
            #Funcao de seguranca para o banco
            sqlite_funcoes.criar_banco()
            #Entrada para pesquisa de detalhes
            identificador = request.args.get('id_modelo')
            #Select para demonstrar os detalhes
            modelos_geral = sqlite_funcoes.selecionar_modelos_detalhes(identificador)
            paginas_contidas = sqlite_funcoes.selecionar_modelos_detalhes_paginas(identificador)
            paginas = []
            id_paginas = []
            #Buscando paginas que compoem o modelo
            for i in paginas_contidas:
                for t in funcoes_gerais.converte_string(i).split("-"):
                    id_url = funcoes_gerais.limpeza_somente_valores(t)
                    if funcoes_gerais.ler_caracteres(id_url) > 0:
                        id_paginas.append(id_url)
                        paginas.append(sqlite_funcoes.select_paginas_url(funcoes_gerais.limpeza_somente_valores(id_url)))
            #Exibicao das paginas
            exibir_paginas = []
            for i in paginas:
                for t in i:
                    exibir_paginas.append(funcoes_gerais.limpar_detalhes_modelos(t))

            #paginas e ID   
            exibir_paginas = funcoes_gerais.zip_arrays(exibir_paginas, id_paginas)

            #Inicoando a pagina
            return render_template("detalhes_modelos.html", versao=versao, css=css, js=js, titulo="Detalhes do modelo", icone=icone, links_menu=links_menu, modelos_geral=modelos_geral, exibir_paginas=exibir_paginas)
        else:
            return redirect(url_for("modelos"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao exibir detalhes de modelos")
        return redirect(url_for("erro"))  

#Detalhes dos links
@app.route("/detalhes_pagina", methods=['GET', 'POST'])
def detalhes_pagina():
    try:
        if request.method == "GET":
            #Criar o banco caso nao exista
            sqlite_funcoes.criar_banco()
            #Capturando o valor
            identificador = request.args.get('id_pagina')

            #Selects necessarios para mostrar o detalhamento
            pagina_geral = sqlite_funcoes.select_banco_paginas(identificador)
            frases = sqlite_funcoes.select_varios_bancos(identificador, "frases")
            palavras = sqlite_funcoes.select_varios_bancos(identificador, "palavras")
            tags = sqlite_funcoes.select_varios_bancos(identificador, "tags")
            imagens = sqlite_funcoes.select_varios_bancos(identificador, "imagens")
            videos = sqlite_funcoes.select_varios_bancos(identificador, "videos")
            audio = sqlite_funcoes.select_varios_bancos(identificador, "audios")
            links = sqlite_funcoes.select_varios_bancos(identificador, "links")

            #Limpando data para apresentacao
            limpa = funcoes_gerais.split_geral(funcoes_gerais.converte_string(pagina_geral), ",")
            data = funcoes_gerais.limpar_data(funcoes_gerais.converte_string(limpa[funcoes_gerais.ler_caracteres(limpa)-1]))

            #Limpando as frases para serem apresentadas
            limpa = []
            for i in frases:
                limpa.append(funcoes_gerais.limpar_apresentacao_frases(funcoes_gerais.converte_string(i)))
            frases = limpa
        
            return render_template("detalhes_pagina.html", versao=versao, css=css, js=js, titulo="Detalhes da página extraida", icone=icone, links_menu=links_menu, pagina_geral=pagina_geral, data=data, frases=frases, palavras=palavras, tags=tags, imagens=imagens, videos=videos, audio=audio, links=links)
        else:
            return redirect(url_for("extraidos"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao exibir delathes")
        return redirect(url_for("erro"))  

#Extrair página web e entender seus componentes
@app.route("/analisar_url", methods=['GET', 'POST'])
def analisar_url():
    try:
        #Metodo post
        if request.method == "POST":
            try:
                #Obter valor do input
                url = request.form.get("url")
                #Capturar página -> Fazer comunicação
                pagina = extrair_Pagina.capturar_pagina_url(url)
                #Saber se existe o url
                registar_url(url, pagina)
            except:
                funcoes_gerais.registrar_log_erros("Erro ao analisar uma URL")
        #Retorno
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Maiores problemas ao analisar uma URL")
        return redirect(url_for("erro"))  

#Analisar txt
#Extrair página web e entender seus componentes
@app.route("/analisar_txt", methods=['GET', 'POST'])
def analisar_txt():
    try:
        diretorio = "uploads"
        funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
        funcoes_gerais.destruir_diretorio(diretorio)
        if request.method == "POST":
            #Upload do arquivo e devolve o caminho
            arquivo = upload_file(diretorio, request.files["txt"])
            #Leia arquivo do upload
            with open(arquivo, "r") as saida:
                #Ler as linhas do arquivo
                for i in saida:
                    #Url atual
                    url = funcoes_gerais.dar_strip(i)
                    #Capturar a pagina
                    pagina = extrair_Pagina.capturar_pagina_url(url)
                    #Saber se existe o url
                    registar_url(url, pagina)
            saida.close()
        #Escapando da analise do txt
        else:
            pass
        #Deleta uploads
        funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
        funcoes_gerais.destruir_diretorio(diretorio)
        #Retorno
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro durante operacao da analise de txt")
        return redirect(url_for("erro"))  



"""
Funcoes de deletar
"""

#Deletar uma analise com base no ID
@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    try:
        if request.method == "POST":
            sqlite_funcoes.criar_banco()
            sqlite_funcoes.delete_banco(request.form.get("id"))
        return redirect(url_for("extraidos"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao deletar conteudo do banco")
        return redirect(url_for("erro")) 

#Destruit toda a base de dados
@app.route("/destruir_banco")
def destruir_banco():
    try:
        for id_modelo in sqlite_funcoes.selecionar_ids_modelos():
            deleter_modelo_id(funcoes_gerais.limpeza_somente_valores(id_modelo))
        sqlite_funcoes.destruir_modelos_classificados()
        sqlite_funcoes.destruir_banco_atual()
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao destruir o banco")
        return redirect(url_for("erro"))

#Destruit toda a base de dados
@app.route("/destruir_modelos")
def destruir_modelos():
    try:
        sqlite_funcoes.destruir_modelos_classificados()
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro oa destruir modelos")
        return redirect(url_for("erro")) 

#Destruit toda a base de dados
@app.route("/destruir_classificados")
def destruir_classificados():
    try:
        sqlite_funcoes.deletar_classificada()
        return redirect(url_for("index"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao destruir classificados")
        return redirect(url_for("erro")) 

#Deletar modelos
@app.route("/deletar_modelos", methods=['GET', 'POST'])
def deletar_modelos():
    try:
        if request.method == "POST":
            sqlite_funcoes.criar_banco()
            deleter_modelo_id(request.form.get("id"))  
        return redirect(url_for("modelos"))
    except:
        funcoes_gerais.registrar_log_erros("Erro ao deletar modelos")
        return redirect(url_for("erro")) 



"""
Erro geral
"""

#Erro em situacao de merlin
@app.route("/erro")
def erro():
    return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)



"""
Iniciando o programa
"""

#Executar o flask
if __name__ == "__main__":    
    #Colocada esses array na mao para evitar de um subir na frente do outro e estragar a apresentacao
    #CSS - geral
    css = ["./Static/css/reset.css", "./Static/css/bootstrap.css", "./Static/css/css_pessoal.css"]
    #JS - geral
    js = ["./Static/js/jquery-3.4.1.slim.min.js", "./Static/js/bootstrap.js", "./Static/js/popper.min.js", "./Static/js/js_pessoal.js"]
    #Páginas para movimentacao Web
    links_menu = ["extraidos", "classificador_paginas", "modelos", "testar_modelos", "destruir_banco", "destruir_modelos", "destruir_classificados", "versoes"]
    #Versao
    versao, icone = retorno_versao_icone()
    #Debug para analise - So para saber o que ta acontecendo
    #Liberado acesso a host externo
    app.run(host='0.0.0.0', debug=True)