import json
from tenacity import *   #retry mothed
from tools import *
from task import Task
import curio
import time
import taskDb

taskDbSave = 1  # 是否保存数据到数据库，见taskDb.py

def main_handler(event, context):
    print("Received event: " + json.dumps(event, indent = 2))
    print("Received context: " + str(context))
    cmq = event['Records'][0]['CMQ']
    msg = json.loads(cmq['msgBody'])
    print("--------------------------------")
    if (not ('url' in msg)) or type(msg) != dict:
        raise  TypeError("msg musr be a dict,and must have key 'url'")

    taskInfo = {
        'listFlag':msg['listFlag'] if 'listFlag' in msg else None,
        'method': msg['method'] if 'method' in msg else 'GET',
        'url': msg['url'],
        'params': msg['params'] if 'params' in msg else {},
        'data': msg['data'] if 'data' in msg else None,
        'cookies': msg['cookies'] if 'cookies' in msg else {},
        'headers': msg['headers'] if 'headers' in msg else {},
        'responseType': msg['responseType'] if 'responseType' in msg else 'text',
        'useage':msg['useage'] if 'useage' in msg else '',
        'connections':msg['connections'] if 'connections' in msg else 10
    }

    createTime = time.time()
    if taskDbSave:
        taskid = curio.run(taskDb.taskStart(msg, createTime,taskInfo['useage']))

    if taskInfo['method'].upper() not in ('GET','POST','PUT','DELETE'):
        taskInfo['method'] = 'GET'
    tasks =  tasksInit(
            taskInfo['listFlag'],
            taskInfo['method'].upper(),
            taskInfo['url'],
            taskInfo['params'],
            taskInfo['data'],
            taskInfo['cookies'],
            taskInfo['headers'],
            taskInfo['responseType'],
        )

    task = Task(tasks,sessionConnections=taskInfo['connections'])
    taskList = curio.run(task.taskGo)
    if taskList and taskDbSave:
        _result = curio.run(taskDb.taskFinish(taskList, taskid, createTime))
        if _result != 1:raise dbStoreError(f'dbStore.taskFinish:{_result}')
    print('-----end---resultTaskList-----------')
    print(taskList)



def tasksInit(listFlag, method, url, params=None, data=None, cookies=None, headers=None,
                 responseType='text'):
    '''
    :param listFlag: 标示哪一个参数用是队列列表,必须为url|params|data中的一个
    :param method: GET|PODT
    :param url: 如果listFlag为urls,urls必须为list,否则为 str
    :param params:同上，否则为dict
    :param data: 同上，否则为dict 或 str
    :param cookies,dict
    :param responseType: taskList
    :return: tasks
    '''
    tasks = {}
    publicDict = {
        'method':method,
        'cookies':cookies,
        'headers': headers,
        'responseType':responseType
    }
    taskList = []
    tasks.update({'public':publicDict})

    if listFlag == "url":
        if type(url) != list:
            raise typeError('listFlag is urls,urls must be a list')
        for i in url:
            taskList.append({
                'url':i,
                'params':params,
                'data':data
            })

    elif listFlag == "params":
        params = dictToList(params)
        if type(params) != list:
            raise typeError('listFlag is params,params must be a list')
        for i in params:
            taskList.append({
                'url': url,
                'params': i,
                'data': data
            })

    elif listFlag == "data":
        params = dictToList(params)
        if type(data) != list:
            raise typeError('listFlag is data,data must be a list')
        for i in data:
            taskList.append({
                'url': url,
                'params': params,
                'data': i
            })
    else:
        #raise typeError('listFlag must be in urls|params|datas')
        #如果 listFlag 非 must be in urls|params|datas' 时当做单一任务处理
        taskList.append({
            'url': url,
            'params': params,
            'data': data
        })
    tasks.update({'taskList':taskList})
    return  tasks
