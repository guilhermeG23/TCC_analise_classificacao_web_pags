import requests
from bs4 import BeautifulSoup

url = 'https://www.xvideos.com/'
page = requests.get(url, timeout=10, verify=False)
pagina = BeautifulSoup(page.text, 'html.parser')

#Estruturar a pagina
#print(pagina.prettify())

tags = []
#Todas as tags do url
for tag in pagina.find_all(True):
    tags.append(tag.name)

ja_listadas_palavras = []
for i in range(0, len(tags)):
    atual = tags[i]
    interno = []
    interno.append(atual)
    interno.append(tags.count(atual))
    try:
        ja_listadas_palavras.index(interno)
    except ValueError:
        ja_listadas_palavras.append(interno)

    def sortSecond(val): 
        return int(val[1])

ja_listadas_palavras.sort(key = sortSecond, reverse = True) 

for i in range(0, len(ja_listadas_palavras)):
    print("Rank: {} - Palavra: {} - Qtd: {}".format((i+1), ja_listadas_palavras[i][0], ja_listadas_palavras[i][1]))

print(ja_listadas_palavras)
"""
for link in pagina.find_all('a'):
    print(link.get('href'))

for link in pagina.find_all('div'):
    print(link.get_text())

for link in pagina.find_all('img'):
    print(link)
"""