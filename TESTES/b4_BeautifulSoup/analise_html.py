#Link: https://medium.com/horadecodar/como-fazer-webscraping-com-python-e-beautiful-soup-28a65eee2efd

from bs4 import BeautifulSoup
import requests

url = 'https://www.google.com/'

html = requests.get(url)

soup = BeautifulSoup(html.content, 'html.parser')

print(soup.get_text())