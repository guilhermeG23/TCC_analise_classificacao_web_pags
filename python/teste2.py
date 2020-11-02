#libs
from fuzzywuzzy import fuzz
from fuzzywuzzy import process 

#Arrays de teste
a = ["teste"]
b = ["teste1", "pastel1", "kilo2"]

#Print dos resultados
print(fuzz.token_set_ratio(a, b)) #Result: 40
print(fuzz.token_set_ratio(a, b[0])) #Result: 91
print(fuzz.partial_token_set_ratio(a, b)) #Result: 100
print(fuzz.partial_token_set_ratio(a, b[0])) #Result: 100