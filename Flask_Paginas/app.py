from flask import Flask, render_template, request, redirect, url_for
import sqlite_funcoes
import Analise_Pagina as anl

app = Flask(__name__)

@app.route("/index")
@app.route("/")
def index():
    sqlite_funcoes.criar_banco()
    return render_template("index.html")

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

@app.route("/analisar", methods=['GET', 'POST'])
def analisar():
    if request.method == "POST":
        url = request.form.get("url")
        sqlite_funcoes.criar_banco()
        #return redirect(url_for("analise"))

        pagina = anl.capturar_pagina_url(url)

        tags = anl.tags_pagina(pagina)
        todas_tags = anl.quantificar_palavras(tags)

        palavras = anl.quantificar_palavras(anl.palavras_listadas(anl.buscar_lista(todas_tags), pagina))

        dominio = anl.obter_dominio(url)

        #Forma preguiçosa de se fazer
        sqlite_funcoes.insert_banco(dominio, url, str(palavras), str(todas_tags), "1")

        return render_template("analise.html", url=url, dominio=dominio, tags=todas_tags, palavras=palavras)
    else:
        return redirect(url_for("index"))

@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    if request.method == "POST":
        sqlite_funcoes.criar_banco()
        entrada = request.form.get("id")
        sqlite_funcoes.delete_banco(entrada)
    return redirect(url_for("classificados"))

@app.route("/destruir")
def destruir():
    sqlite_funcoes.delete_banco_all()
    return redirect(url_for("classificados"))

if __name__ == "__main__":
    app.run(debug=True)