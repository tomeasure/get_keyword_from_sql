
def canNotSelect(word):
    import cx_Oracle as orc
    conn = orc.connect('db_name/db_pass@host_ip:port/db_usr')
    cursor = conn.cursor()
    sql = 'select * from ' + word
    try:
        cursor.execute(sql)
    except orc.DatabaseError as e:
        return e.__str__()
    else:
        return None
def getFiles():
    import os
    files = os.listdir('./SQLFiles/')
    toBeDeleted = []
    for i in range(len(files)):
        files[i] = './SQLFiles/' + files[i]
        if files[i][-3:] != 'sql':
            toBeDeleted.append(i)
    for i in range(len(toBeDeleted)):
        del files[toBeDeleted[len(toBeDeleted)-i-1]]
    return files
def getSqlFrom(file):
    with open(file, 'r', encoding='gbk') as fin:
        sql = fin.read()
    return sql
#接下来的问题：如何获取字段
def isPartOfToken(chr):
    res = chr.isalnum() or chr == '.' or chr == '_'
    return res
def dotLeft(string, dotIndex):
    i = 1
    while isPartOfToken(string[dotIndex-i]):
        i += 1
    return dotIndex - i + 1
def dotRight(string, dotIndex):
    i = 1
    while isPartOfToken(string[dotIndex+i]):
        i += 1
    return dotIndex + i
def isToken(string, dotIndex):
    return isPartOfToken(string[dotIndex-1])
def hasDot(string, beg):
    index = string.find('.', beg)
    return index != -1, index
def getToken(string, dotIndex):
    start = dotLeft(string, dotIndex)
    end = dotRight(string, dotIndex)
    return string[start:end]
def getTokens(string):
    tokens = set()
    beg = 0; has_dot, dot_index = hasDot(string, beg)
    while has_dot:
        beg = dot_index+1
        if isToken(string, dot_index):
            token = getToken(string, dot_index)
            if token[0] != 'o':
                tokens.add(token)
        has_dot, dot_index = hasDot(string, beg)
    return sorted(list(tokens))
# 接下来的问题：获取别名
import re
case_set = set(['from', 'where', 'and', 'as', 'in', 'then', 'case', 'not',
                'FROM', 'WHERE', 'AND', 'AS', 'IN', 'THEN', 'CASE', 'NOT'])
def getBias(string, tokenIndex):
    matched = re.search(' [a-zA-z0-9]+[\n ]', string[tokenIndex:])
    if matched:
        bias = matched.group().strip()
        if bias not in case_set and not bias[0].isdigit() and bias.find('_')==-1:
            return bias
    else:
        return ''
def getBiasDict(tokens, string):
    biasDict = {}
    for t in tokens:
        tokenIndex = string.find(t)
        bias = getBias(string, tokenIndex)
        if bias:
            #print(bias)
            biasDict[bias] = t
    return biasDict
def resetTokens(biasDict, tokens):
    newTokens = [t for t in tokens]
    for k in biasDict.keys():
        for i in range(len(newTokens)):
            newTokens[i] = newTokens[i].replace(k, biasDict[k])
    return newTokens

def tokenTocheck(file):
    sql = getSqlFrom(file)
    tokens = getTokens(sql)
    biasDict = getBiasDict(tokens, sql)
    new_tokens = resetTokens(biasDict, tokens)
    return new_tokens

if __name__ == '__main__':
    files = getFiles()
    #tokens = tokenTocheck(files[0])
    tokens = getTokens(getSqlFrom(files[0]))
    for t in tokens:
        print(t)
    #for t in tokens:
    #    can_not_access = canNotSelect(t)
    #    if can_not_access:
    #        print(t,': ', can_not_access)
    #print(canNotSelect('FA_INVOICE_DETAILS_V'))
