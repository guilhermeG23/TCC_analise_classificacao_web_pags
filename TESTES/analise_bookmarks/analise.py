import requests
from bs4 import BeautifulSoup

url = 'https://www.google.com/search?client=firefox-b-d&q=metaploit+flask'
page = requests.get(url, timeout=10, verify=False)
pagina = BeautifulSoup(page.text, 'html.parser')
pagina = pagina.prettify()
contador = 0
for i in pagina:
    contador = contador + 1
print(contador)