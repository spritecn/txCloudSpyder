import time


def randomFileName(ex=''):
    '''
    生成随机文件名，ex为扩展名，默认为空
    返回16位数字加 .扩展名
    '''
    from random import randint
    #timeStr = str(int(time.time()*1000))
    #randStr = f"{(lambda x: ((3-len(x)) * '0') + x)(str(randint(1,999)))}"
    #return timrStr + randStr
    if ex:
        return f"{int((time.time()*1000))}{(lambda x: ((3-len(x)) * '0') + x)(str(randint(1,999)))}.{ex}"
    return f"{int((time.time()*1000))}{(lambda x: ((3-len(x)) * '0') + x)(str(randint(1,999)))}"

def getTempDir():
    from tempfile import gettempdir
    return gettempdir()

def dictToList(sDict):
    '''
    将一个dict根据value转换为list,如果有两个key的value是list,len(value)必须相等，如下
    :param sDict: {'aa':['bb','cc'],'dd':'ee'}, {'aa': ['bb', 'cc'], 'dd': 'ee','ff':[1,2]}
    :return: [{'aa':'bb','dd':'ee'},{'aa':'cc','dd':'ee'}],
            [{'aa': 'bb', 'ff': 1, 'dd': 'ee'}, {'aa': 'cc', 'ff': 2, 'dd': 'ee'}]
    '''
    resultList = []
    baseDict = {}
    flag = 0
    for key in sDict.keys():
        if type(sDict.get(key)) == list:
            for index,d in enumerate(sDict.get(key)):
                if flag == 0:
                    resultList.append({key:d})
                else:
                    resultList[index].update({key:d})
            flag = 1
        else:
            baseDict.update({key:sDict[key]})
    if resultList:
        for i,d in enumerate(resultList):
            resultList[i].update(baseDict)
    else:
        resultList.append(baseDict)
    return resultList



class typeError(Exception):
    '''just def a error'''
    pass

class dbStoreError(Exception):
    pass