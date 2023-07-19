def replaceSymbols(string):
    nova_string = string
    for s in ["%20", " "]:
        nova_string = nova_string.replace(s, "")
    return nova_string



print(replaceSymbols("SCD4%20"))