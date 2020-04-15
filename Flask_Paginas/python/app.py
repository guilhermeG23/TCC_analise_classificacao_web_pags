from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite_funcoes
import Extrair_Pagina as anl
import shutil
import Analise_modelo
import re


#versao = "Versão: 0.0.1 - Medusa - Rider"
#versao = "Versão: 0.0.2 - Euryale - Archer"
#versao = "Versão: 0.0.3 - Stheno - Assassins"
#versao = "Versão: 0.0.4 - Medusa - Lancer" 
#versao = "Versão: 0.0.5 - Gorgon - Avenger"
versao = "Versão: 0.0.6 - Mash - Shielder"

app = Flask(__name__, static_folder='../Static', template_folder='../templates')

#Pagina princiapl
@app.route("/index")
@app.route("/")
def index():
    sqlite_funcoes.criar_banco()
    dominios = sqlite_funcoes.select_count_domain().fetchall()
    return render_template("index.html", versao=versao, css=css, js=js, links_menu=links_menu, dominios=dominios)

#Pagina dos já extraidos
@app.route("/extraidos")
def extraidos():
    sqlite_funcoes.criar_banco()
    tabela = sqlite_funcoes.select_banco_extraidos().fetchall()
    return render_template("extraidos.html", versao=versao, css=css, js=js, links_menu=links_menu, linhas=tabela)

#Pagina para selecionar os que serao classificados
@app.route("/classificador_paginas")
def classificador_paginas():
    sqlite_funcoes.criar_banco()
    tabela = sqlite_funcoes.select_banco_extraidos().fetchall()
    return render_template("classificar_paginas.html", versao=versao, css=css, js=js, links_menu=links_menu, linhas=tabela)

#Criar CSV
@app.route("/criar_modelos", methods=['GET', 'POST'])
def criar_modelos():

    if request.method == "POST":

        #Requests post
        modelo_nome = request.form.get("modelo_nome")
        pesquisar_dominios = request.form.get("pesquisar_dominios")
        aprovacao_do_modelo = request.form.get("aprovacao_do_modelo")

        #Gerar CSV
        sqlite_funcoes.extracao_csv(modelo_nome, pesquisar_dominios)

        #Implementar aqui no meio a I.A
        Analise_modelo.acionar_IA_classificacao()

        #Destruir modelos apos a analise da I.A
        sqlite_funcoes.destruir_modelos_csv()

        return redirect(url_for("classificador_paginas"))

    else:
        return redirect(url_for("classificador_paginas"))


    sqlite_funcoes.criar_banco()
    tabela = sqlite_funcoes.select_banco_extraidos().fetchall()
    return render_template("classificar_paginas.html", versao=versao, css=css, js=js, links_menu=links_menu, linhas=tabela)

#Arrumar esse
#Pagina para testar os modelos com as classificações já feitas
@app.route("/testar_modelos")
def testar_modelos():
    sqlite_funcoes.criar_banco()
    tabela = sqlite_funcoes.select_banco_extraidos().fetchall()
    return render_template("testador_modelos.html", versao=versao, css=css, js=js, links_menu=links_menu, linhas="Colocar modelos")

#Comparacao dos modelos com o url
@app.route("/processamento_modelos", methods=['GET', 'POST'])
def processamento_modelos():
    if request.method == "POST":
        try:
            #Obter valor do input
            url = request.form.get("url")
            modelos = request.form.get("modelos")

            #Capturar página -> Fazer comunicação
            pagina = anl.capturar_pagina_url(url)

            if len(url) > 0:
                #Confirma se consegue capturar a pagina
                if pagina == False :
                        #Deu errado volte para o index
                        return redirect(url_for("testar_modelos"))
                else:
                    #Confere o estado do URL
                    if str(anl.status_url(pagina)) == "200":
    
                        #Capturar página -> Fazer comunicação
                        pagina = anl.capturar_pagina_url(url)
                            
                        #Extracao e entrada no banco
                        processar_url(url, pagina)

                        #Variaveis para o trabalho do csv
                        id_pesquisa = sqlite_funcoes.select_ultimo_insert_paginas()
                        for i in id_pesquisa:
                            #Limpar
                            i = re.sub('[^0-9]', '', str(i))
                            id_pesquisa = i
                                    
                        id_pesquisa = "-{}".format(id_pesquisa)
                        nome_temporario_para_processo ="1"

                        #Extracao da ultima pagina que fez entrada no banco
                        sqlite_funcoes.extracao_csv(nome_temporario_para_processo, id_pesquisa)

                        #Comparaca da extracao com os modelos fica bem aqui

                        #Destruir modelos de csv
                        sqlite_funcoes.destruir_modelos_csv()

                        return redirect(url_for("testar_modelos"))
        except:
            return redirect(url_for("testar_modelos"))
        
        return redirect(url_for("testar_modelos"))

    else:

        #Deu errado volte para o index
        return redirect(url_for("testar_modelos"))


#Detalhes dos links
@app.route("/detalhes", methods=['GET', 'POST'])
def detalhes():
    if request.method == "GET":
        sqlite_funcoes.criar_banco()
        identificador = request.args.get('t')
        pagina_geral = sqlite_funcoes.select_banco_paginas(identificador).fetchall()

        frases = sqlite_funcoes.select_varios_bancos(identificador, "frases").fetchall()
        palavras = sqlite_funcoes.select_varios_bancos(identificador, "palavras").fetchall()
        tags = sqlite_funcoes.select_varios_bancos(identificador, "tags").fetchall()
        imagens = sqlite_funcoes.select_varios_bancos(identificador, "imagens").fetchall()
        videos = sqlite_funcoes.select_varios_bancos(identificador, "videos").fetchall()
        audio = sqlite_funcoes.select_varios_bancos(identificador, "audio").fetchall()
        links = sqlite_funcoes.select_varios_bancos(identificador, "links").fetchall()

        return render_template("detalhes.html", versao=versao, css=css, js=js, links_menu=links_menu, pagina_geral=pagina_geral, frases=frases, palavras=palavras, tags=tags, imagens=imagens, videos=videos, audio=audio, links=links)
    else:
        return redirect(url_for("extraidos"))

#Processar a entrada de uma URL
def processar_url(url, pagina):
    #Abrir o banco
    sqlite_funcoes.criar_banco()
    #Trazer o estado da página
    pagina = anl.capturar_pagina(pagina)
    #Titulo da página
    titulo = anl.extrar_titulo(pagina)
    #Quantidade de linhas do html
    qtd_linhas_pag = anl.qtd_linhas_pagina(pagina)
    #Idioma da página pelo titulo
    idioma = anl.detectar_idioma(titulo)
    #Obter dominio da pagina
    dominio = anl.obter_dominio(url)
    #Insert principal da pagina
    sqlite_funcoes.insert_banco_pagina(dominio, url, titulo, qtd_linhas_pag, idioma)
    #Extrair ID da ultima página extraida
    id_pagina = sqlite_funcoes.select_ultimo_insert_paginas()
    for i in id_pagina:
        id_pagina = i
    id_pagina = id_pagina[0]
    #Todas as tags
    todas_tags = anl.tags_pagina(pagina)
    tags = anl.quantificar_palavras(anl.tags_pagina(pagina))
    #Todas as frases
    frases = anl.quantificar_palavras(anl.frases_listadas(anl.sem_repeticoes(anl.buscar_lista(todas_tags)), pagina))
    #Todas as palavras do html
    palavras = anl.quantificar_palavras(anl.palavras_listadas(anl.sem_repeticoes(anl.buscar_lista(todas_tags)), pagina))
    #Capturar imagens
    imagens = anl.quantificar_palavras(anl.tags_imagens(pagina, dominio))
    #Links da pagina
    links = anl.quantificar_palavras(anl.Extrair_links(pagina, dominio))
    #Links videos
    videos = anl.quantificar_palavras(anl.Extrair_videos(pagina, dominio))
    #Link audios
    audios = anl.quantificar_palavras(anl.Extrair_audios(pagina, dominio))

    #Todos os tipos de tags da pagina
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "tags", tags)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "frases", frases)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "palavras", palavras)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "imagens", imagens)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "videos", videos)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "audio", audios)
    sqlite_funcoes.insert_geral_para_tabelas_secudarias(id_pagina, "links", links)

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
            pagina = anl.capturar_pagina_url(url)

            if len(url) > 0:
                #Confirma se consegue capturar a pagina
                if pagina == False :
                        #Deu errado volte para o index
                        return redirect(url_for("index"))
                else:
                    #Confere o estado do URL
                    if str(anl.status_url(pagina)) == "200":
                        #Extracao e entrada no banco
                        processar_url(url, pagina)
                        #Mostrar a pagina de analise
                        #return render_template("index.html")
                        return redirect(url_for("index"))
                    else:
                        #Deu errado volte para o index
                        return redirect(url_for("index"))
        except:
            return redirect(url_for("index"))
        
        return redirect(url_for("index"))

    else:

        #Deu errado volte para o index
        return redirect(url_for("index"))

#Analisar txt
#Extrair página web e entender seus componentes
@app.route("/analisar_txt", methods=['GET', 'POST'])
def analisar_txt():
    if request.method == "POST":
        
        #Requisita o arquivo
        file = request.files["txt"]
        
        #Cria a pastas
        os.mkdir("uploads")

        file.save(os.path.join("uploads", file.filename))

        arquivo = "uploads/{}".format(file.filename)

        ler_arquivo = open(arquivo, "r")

        for i in ler_arquivo:
            url = i
            pagina = anl.capturar_pagina_url(url)
            processar_url(url, pagina)
        
        ler_arquivo.close()

        shutil.rmtree("uploads")

        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


#Deletar uma analise com base no ID
@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    if request.method == "POST":
        sqlite_funcoes.criar_banco()
        entrada = request.form.get("id")
        sqlite_funcoes.delete_banco(entrada)
    return redirect(url_for("extraidos"))

#Destruit toda a base de dados
@app.route("/destruir")
def destruir():
    sqlite_funcoes.destruir_banco_atual()
    return redirect(url_for("index"))

#Executar o flask
if __name__ == "__main__":
    css = ["./Static/css/reset.css", "./Static/css/bootstrap.css", "./Static/css/css_pessoal.css"]
    js = ["./Static/js/jquery-3.4.1.slim.min.js", "./Static/js/bootstrap.js", "./Static/js/popper.min.js", "./Static/js/js_pessoal.js"]
    links_menu = ["extraidos", "classificador_paginas", "testar_modelos", "destruir"]
    app.run(debug=True)