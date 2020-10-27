#Libs para TFIDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
#Array de teste
teste = ['teste teste1 teste2 teste teste teste1 a teste']
#TDIFD para operacao
vectorizer = TfidfVectorizer()
#Operando sobre o array
vector_pagina = vectorizer.fit_transform(teste)
#palavras de relevancia
print(vectorizer.get_feature_names())
#Frequencia
print(vector_pagina)
print(vector_pagina.shape)

