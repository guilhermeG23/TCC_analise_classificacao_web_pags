#Lib para BS4
from bs4 import BeautifulSoup
#HTML de exemplo
html ="<!DOCTYPE html><p>Teste</p><h1>teste</h1><p>teste1</p></html>"
#Ler HTML
saida = BeautifulSoup(html, 'html.parser')
#Obter todos os P
print(saida.find_all('p'))