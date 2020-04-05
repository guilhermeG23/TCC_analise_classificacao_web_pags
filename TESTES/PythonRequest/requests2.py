import requests
import re
import string

#Verficy -> Ignore SSL do requerido
#page = requests.get('https://www.google.com.br/', verify=False)
page = requests.get('https://stackoverflow.com/questions/44203397/python-requests-get-returns-improperly-decoded-text-instead-of-utf-8', verify=False)
#page.encoding = 'utf-8'
page.encoding = 'latin-1'
print(page.text)

f = open("arquivo.txt", "w+")
f.write(page.text)
f.close()

"""
f = open("arquivo.txt", "r")
for i in f.readlines():
    res = re.findall(r'\w+', i) 
    print(res)
    pass

f.close()
"""

"""
# Python3 code to demonstrate  
# to extract words from string  
# using regex( findall() ) 
import re 
  
# initializing string   
test_string = "Geeksforgeeks,    is best @# Computer Science Portal.!!!"
  
# printing original string 
print ("The original string is : " +  test_string) 
  
# using regex( findall() ) 
# to extract words from string 
res = re.findall(r'\w+', test_string) 
  
# printing result 
print ("The list of words is : " +  str(res)) 


# Python3 code to demonstrate  
# to extract words from string  
# using regex() + string.punctuation 
import string 
  
# initializing string   
test_string = "Geeksforgeeks,    is best @# Computer Science Portal.!!!"
  
# printing original string 
print ("The original string is : " +  test_string) 
  
# using regex() + string.punctuation 
# to extract words from string 
res = re.sub('['+string.punctuation+']', '', test_string).split() 
  
# printing result 
print ("The list of words is : " +  str(res)) 
"""

#print(page.status_code)
#print(page.url)
#print(page.text)
#print(page.encoding)
#print(page.content)
#print(page.headers['content-type'])
#print(page.headers)