def canNotSelect(word):
    import cx_Oracle as orc
    conn = orc.connect('db_name/db_pass@host_ip:port/db_usr')
    cursor = conn.cursor()
    try:
        cursor.execute(word)
    except orc.DatabaseError as e:
        err = e.__str__()
        # 跳过 procedure 与 function
        if err.split(':')[0]=='ORA-04044':
            pass
        else:
            return err
    else:
        return None
def getFiles():
    import os
    print('---------------------------------------------')
    print('Getting the list of sql file')
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
    print('-----------------------')
    print('Getting sql from ', file)
    with open(file, 'r', encoding='gbk') as fin:
        sql = fin.read()
    return sql
#接下来的问题：如何获取字段
def isPartOfToken(chr):
    res = chr.isalnum() or chr=='.' or chr=='_'
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
    token = string[start:end]
    if token.count('.')>1:
        token = token.replace('.', ':', 1)
        token = token.split('.')[0]
        token = token.replace(':', '.')
    return token
def getTokens(string):
    tokens = set()
    beg = 0; has_dot, dot_index = hasDot(string, beg)
    print('-----------------------')
    print('Getting tokens from sql')
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
def getBiasList(tokens):
    print('-----------------------')
    print('Getting biases according to tokens')
    biases = []
    for token in tokens:
        bias = token.split('.')[0]
        if bias not in biases:
            biases.append(bias)
    return biases
def getBiasDict(biases, tokens, string):
    print('-----------------------')
    print('Getting bias dictionary according to biases, tokens and sql')
    biasDict = {}
    for bias in biases:
        findBias = re.search(' '+bias+'[\s,]', string)
        if findBias:
            end = findBias.span()[0]
            toChecked = string[end:end-50:-1][::-1]
            for token in tokens:
                findToken = re.search(token, toChecked)
                if findToken:
                    biasDict[bias] = token
    return biasDict
def sqlWord(token, biasDict):
    head = 'select * from '
    tail = ' where rownum<=1'
    bias = token.split('.')[0]
    biasSet = list(biasDict.keys())
    if bias not in biasSet:
        return head + token + tail
    else:
        return 'select ' + token.split('.')[1] + ' from ' + biasDict[bias] + tail
def writeFile(tokens, biasDict, errDir, file):
    import time
    print('-----------------------')
    print('updating error file')
    with open(errDir+'/Error-'+time.strftime('%Y-%m-%d')+'.txt', 'a+') as fout:
        fout.write(time.strftime('%H:%M:%S') + '\n')
        fout.write(file+'\n')
        for token in tokens:
            word = sqlWord(token, biasDict)
            hasError = canNotSelect(word)
            if hasError:
                fout.write(token + ': ' + hasError + '\n')
def printErr2File(file):
    import os
    errDir = 'Errors'
    print('-----------------------')
    print('Checking ', file)
    # 如果当前目录下没有存放 error 集的目录，则创建新目录
    if errDir not in os.listdir():
        os.mkdir(errDir)
    # 将文件存放在当日的问题文件中
    sql = getSqlFrom(file)
    tokens = getTokens(sql)
    biases = getBiasList(tokens)
    biasDict = getBiasDict(biases, tokens, sql)
    writeFile(tokens, biasDict, errDir, file)


if __name__ == '__main__':
    files = getFiles()
    for file in files:
        printErr2File(file)


    #sql = getSqlFrom(files[0])
    #tokens = getTokens(sql)
    #print(canNotSelect('apps.fnd_profile'))
    #for t in tokens:
    #    print(t)
    #biases = getBiasList(tokens)
    #print(biases)
    #biasDict = getBiasDict(biases, tokens, sql)
    #for token in tokens:
    #    word = sqlWord(token, biasDict)
    #    #print(word)
    #    hasError = canNotSelect(word)
    #    if hasError:
    #        print(token, ': ', hasError)



    #for bd in biasDict.items():
    #    print(bd)
    #print(biasDict.keys())
    #for t in tokens:
    #    can_not_access = canNotSelect(t)
    #    if can_not_access:
    #        print(t,': ', can_not_access)
    #print(canNotSelect('FA_INVOICE_DETAILS_V'))
