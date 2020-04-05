import wget
import os
import sys

#entrada = str(input("URL: "))
entrada = sys.argv[1]
saida = entrada.split('/')
wget.download(entrada)
os.rename(r'download.wget',r'{}'.format(saida[2]))
