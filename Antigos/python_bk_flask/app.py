#Bibliotecas importadas
#Especifico
from flask import Flask, render_template, request, redirect, url_for
 
#Outros arquivos python que contem as funcoes
import funcoes_sql
import funcoes_extrair
import funcoes_analise
import funcoes_gerais

#Global
#Retorno das analises
global retornos
retornos = []


"""
Funcoes
"""

#Criar diretorio modelo para arquivos csv modelos
def criar_diretorio_modelos():
    funcoes_gerais.criar_diretorio("modelos")

#Funcao para cirar os modelos
def funcao_criar_modelos(modelo_nome, pesquisar_dominios, aprovacao_do_modelo, descricao_do_modelo):
    #Nome do modelo reformado
    modelo_nome = funcoes_gerais.limpeza_string_com_adicionais(modelo_nome)
    #Gerar CSV
    funcoes_sql.extracao_csv(modelo_nome, pesquisar_dominios)
    #Implementar aqui no meio a I.A
    funcoes_sql.gerar_modelos_csv()
    #Insert no banco de modelos
    funcoes_sql.insert_modelos_comparativos(modelo_nome, funcoes_gerais.converte_string(pesquisar_dominios), funcoes_gerais.converte_string(aprovacao_do_modelo), funcoes_gerais.converte_string(descricao_do_modelo))
    #Destruir modelos apos a analise da I.A
    funcoes_sql.destruir_modelos_csv()
    #Retorno normal
    return True

#Registrar pagina
def registar_url(url, pagina):
    if funcoes_gerais.ler_quantidade_variavel(url) > 0:
    #Confirma se consegue capturar a pagina
        if pagina != False :
            #Confere o estado do URL
            if funcoes_gerais.converte_string(funcoes_extrair.status_url(pagina)) == "200":
                #Extracao e entrada no banco
                processar_url(url, pagina)
    return True

#Processar a entrada de uma URL
def processar_url(url, pagina):
    #Abrir o banco
    funcoes_sql.criar_banco()
    #Trazer o estado da página
    pagina = funcoes_extrair.capturar_pagina(pagina)
    #Titulo da página
    titulo = funcoes_extrair.extrar_titulo(pagina)
    #Quantidade de linhas do html
    qtd_linhas_pag = funcoes_extrair.qtd_linhas_pagina(pagina)
    #Idioma da página pelo titulo
    idioma = funcoes_extrair.detectar_idioma(titulo)
    #Ips da pagina se possivel
    ip_pagina = funcoes_extrair.endereco_ip_web(url)
    #Obter dominio da pagina
    dominio = funcoes_extrair.obter_dominio(url)
    #Insert principal da pagina
    funcoes_sql.insert_banco_pagina(dominio, url, ip_pagina, titulo, qtd_linhas_pag, idioma, funcoes_extrair.hora_atual_operacao())
    #Extrair ID da ultima página extraida
    id_pagina = funcoes_sql.select_ultimo_insert_paginas()
    for i in id_pagina:
        id_pagina = i
    id_pagina = id_pagina[0]
    #Todas as tags
    todas_tags = funcoes_extrair.tags_pagina(pagina)
    tags = funcoes_extrair.quantificar_palavras(funcoes_extrair.tags_pagina(pagina))
    #Todas as frases
    frases = funcoes_extrair.quantificar_palavras(funcoes_extrair.frases_listadas(funcoes_gerais.limpar_repetidos_array(funcoes_extrair.buscar_lista(todas_tags)), pagina))
    #Todas as palavras do html
    palavras = funcoes_extrair.quantificar_palavras(funcoes_extrair.palavras_listadas(funcoes_gerais.limpar_repetidos_array(funcoes_extrair.buscar_lista(todas_tags)), pagina))
    #Capturar imagens
    imagens = funcoes_extrair.quantificar_palavras(funcoes_extrair.tags_imagens(pagina, dominio))
    #Links da pagina
    links = funcoes_extrair.quantificar_palavras(funcoes_extrair.Extrair_links(pagina, dominio))
    #Links videos
    videos = funcoes_extrair.quantificar_palavras(funcoes_extrair.Extrair_videos(pagina, dominio))
    #Link audios
    audios = funcoes_extrair.quantificar_palavras(funcoes_extrair.Extrair_audios(pagina, dominio))
    #Realizar cadastros
    tabelas = ["tags", tags, "frases", frases, "palavras", palavras, "imagens", imagens, "videos", videos, "audios", audios, "links", links]
    for tabela in range(0, funcoes_gerais.ler_quantidade_variavel(tabelas), 2):
        funcoes_sql.insert_geral_para_tabelas_secudarias(id_pagina, tabelas[funcoes_gerais.converte_inteiro(tabela)], tabelas[funcoes_gerais.converte_inteiro(tabela) + 1])

    pagina = funcoes_gerais.converte_string(pagina)

    #Registrar página
    funcoes_gerais.criar_diretorio("paginas")
    gravar_pagina = "paginas/{}.txt".format(id_pagina)
    with open(gravar_pagina, "w+") as arquivo:   
        arquivo.write("{}".format(pagina))
    arquivo.close()
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
    saida = funcoes_sql.selecionar_modelos_analise(entrada)
    modelos_deletar = []
    for i in saida:
        modelos_deletar.append(funcoes_gerais.limpeza_string_simples(i))
    #Deletar valor em classificados
    funcoes_sql.deletar_url_classificada("%-{}-%".format(entrada))
    #Apagandos os arquivos
    csvs = ["audios", "dominios", "frases", "imagens", "links", "paginas", "palavras", "tags", "videos"]
    for modelo in modelos_deletar:
        for csv in csvs:
            funcoes_gerais.deletar_arquivo("modelos/{}-{}.csv".format(modelo, csv))
    #Realizar os deletes
    funcoes_sql.delete_modelo_banco(entrada)
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
        funcoes_sql.criar_banco()
        #Fazer requisicao de dominios para apresentacao no index
        dominios = funcoes_sql.select_count_domain()
        #Classificados
        classificados = funcoes_sql.select_count_classificados()
        aprovacoes = funcoes_sql.select_count_classificados_somente_id()
        #Puxandos os nomes dos modelos
        saida_aprovados = []
        for i in aprovacoes:
            momento = []
            for t in funcoes_gerais.split_geral(funcoes_gerais.juntar_join(i), "-"):
                if t != "":
                    x = funcoes_gerais.limpeza_string_simples(funcoes_sql.selecionar_modelos_analise(t))
                    momento.append([x, t])
                else:
                    pass
            saida_aprovados.append(momento)

        #Retorno dos classificados de forma ajustada
        classificados = funcoes_gerais.zip_arrays(classificados, saida_aprovados)
        #Montar a pagina
        return render_template("index.html", versao=versao, css=css, js=js, titulo="Index - Página principal", icone=icone, links_menu=links_menu, dominios=dominios, classificados=classificados)
    except Exception as erro:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar no index - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Pagina dos já extraidos
@app.route("/extraidos")
def extraidos():
    #try:
    #Criar banco caso tiver problemas
    funcoes_sql.criar_banco()
    #Mostrar pagina das paginas extraidas
    tabela = funcoes_sql.select_banco_extraidos()
    #Render a pagina
    return render_template("extraidos.html", versao=versao, css=css, js=js, titulo="Paginas extraidas", icone=icone, links_menu=links_menu, linhas=tabela)

#Pagina para selecionar os que serao classificados
@app.route("/classificador_paginas")
def classificador_paginas():
    try:
        #Criar o banco
        funcoes_sql.criar_banco()
        #Select das paginas para extracao
        tabela = funcoes_sql.select_banco_extraidos()
        #Render na pagina
        return render_template("classificar_paginas.html", versao=versao, css=css, titulo="Classificador de páginas", icone=icone, js=js, links_menu=links_menu, linhas=tabela)
    except Exception as erro:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar na pagina de classificacao - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Pagina para selecionar os que serao classificados
@app.route("/modelos")
def modelos():
    try:
        #Criar o banco
        funcoes_sql.criar_banco()
        #Selecionar modelo
        tabela = funcoes_sql.select_modelos()
        #Render na pagina
        return render_template("modelos.html", versao=versao, css=css, js=js, titulo="Modelos", icone=icone, links_menu=links_menu, linhas=tabela)
    except Exception as erro:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar na pagina de modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Arrumar esse
#Pagina para testar os modelos com as classificações já feitas
@app.route("/testar_modelos")
def testar_modelos():
    try:
        criar_diretorio_modelos()
        funcoes_sql.criar_banco() 
        valores_modelos = funcoes_sql.select_modelos()
        return render_template("testador_modelos.html", versao=versao, css=css, js=js, titulo="Testar modelos", icone=icone, links_menu=links_menu, linhas=valores_modelos)
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao criar testador de modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Mostrar as versoes do software
@app.route("/versoes")
def versoes():
    try:
        return render_template("versoes.html", versao=versao, css=css, js=js, titulo="Versões", icone=icone, links_menu=links_menu, versoes=funcoes_gerais.todas_versoes_software())
    except Exception as erro:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao entrar em versoes - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)



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
    except Exception as erro:
        #log de erro
        funcoes_gerais.registrar_log_erros("Erro ao criar modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

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
                    pagina = funcoes_extrair.capturar_pagina_url(url)
                    #Confirmar que esta extraindo a pagina e nao um false
                    try:
                        registar_url(url, pagina)
                        #Contador
                        contador = contador + 1
                    except Exception as erro:
                        funcoes_gerais.registrar_log_erros("Erro ao registrar alguma URL - {}".format(erro))
            #Fechando o txt
            saida.close()
            #Deleta uploads
            funcoes_gerais.eliminar_conteudo_diretorio(diretorio)
            funcoes_gerais.destruir_diretorio(diretorio)
            #Jeito que deve ser
            #-123-122
            #Puxando os ultimos valores inseridos com uso do limitador para criar a chamada
            valores = funcoes_sql.select_paginas_limit(contador)
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
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao criar modelo txt - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Comparacao dos modelos com o url
@app.route("/processamento_modelos", methods=['GET', 'POST'])
def processamento_modelos():
    try:
        #Destruir csv por seguranca
        funcoes_sql.destruir_modelos_csv()
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

            #Feito na mão para ser rápido
            if tipo_analise_modelo == "uso_total_fuzzy":
                descricao_analise_modelo = "Processamento de texto via Fuzzy"
            elif tipo_analise_modelo == "uso_total_processamento_imagens":
                descricao_analise_modelo = "Processamento de imagens com predição"
            elif tipo_analise_modelo == "predicao_processamento_banco_palavras":
                descricao_analise_modelo = "Processamento de texto via TF-IDF"
            else:
                descricao_analise_modelo = "Erro ao listar"

            #Retorno no array para mostrar a saida
            retornos.append(descricao_analise_modelo)
            retornos.append(url)

            #Retorno do nomes dos modelo 
            saidas = modelos.split("-")
            saidona = []
            for saida in saidas:
                if funcoes_gerais.ler_quantidade_variavel(saida) > 0:
                    saidona.append(saida)
            saidas = saidona

            nome_modelos = []
            for i in saidas:
                for t in funcoes_sql.selecionar_modelos_aprovados(i):
                    nome_modelos.append(t)
            retornos.append(nome_modelos)
            
            #Capturar página -> Fazer comunicação
            pagina = funcoes_extrair.capturar_pagina_url(url)
            #Confirma se consegue capturar a pagina
            if pagina == False :
                #Deu errado volte para o index
                return redirect(url_for("testar_modelos"))
            else:
                #Confere o estado do URL
                if funcoes_gerais.converte_string(funcoes_extrair.status_url(pagina)) == "200":
                    try:
                        #Extracao e entrada no banco
                        registar_url(url, pagina)
                        #Variaveis para o trabalho do csv
                        id_pesquisa = funcoes_sql.select_ultimo_insert_paginas()
                        for i in id_pesquisa:
                            #Limpar
                            i = funcoes_gerais.limpeza_somente_valores(i)
                        id_pesquisa = i
                        id_pesquisa = "-{}".format(id_pesquisa)
                        nome_temporario_para_processo ="modelotemporario"
                        #Extracao da ultima pagina que fez entrada no banco
                        funcoes_sql.extracao_csv(nome_temporario_para_processo, id_pesquisa)

                        #Comparaca da extracao com os modelos fica bem aqui
                        retornos.append(funcoes_analise.escolher_analise(tipo_analise_modelo, nome_temporario_para_processo, modelos, precisao_semente, cinza))
                        
                        #Ajustando a saida da semente na interface
                        if tipo_analise_modelo != "uso_total_processamento_imagens":
                            precisao_semente = 0

                        retornos.append(precisao_semente)
                        #Destruir modelos de csv
                        funcoes_sql.destruir_modelos_csv()
                        #Insert nos classificados
                        funcoes_sql.insert_pagina_classificada(url, modelos, tipo_analise_modelo, retornos[3][2], precisao_semente, retornos[3][1][8])
                    except Exception as erro:
                        funcoes_gerais.registrar_log_erros("Erro ao processador modelos - {}".format(erro))
        #Retorno
        return redirect(url_for("exibir_teste_modelos"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro durante o processamento de modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)
    
#Detalhes dos modelos
@app.route("/exibir_teste_modelos", methods=['GET', 'POST'])
def exibir_teste_modelos():
    try:
        criar_diretorio_modelos()
        if retornos:
            return render_template("resultado_analise_modelo.html", versao=versao, css=css, js=js, titulo="Resultado da analise", icone=icone, links_menu=links_menu, linhas=retornos)
        else:
            return redirect(url_for("index"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao exibir teste de modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Detalhes dos modelos
@app.route("/detalhes_modelos", methods=['GET', 'POST'])
def detalhes_modelos():
    try:
        criar_diretorio_modelos()
        #log
        if request.method == "GET":
            
            #Funcao de seguranca para o banco
            funcoes_sql.criar_banco()
            #Entrada para pesquisa de detalhes
            identificador = request.args.get('id_modelo')
            #Select para demonstrar os detalhes
            modelos_geral = funcoes_sql.selecionar_modelos_detalhes(identificador)
            paginas_contidas = funcoes_sql.selecionar_modelos_detalhes_paginas(identificador)
            paginas = []
            id_paginas = []
            #Buscando paginas que compoem o modelo
            for i in paginas_contidas:
                for t in funcoes_gerais.converte_string(i).split("-"):
                    id_url = funcoes_gerais.limpeza_somente_valores(t)
                    if funcoes_gerais.ler_quantidade_variavel(id_url) > 0:
                        id_paginas.append(id_url)
                        paginas.append(funcoes_sql.select_paginas_url(funcoes_gerais.limpeza_somente_valores(id_url)))
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
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao exibir detalhes de modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Detalhes dos links
@app.route("/detalhes_pagina", methods=['GET', 'POST'])
def detalhes_pagina():
    try:
        if request.method == "GET":
            #Criar o banco caso nao exista
            funcoes_sql.criar_banco()
            #Capturando o valor
            identificador = request.args.get('id_pagina')

            #Selects necessarios para mostrar o detalhamento
            pagina_geral = funcoes_sql.select_banco_paginas(identificador)
            frases = funcoes_sql.select_varios_bancos(identificador, "frases")
            palavras = funcoes_sql.select_varios_bancos(identificador, "palavras")
            tags = funcoes_sql.select_varios_bancos(identificador, "tags")
            imagens = funcoes_sql.select_varios_bancos(identificador, "imagens")
            videos = funcoes_sql.select_varios_bancos(identificador, "videos")
            audio = funcoes_sql.select_varios_bancos(identificador, "audios")
            links = funcoes_sql.select_varios_bancos(identificador, "links")

            #Limpando data para apresentacao
            limpa = funcoes_gerais.split_geral(funcoes_gerais.converte_string(pagina_geral), ",")
            data = funcoes_gerais.limpar_data(funcoes_gerais.converte_string(limpa[funcoes_gerais.ler_quantidade_variavel(limpa)-1]))

            #Limpando as frases para serem apresentadas
            limpa = []
            for i in frases:
                limpa.append(funcoes_gerais.limpar_apresentacao_frases(funcoes_gerais.converte_string(i)))
            frases = limpa

            codigo = funcoes_gerais.ler_pagina(identificador)

            return render_template("detalhes_pagina.html", versao=versao, css=css, js=js, titulo="Detalhes da página extraida", icone=icone, links_menu=links_menu, pagina_geral=pagina_geral, data=data, frases=frases, palavras=palavras, tags=tags, imagens=imagens, videos=videos, audio=audio, links=links, codigo=codigo)
        else:
            return redirect(url_for("extraidos"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao exibir delathes - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

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
                pagina = funcoes_extrair.capturar_pagina_url(url)
                #Saber se existe o url
                registar_url(url, pagina)
            except Exception as erro:
                funcoes_gerais.registrar_log_erros("Erro ao analisar uma URL - {}".format(erro))
        #Retorno
        return redirect(url_for("index"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Maiores problemas ao analisar uma URL - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

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
                    pagina = funcoes_extrair.capturar_pagina_url(url)
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
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro durante operacao da analise de txt - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)



"""
Funcoes de deletar
"""

#Deletar uma analise com base no ID
@app.route("/deletar", methods=['GET', 'POST'])
def deletar():
    try:
        if request.method == "POST":
            valor = request.form.get("id")
            funcoes_sql.criar_banco()
            funcoes_sql.delete_banco(valor)
            funcoes_gerais.deletar_arquivo("paginas/{}.txt".format(valor))
        return redirect(url_for("extraidos"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao deletar conteudo do banco - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Destruit toda a base de dados
@app.route("/destruir_banco")
def destruir_banco():
    try:
        funcoes_gerais.eliminar_conteudo_diretorio('modelos')
        funcoes_gerais.eliminar_conteudo_diretorio('paginas')
        funcoes_sql.destruir_modelos_classificados()
        funcoes_sql.destruir_banco_atual()
        return redirect(url_for("index"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao destruir o banco - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Destruit toda a base de dados
@app.route("/destruir_modelos")
def destruir_modelos():
    try:
        funcoes_sql.destruir_modelos_classificados()
        funcoes_gerais.eliminar_conteudo_diretorio('modelos')
        return redirect(url_for("index"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro oa destruir modelos - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Destruit toda a base de dados
@app.route("/destruir_classificados")
def destruir_classificados():
    try:
        funcoes_sql.deletar_classificada()
        return redirect(url_for("index"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao destruir classificados - {}".format(erro))
        return render_template("erro.html", versao=versao, css=css, js=js, titulo="Erro", icone=icone, links_menu=links_menu)

#Deletar modelos
@app.route("/deletar_modelos", methods=['GET', 'POST'])
def deletar_modelos():
    try:
        if request.method == "POST":
            funcoes_sql.criar_banco()
            deleter_modelo_id(request.form.get("id"))  
        return redirect(url_for("modelos"))
    except Exception as erro:
        funcoes_gerais.registrar_log_erros("Erro ao deletar modelos - {}".format(erro))
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
    versao, icone = funcoes_gerais.retorno_versao_icone()
    #versao, icone = 
    #Debug para analise - So para saber o que ta acontecendo
    #Liberado acesso a host externo
    app.run(host='0.0.0.0', debug=True)