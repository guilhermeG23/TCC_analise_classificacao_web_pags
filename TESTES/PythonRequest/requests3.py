import requests
import sys

#page = requests.get('https://www.google.com/', verify=False)
page = requests.get('https://wiki.python.org.br/ManipulandoStringsComPython')
page.encoding = 'utf-8'
print(page.status_code)

pagina = str(page.text)
pagina = pagina.split()
#print(pagina)
#print(len(pagina))

rankeado = []
rankeado = pagina
#print(rankeado)

#sys.exit()

"""
for i in range(0, len(pagina)):
    if rankeado.index(pagina[i]) == True:
        print(rankeado.index(pagina[i]))
    else:
    rankeado.append(pagina[i])
    #rankeado.append(pagina[i])
    #print("Palavra: {} - Posição: {}".format(pagina[i], rankeado.index(pagina[i])))
"""
"""
for i in range(0, len(pagina)):
    rankeado.append(pagina[i])
"""
ja_listadas = ['']

#Ajudou muito aqui: https://docs.python.org/3/tutorial/errors.html
for i in range(0, len(rankeado)):
    try:
        ja_listadas.index(rankeado[i])
    except ValueError:
        atual = rankeado[i]
        ja_listadas.append(atual)
        ja_listadas.append(rankeado.count(atual))

print(ja_listadas)

"""
for i in range(0, len(rankeado)):
    try:
        print(ja_listadas.index(rankeado[i]))
    except ValueError:
        print("valor nao encontrado")
    

#    if int(ja_listadas.index(rankeado[i])) == 0:
#        ja_listadas.append(rankeado[i])
#        print(rankeado.count(rankeado[i]))
"""

"""
for i in range(0, len(rankeado)):
    print(ja_listadas.index(rankeado[i]))
"""
"""
    if ja_listadas.index(rankeado[i]) == 0:
        ja_listadas.append(rankeado[i])
        print(rankeado.count(rankeado[i]))
"""


#print(len(rankeado))

"""
for i in range(0, len(rankeado)):
    print("Palavra: {} - Posição: {}".format(pagina[i], rankeado.index(pagina[i])))
"""
#print(rankeado)



"""
for i in pagina:
    print(pagina.find('<p'))
"""
"""
f = open("arquivo.txt", "w+")
f.write(page.text)
f.close()
"""