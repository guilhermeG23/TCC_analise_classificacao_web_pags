import nltk

nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('portuguese')

import urllib.request
from bs4 import BeautifulSoup
response = urllib.request.urlopen('https://pt.wikipedia.org/wiki/Scikit-learn')
html = response.read()

soup = BeautifulSoup(html,'html5lib')
text = soup.get_text(strip = True)
text = text.lower()

import re
text = re.sub(r'[^\w\s]', ' ', text)
text = re.sub("\d+", ' ', text)
tokens = [t for t in text.split()]

clean_tokens = []
for token in tokens:
    if token not in stopwords and len(token) < 20:
        clean_tokens.append(token)

freq = nltk.FreqDist(clean_tokens)

for key,val in freq.items():
    print(str(key) + ':' + str(val))

freq.plot(20, cumulative=False)