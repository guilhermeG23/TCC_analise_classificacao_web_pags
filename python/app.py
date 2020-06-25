#Bibliotecas importadas
#Especifico
from flask import Flask, render_template, request, redirect, url_for
#Geral
import os
 
#Paginas com funcoes
import sqlite_funcoes
import Extrair_Pagina
import funcoes_analise
import funcoes_gerais

#Versoes

# Estavel -> Classes extras (Ruler, Avenger, Moon cancer, alterego, foreign, shilder)
# Alteracoes -> Classes de combate (Saber, Archer, Lancer)
# Instavel -> Classes de suporte (Rider, Caster, Assassins)
# Muitas alterações necessárias -> Está numa situação ruim -> Berserker

#versao = "Versão: 0.0.1 - Medusa - Rider"
#versao = "Versão: 0.0.2 - Euryale - Archer"
#versao = "Versão: 0.0.3 - Stheno - Assassins"
#versao = "Versão: 0.0.4 - Medusa - Lancer" 
#versao = "Versão: 0.0.5 - Gorgon - Avenger"
#versao = "Versão: 0.0.6 - Mash - Shielder"
#versao = "Versão: 0.0.7 - Atalanta - Archer"
#versao = "Versão: 0.0.8 - Atalanta Alter - Berserker"
#versao = "Versão: 0.0.9 - Okita - Saber"
#versao = "Versão: 0.1.0 - Nobu - Archer"
#versao = "Versão: 0.1.1 - Schath - Caster"
#versao = "Versão: 0.1.2 - Valkire - Lancer"
#versao = "Versão: 0.1.3 - Okita Alter - Alterego"
#versao = "Versão: 0.1.4 - Mordred Summer - Rider"
#versao = "Versão: 0.1.5 - Mama Raiko - Berserker"
versao = "Versão: 0.1.6 - Waver - Caster - 20/06/2020"

#Flask
#Iniciando o flask
app = Flask(__name__, static_folder='../Static', template_folder='../templates')

#Pagina princiapl
@app.route("/index")
@app.route("/")
def index():
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
        i = ''.join(i)
        momento = []
        for t in i.split("-"):
            if t != "":
                x = funcoes_gerais.limpeza_string_simples(sqlite_funcoes.selecionar_modelos_analise(t))
                momento.append([x, t])
            else:
                pass
        saida_aprovados.append(momento)

    #Retorno dos classificados de forma ajustada
    classificados = zip(classificados, saida_aprovados)

    #Titutlo pagina
    titulo="Index - Página principal"

    #Montar a pagina
    return render_template("index.html", versao=versao, css=css, js=js, titulo=titulo, links_menu=links_menu, dominios=dominios, classificados=classificados)

#Pagina dos já extraidos
@app.route("/extraidos")
def extraidos():
    #Criar banco caso tiver problemas
    sqlite_funcoes.criar_banco()
    #Mostrar pagina das paginas extraidas
    tabela = sqlite_funcoes.select_banco_extraidos()
    #Render a pagina
    return render_template("extraidos.html", versao=versao, css=css, js=js, titulo="Paginas extraidas", links_menu=links_menu, linhas=tabela)

#Pagina para selecionar os que serao classificados
@app.route("/classificador_paginas")
def classificador_paginas():
    #Criar o banco
    sqlite_funcoes.criar_banco()
    #Select das paginas para extracao
    tabela = sqlite_funcoes.select_banco_extraidos()
    #Render na pagina
    return render_template("classificar_paginas.html", versao=versao, css=css, titulo="Classificador de páginas", js=js, links_menu=links_menu, linhas=tabela)

#Pagina para selecionar os que serao classificados
@app.route("/modelos")
def modelos():
    #Criar o banco
    sqlite_funcoes.criar_banco()
    #Selecionar modelo
    tabela = sqlite_funcoes.select_modelos()
    #Render na pagina
    return render_template("modelos.html", versao=versao, css=css, js=js, titulo="Modelos", links_menu=links_menu, linhas=tabela)

#Criar CSV
@app.route("/criar_modelos", methods=['GET', 'POST'])
def criar_modelos():
    #Criar diretorio para os modelos
    criar_diretorio_modelos()
    #Confirma que a requisicao e post
    if request.method == "POST":
        #Requests post
        modelo_nome = request.form.get("modelo_nome")
        pesquisar_dominios = request.form.get("pesquisar_dominios")
        aprovacao_do_modelo = request.form.get("aprovacao_do_modelo")
        descricao_do_modelo = request.form.get("descricao")
        #Limpando o nome do modelos para nao dar merda
        modelo_nome = funcoes_gerais.limpeza_string_simples(modelo_nome)
        #Gerar CSV
        sqlite_funcoes.extracao_csv(modelo_nome, pesquisar_dominios)
        #Implementar aqui no meio a I.A
        sqlite_funcoes.gerar_modelos_csv()
        #Insert no banco de modelos
        sqlite_funcoes.insert_modelos_comparativos(modelo_nome, str(pesquisar_dominios), str(aprovacao_do_modelo), str(descricao_do_modelo))
        #Destruir modelos apos a analise da I.A
        sqlite_funcoes.destruir_modelos_csv()
    #Retorno    
    return redirect(url_for("modelos"))

#Criar modelo via TXT
@app.route("/criar_modelo_txt", methods=['GET', 'POST'])
def criar_modelo_txt():
    #Criar o diretorio modelo
    criar_diretorio_modelos()
    #Diretorio
    diretorio = "uploads"
    #Destruir diretorio
    funcoes_gerais.destruir_diretorio(diretorio)
    #Tipo de requisicao
    if request.method == "POST":
        #Requisita o arquivo
        file = request.files["txt_classifica"]
        #Cria a pastas
        funcoes_gerais.criar_diretorio(diretorio)
        #Faca o upload
        file.save(os.path.join(diretorio, file.filename))
        #Caminho do arquivo
        arquivo = "{}/{}".format(diretorio, file.filename)
        #Leia arquivo do upload
        with open(arquivo) as file:
            ler_arquivo = file.read()
            #Contador para este caso
            contador = 0
            #Ler as linhas do arquivo
            for i in ler_arquivo:
                #Url atual
                url = i
                #Capturar a pagina
                pagina = Extrair_Pagina.capturar_pagina_url(url)
                #Confirmar que esta extraindo a pagina e nao um false
                if pagina != False:
                    #Processa captura
                    processar_url(url, pagina)
                else:
                    #Ignora a passa para outro
                    pass
                contador = contador + 1
            ler_arquivo.close()
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
            modelo_nome = request.form.get("modelo_nome")
            aprovacao_do_modelo = request.form.get("aprovacao_do_modelo")
            descricao_do_modelo = request.form.get("descricao")
            #Limpando o nome do modelos para nao dar merda
            modelo_nome = funcoes_gerais.limpeza_string_simples(modelo_nome)
            #Gerar CSV
            sqlite_funcoes.extracao_csv(modelo_nome, pesquisar_dominios)
            #Implementar aqui no meio a I.A
            sqlite_funcoes.gerar_modelos_csv()
            #Insert no banco de modelos
            sqlite_funcoes.insert_modelos_comparativos(modelo_nome, str(pesquisar_dominios), str(aprovacao_do_modelo), str(descricao_do_modelo))
            #Destruir modelos apos a analise da I.A
            sqlite_funcoes.destruir_modelos_csv()
    #Caso der alguma coisa no post, passa reto
    else:
        pass
            
    #Retorno    
    return redirect(url_for("index"))

#Arrumar esse
#Pagina para testar os modelos com as classificações já feitas
@app.route("/testar_modelos")
def testar_modelos():
    criar_diretorio_modelos()
    sqlite_funcoes.criar_banco() 
    valores_modelos = sqlite_funcoes.select_modelos()
    return render_template("testador_modelos.html", versao=versao, css=css, js=js, titulo="Testar modelos", links_menu=links_menu, linhas=valores_modelos)

#Comparacao dos modelos com o url
@app.route("/processamento_modelos", methods=['GET', 'POST'])
def processamento_modelos():

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

        #Confirmar modelo parcial
        precisao_partial = request.form.get("precisao_partial")

        #Retorno no array para mostrar a saida
        retornos.append(tipo_analise_modelo)
        retornos.append(url)

        #Retorno do nomes dos modelo 
        saidas = modelos.split("-")
        saidona = []
        for saida in saidas:
            if len(saida) > 0:
                saidona.append(saida)
        saidas = saidona

        nome_modelos = []
        for i in saidas:
            for t in sqlite_funcoes.selecionar_modelos_aprovados(i):
                nome_modelos.append(t)
        retornos.append(nome_modelos)
        
        #Capturar página -> Fazer comunicação
        pagina = Extrair_Pagina.capturar_pagina_url(url)
        #Confirma se consegue capturar a pagina
        if pagina == False :
            #Deu errado volte para o index
            return redirect(url_for("testar_modelos"))
        else:
            #Confere o estado do URL
            if str(Extrair_Pagina.status_url(pagina)) == "200":
                #Extracao e entrada no banco
                processar_url(url, pagina)
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
                retornos.append(funcoes_analise.escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_partial))
                retornos.append(precisao_partial)
                #Destruir modelos de csv
                sqlite_funcoes.destruir_modelos_csv()


    #Insert nos classificados
    sqlite_funcoes.insert_pagina_classificada(url, modelos, retornos[3][1][8])

    #Retorno
    return redirect(url_for("exibir_teste_modelos"))

#Detalhes dos modelos
@app.route("/exibir_teste_modelos", methods=['GET', 'POST'])
def exibir_teste_modelos():
    criar_diretorio_modelos()
    if retornos:
        return render_template("resultado_analise_modelo.html", versao=versao, css=css, js=js, titulo="Resultado da analise", links_menu=links_menu, linhas=retornos)
    else:
        return redirect(url_for("index"))

#Detalhes dos modelos
@app.route("/detalhes_modelos", methods=['GET', 'POST'])
def detalhes_modelos():
    criar_diretorio_modelos()
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
            for t in str(i).split("-"):
                id_url = funcoes_gerais.limpeza_somente_valores(t)
                if len(id_url) > 0:
                    id_paginas.append(id_url)
                    paginas.append(sqlite_funcoes.select_paginas_url(funcoes_gerais.limpeza_somente_valores(id_url)))
        #Exibicao das paginas
        exibir_paginas = []
        for i in paginas:
            for t in i:
                exibir_paginas.append(funcoes_gerais.limpar_detalhes_modelos(t))

        #paginas e ID   
        exibir_paginas = zip(exibir_paginas, id_paginas)

        #Inicoando a pagina
        return render_template("detalhes_modelos.html", versao=versao, css=css, js=js, titulo="Detalhes do modelo", links_menu=links_menu, modelos_geral=modelos_geral, exibir_paginas=exibir_paginas)
    else:
        return redirect(url_for("modelos"))

#Detalhes dos links
@app.route("/detalhes", methods=['GET', 'POST'])
def detalhes():
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
        limpa = str(pagina_geral).split(",")
        data = funcoes_gerais.limpar_data(str(limpa[len(limpa)-1]))

        #Limpando as frases para serem apresentadas
        limpa = []
        for i in frases:
            limpa.append(funcoes_gerais.limpar_apresentacao_frases(str(i)))
        frases = limpa
    
        return render_template("detalhes.html", versao=versao, css=css, js=js, titulo="Detalhes da página extraida", links_menu=links_menu, pagina_geral=pagina_geral, data=data, frases=frases, palavras=palavras, tags=tags, imagens=imagens, videos=videos, audio=audio, links=links)
    else:
        return redirect(url_for("extraidos"))

#Processar a entrada de uma URL
def processar_url(url, pagina):
    #Abrir o banco
    sqlite_funcoes.criar_banco()
    #Trazer o estado da página
    pagina = Extrair_Pagina.capturar_pagina(pagina)
    #Titulo da página
    titulo = Extrair_Pagina.extrar_titulo(pagina)
    #Quantidade de linhas do html
    qtd_linhas_pag = Extrair_Pagina.qtd_linhas_pagina(pagina)
    #Idioma da página pelo titulo
    idioma = Extrair_Pagina.detectar_idioma(titulo)
    #Ips da pagina se possivel
    ip_pagina = Extrair_Pagina.endereco_ip_web(url)
    #Obter dominio da pagina
    dominio = Extrair_Pagina.obter_dominio(url)
    #Insert principal da pagina
    sqlite_funcoes.insert_banco_pagina(dominio, url, ip_pagina, titulo, qtd_linhas_pag, idioma, Extrair_Pagina.hora_atual_operacao())
    #Extrair ID da ultima página extraida
    id_pagina = sqlite_funcoes.select_ultimo_insert_paginas()
    for i in id_pagina:
        id_pagina = i
    id_pagina = id_pagina[0]
    #Todas as tags
    todas_tags = Extrair_Pagina.tags_pagina(pagina)
    tags = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.tags_pagina(pagina))
    #Todas as frases
    frases = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.frases_listadas(Extrair_Pagina.sem_repeticoes(Extrair_Pagina.buscar_lista(todas_tags)), pagina))
    #Todas as palavras do html
    palavras = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.palavras_listadas(Extrair_Pagina.sem_repeticoes(Extrair_Pagina.buscar_lista(todas_tags)), pagina))
    #Capturar imagens
    imagens = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.tags_imagens(pagina, dominio))
    #Links da pagina
    links = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.Extrair_links(pagina, dominio))
    #Links videos
    videos = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.Extrair_videos(pagina, dominio))
    #Link audios
    audios = Extrair_Pagina.quantificar_palavras(Extrair_Pagina.Extrair_audios(pagina, dominio))

    #Realizar cadastros
    tabelas = ["tags", tags, "frases", frases, "palavras", palavras, "imagens", imagens, "videos", videos, "audios", audios, "links", links]
    for tabela in range(0, len(tabelas), 2):
        sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, tabelas[int(tabela)], tabelas[int(tabela) + 1])

    #Retorno neutro após extracao
    return True

#Extrair página web e entender seus componentes
@app.route("/analisar_url", methods=['GET', 'POST'])
def analisar_url():
    if request.method == "POST":
        try:
            #Obter valor do input
            url = request.form.get("url")
            #Capturar página -> Fazer comunicação
            pagina = Extrair_Pagina.capturar_pagina_url(url)
            #Saber se existe o url
            if len(url) > 0:
                #Confirma se consegue capturar a pagina
                if pagina != False :
                    #Confere o estado do URL
                    if str(Extrair_Pagina.status_url(pagina)) == "200":
                        #Extracao e entrada no banco
                        processar_url(url, pagina)
                    else:
                        pass
                else:
                    pass
            else:
                pass
        except:
            pass

    #Deu errado volte para o index
    return redirect(url_for("index"))

#Analisar txt
#Extrair página web e entender seus componentes
@app.route("/analisar_txt", methods=['GET', 'POST'])
def analisar_txt():
    diretorio = "uploads"
    funcoes_gerais.destruir_diretorio(diretorio)
    if request.method == "POST":
        #Requisita o arquivo
        file = request.files["txt"]
        #Cria a pastas
        funcoes_gerais.criar_diretorio(diretorio)
        #Faca o upload
        file.save(os.path.join(diretorio, file.filename))
        #Caminho do arquivo
        arquivo = "{}/{}".format(diretorio, file.filename)
        #Leia arquivo do upload
        with open(arquivo) as file:
            ler_arquivo = file.read()
            #Ler as linhas do arquivo
            for i in ler_arquivo:
                #Url atual
                url = i
                #Capturar a pagina
                pagina = Extrair_Pagina.capturar_pagina_url(url)
                #Confirmar que esta extraindo a pagina e nao um false
                if pagina != False:
                    #Processa captura
                    processar_url(url, pagina)
                else:
                    #Ignora a passa para outro
                    pass
            ler_arquivo.close()
    #Escapando da analise do txt
    else:
        pass
    #Deleta uploads
    funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
    funcoes_gerais.destruir_diretorio(diretorio)
    #Retorno
    return redirect(url_for("index"))

#Funcao para deletar os modelos pelo ID
def deleter_modelo_id(entrada):
    #Buscandos os nomes dos mdoelos
    saida = sqlite_funcoes.selecionar_modelos_analise(entrada)
    modelos_deletar = []
    for i in saida:
        modelos_deletar.append(funcoes_gerais.limpeza_string_simples(i))
    #Apagandos os arquivos
    csvs = ["audios", "dominios", "frases", "imagens", "links", "paginas", "palavras", "tags", "videos"]
    for modelo in modelos_deletar:
        for csv in csvs:
            os.remove("modelos/{}-{}.csv".format(modelo, csv))
    #Realizar os deletes
    sqlite_funcoes.delete_modelo_banco(entrada)
    #Retorno verdadeiro
    return True

#Criar diretorio modelo para arquivos csv modelos
def criar_diretorio_modelos():
    funcoes_gerais.criar_diretorio("modelos")

#Deletar uma analise com base no ID
@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    if request.method == "POST":
        sqlite_funcoes.criar_banco()
        sqlite_funcoes.delete_banco(request.form.get("id"))
    return redirect(url_for("extraidos"))

#Destruit toda a base de dados
@app.route("/destruir_banco")
def destruir_banco():
    for id_modelo in sqlite_funcoes.selecionar_ids_modelos():
        deleter_modelo_id(funcoes_gerais.limpeza_somente_valores(id_modelo))
    sqlite_funcoes.destruir_modelos_classificados()
    sqlite_funcoes.destruir_banco_atual()
    return redirect(url_for("index"))

#Destruit toda a base de dados
@app.route("/destruir_modelos")
def destruir_modelos():
    sqlite_funcoes.destruir_modelos_classificados()
    return redirect(url_for("index"))

#Deletar modelos
@app.route("/deletar_modelos", methods=['GET', 'POST'])
def deletar_modelos():
    if request.method == "POST":
        sqlite_funcoes.criar_banco()
        deleter_modelo_id(request.form.get("id"))  
    return redirect(url_for("modelos"))

#Executar o flask
if __name__ == "__main__":
    #CSS - geral
    css = ["./Static/css/reset.css", "./Static/css/bootstrap.css", "./Static/css/css_pessoal.css"]
    #JS - geral
    js = ["./Static/js/jquery-3.4.1.slim.min.js", "./Static/js/bootstrap.js", "./Static/js/popper.min.js", "./Static/js/js_pessoal.js"]
    #Páginas para movimentacao Web
    links_menu = ["extraidos", "classificador_paginas", "modelos", "testar_modelos", "destruir_banco", "destruir_modelos"]
    #Retorno das analises
    retornos = []
    #Debug para analise
    app.run(debug=True)