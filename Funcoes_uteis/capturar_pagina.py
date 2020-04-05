#Retorno da página Web
def capturar_pagina_url(url):
    
    import requests
    from bs4 import BeautifulSoup
    
    page = requests.get(url, timeout=10, verify=False)
    pagina = BeautifulSoup(page.text, 'html.parser')
    return pagina