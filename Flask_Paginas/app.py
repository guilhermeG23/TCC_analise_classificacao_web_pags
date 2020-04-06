from flask import Flask, render_template, request, redirect, url_for
import sqlite_funcoes
import Extrair_Pagina as anl

app = Flask(__name__)

@app.route("/index")
@app.route("/")
def index():
    sqlite_funcoes.criar_banco()
    dominios = sqlite_funcoes.select_count_domain()
    return render_template("index.html", dominios=dominios)

@app.route("/teste")
def teste():
    sqlite_funcoes.criar_banco()
    return redirect(url_for("index"))

@app.route("/classificados")
def classificados():
    sqlite_funcoes.criar_banco()
    tabela = sqlite_funcoes.select_banco_all().fetchall()
    return render_template("classificados.html", linhas=tabela)

@app.route("/detalhes", methods=['GET', 'POST'])
def detalhes():
    if request.method == "GET":
        sqlite_funcoes.criar_banco()
        identificador = request.args.get('t')
        tabela = sqlite_funcoes.select_banco(identificador).fetchall()
        return render_template("detalhes.html", linhas=tabela)
    else:
        return redirect(url_for("classificados"))

#Extrair página web e entender seus componentes
@app.route("/analisar", methods=['GET', 'POST'])
def analisar():
    if request.method == "POST":

        #Obter valor do input
        url = request.form.get("url")

        #Abrir o banco
        sqlite_funcoes.criar_banco()

        #Capturar página
        pagina = anl.capturar_pagina_url(url)

        #Quantidade de linhas do html
        qtd_linhas_pag = anl.qtd_linhas_pagina(pagina)
        
        #Obter dominio da pagina
        dominio = anl.obter_dominio(url)

        #Capturar imagens
        imagens = anl.tags_imagens(pagina, dominio)

        #Todos os tipos de tags da pagina
        tags = anl.tags_pagina(pagina)
        
        #Todas as tags do html
        todas_tags = anl.quantificar_palavras(tags)

        #Todas as frases
        todas_frases = anl.quantificar_palavras(anl.frases_listadas(anl.buscar_lista(todas_tags), pagina))

        #Todas as palavras do html
        palavras = anl.quantificar_palavras(anl.palavras_listadas(anl.buscar_lista(todas_tags), pagina))

        #Forma preguiçosa de se fazer
        sqlite_funcoes.insert_banco(dominio, url, str(todas_frases), str(palavras), str(todas_tags), str(imagens), qtd_linhas_pag, "1")

        #Mostrar a pagina de analise
        return render_template("analise.html", url=url, dominio=dominio, tags=todas_tags, palavras=palavras)
    else:

        #Deu errado volte para o index
        return redirect(url_for("index"))

#Deletar uma analise com base no ID
@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    if request.method == "POST":
        sqlite_funcoes.criar_banco()
        entrada = request.form.get("id")
        sqlite_funcoes.delete_banco(entrada)
    return redirect(url_for("classificados"))

#Destruit toda a base de dados
@app.route("/destruir")
def destruir():
    sqlite_funcoes.delete_banco_all()
    return redirect(url_for("classificados"))

#Executar o flask
if __name__ == "__main__":
    app.run(debug=True)