import requests
import sys

#page = requests.get('https://wiki.python.org.br/ManipulandoStringsComPython')
page = requests.get('https://google.com/')
page.encoding = 'utf-8'
pagina = str(page.text)
pagina = pagina.split()

rankeado = []
rankeado = pagina

ja_listadas = [['', 0]]

for i in range(0, len(rankeado)):
    atual = rankeado[i]
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

for i in range(0, 10):
    print(ja_listadas[i])

sys.exit()