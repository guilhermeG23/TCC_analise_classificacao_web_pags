def tags_pagina(pagina):
    from bs4 import BeautifulSoup
    tags = []
    #Todas as tags do url
    for tag in pagina.find_all(True):
        tags.append(tag.name)

    return tags