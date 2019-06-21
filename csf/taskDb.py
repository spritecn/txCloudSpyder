import  json
#import platform
import asks
import time
import curio
from asks import BasicAuth

asks.init('curio')
dbUrl = 'http://114.115.170.169:8080/php-crud-api.php/records/task' #task表的treesq api的地址，task可以根据表名更改
auth = {'user':'spx','pass':'spx'} #basicAuth, 仅在user不这空时启用
basicAuth = BasicAuth((auth['user'],auth['pass'])) if auth['user'] else None

async def taskStart(topicMsg,createtime,useage = '',clientid = 1):
    #return taskid
    taskDict = {
        'clientid':1,
        'taskinfo':json.dumps(topicMsg),
        'createtime':int(createtime),
        'useage':useage
    }
    _r = await  asks.post(dbUrl,json = taskDict,auth=basicAuth)
    return  _r.json()


async def taskFinish(taskList,taskid,createtime):
    errorinfo = []

    def clearDIct(sDict):
        # 清空dict里空的value,response也清掉
        return  {k:v for k,v in sDict.items() if v and k !='response'}

    for key,i in enumerate(taskList):
        if i['error']:
            errorinfo.append(key)
    resultDict = {
        'taskcount':len(taskList),
        'runtime':round(time.time()-createtime,2),
        'errorcount':len(errorinfo),
        'errorinfo':json.dumps(errorinfo),
        'finished':1
    }

    #先并发写taskresult子表数据,api批量写入太慢了
    print('------taskResult save start-------')
    s = asks.Session(connections=10)
    _psotReslt = []

    async def taskresultSave(k,jsonData):
        _r = await s.post(f'{dbUrl}result',json = jsonData,auth=basicAuth)
        try:
            _psotReslt.append((k,_r.json()))
        except:
            _psotReslt.append((k, _r.text))

    async with curio.TaskGroup() as g:
        for k,i in enumerate(taskList):
            await  g.spawn(taskresultSave,k,{'fid':taskid,'taskid':k,'result':json.dumps(clearDIct(i))})
        async for _ in g:
            print(f"done with {_psotReslt[-1][0]}:{_psotReslt[-1][1]}")

    #更新父表数据
    _r = await asks.put(f'{dbUrl}/{taskid}',json=resultDict,auth=basicAuth)
    return  _r.json()