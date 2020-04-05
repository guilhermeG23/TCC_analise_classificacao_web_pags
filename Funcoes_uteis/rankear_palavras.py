def rankear_palavras(array_palavras, ordem):
    #Reserve = True -> Do maior para menor
    #Reverse = False -> Do menor para o maior
    return array_palavras.sort(key = sortSecond, reverse = ordem) 