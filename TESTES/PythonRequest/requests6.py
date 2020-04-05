import requests
import sys
from bs4 import BeautifulSoup
import re
from googletrans import Translator

#url = 'https://pt.wikipedia.org/wiki/Scikit-learn'
url = 'https://www.xvideos.com.br'

page = requests.get(url)
page.encoding = 'utf-8'

#Usando o analisar de paginas bs4
pagina = BeautifulSoup(page.text, 'html.parser')
pagina = str(pagina.get_text().lower())
pagina = re.sub('[^A-Za-z0-9]+', ' ', pagina)
pagina = pagina.split()

rankeado = []
rankeado = pagina

ja_listadas = []

translator = Translator()

for i in range(0, len(rankeado)):
    #print(translator.translate(rankeado[i]))
    atual = rankeado[i]
    if len(atual) > 1:
        interno = []
        interno.append(atual)
        interno.append(rankeado.count(atual))
        try:
            ja_listadas.index(interno)
        except ValueError:
            ja_listadas.append(interno)

def sortSecond(val): 
    return int(val[1])

ja_listadas.sort(key = sortSecond, reverse = True) 

for i in range(0, 20):
    print("Rank: {} - Palavra: {} - Qtd: {}".format((i+1), ja_listadas[i][0], ja_listadas[i][1]))

sys.exit()