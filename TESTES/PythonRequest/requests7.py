import requests
import sys
from bs4 import BeautifulSoup
import re
from googletrans import Translator

#url = 'https://pt.wikipedia.org/wiki/Scikit-learn'
#url = 'https://www.xvideos.com.br'
url = 'https://www.xvideos.com/video54460567/comendo_a_baba_gostosa_e_peituda_com_forca_no_sofa'

page = requests.get(url)
page.encoding = 'utf-8'
#Usando o analisar de paginas bs4
pagina = BeautifulSoup(page.text, 'html.parser')

tags = ['title', 'p', 'h1', 'h2', 'h3', 'h4', 'a', 'span', 'li', 'footer']
ja_listadas_palavras = []
frases_inteiras = []
todas_palavras = []

for tag in tags:
    for i in range(1, len(pagina.find_all(tag))):
        frases_inteiras.append(pagina.find_all(tag)[i].get_text().lower().split())

for linha in frases_inteiras:
    for palavra in linha:
        todas_palavras.append(palavra)


for i in range(0, len(todas_palavras)):
    atual = todas_palavras[i]
    if len(atual) > 1:
        interno = []
        interno.append(atual)
        interno.append(todas_palavras.count(atual))
        try:
            ja_listadas_palavras.index(interno)
        except ValueError:
            ja_listadas_palavras.append(interno)
        
def sortSecond(val): 
    return int(val[1])

ja_listadas_palavras.sort(key = sortSecond, reverse = True) 

for i in range(0, 10):
    print("Rank: {} - Palavra: {} - Qtd: {}".format((i+1), ja_listadas_palavras[i][0], ja_listadas_palavras[i][1]))

for i in frases_inteiras:
    if len(i) > 1:
        #Listas as frases do site
        #print(i)
        pass

sys.exit()