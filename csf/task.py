
import asks
import curio
from tools import *
from tenacity import *   #retry mothed

asks.init('curio')

maxRetryTime = 2
requestTimeout=5

class Task():
    def __init__(self,tasks,sessionConnections=10):
        '''
        :param taskList:  taskList dict,
        {'public':{
        mothed:get|post
        cookies:cookies字典
        headers:headers字典
        responseType:text|json|stream  仅在为stream时result保存的是stream的临时文件，否则保存返回的text
                     json可以为用来标示结果是否为json
        }
        'taskList':[{
        url:'http://www.qq.com',必填
        params:get参数字典
        data:post数据，字典或是str
        #结果数据
        responseType:text|json|stream  仅在为stream时result保存的是stream的临时文件，否则保存返回的text
                     json可以为用来标示结果是否为json
        requestOk:1或0,返回的状态码为200即成功。
        callbackOk:1,0,如果callback函数成功执行即为1
        result:如果respnseType 为 text或 json,结果就是返回的html或json串
               如果 reonsetype 为 stream 结果为 stream保存的文件名
               如果 responseType 为 空，结果保存在 response里，否则response为空
        response:asks.response，只果请求成功,都会有response,否由为None
        retryTime:重试次数
        error:最后一次重试出错的错误信息
        }]}
        '''
        publicArgs = tasks['public']
        self.method = publicArgs['method']
        self.cookies = publicArgs['cookies'] if 'cookies' in publicArgs else None
        self.responseType = publicArgs['responseType'] if 'resonseType' in publicArgs else 'text'
        self.taskList = tasks['taskList']
        self.s = asks.Session(connections=sessionConnections)
        self.s.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        })
        self.s.headers.update(publicArgs['headers'])

        for i in self.taskList:
            i.update({
                'requestOk': 0,
                'result': '',
                'retryTime': 0,
                'response':None,
                'error': '',
                'responseType':self.responseType
            })
            if 'params' not in i:
                i.update({'params':None})
            if 'data' not in i:
                i.update({'data':None})

    async def taskRequest(self,url, cookies, params, data, method, taskid):
        def retryCallback(retry_state):
            self.taskList[taskid]['retryTime'] = retry_state.attempt_number-1
            if retry_state.attempt_number == maxRetryTime+1:
                self.taskList[taskid]['error'] = f'{type(retry_state.outcome._exception)}:{retry_state.outcome.exception()}'

        @retry(stop=stop_after_attempt(maxRetryTime + 1), wait=wait_fixed(0.5) + wait_random(0, 2),
               sleep=curio.sleep, retry_error_callback=retryCallback)
        async def urlRequest(url, cookies=None, params=None, data=None, method="POST"):
            print(f'task urRequest start in {taskid}:{url}')
            _r = await self.s.request(method, url, cookies=cookies, params=params, data=data,
                                 connection_timeout=requestTimeout,
                                 callback=None if self.responseType != 'stream' else streamSave)
            self.taskList[taskid]['response'] = _r
            if _r.status_code == 200:
                self.taskList[taskid]['requestOk'] = 1
                print((f'task urRequest end in {taskid}:{_r.status_code}'))
                if self.responseType != 'stream':
                    self.taskList[taskid].update({
                        'result':_r.text
                    })
            else:
                self.taskList[taskid]['error'] = f'responseReturnStatus_code:{_r.status_code}'

        async def streamSave(self,bytechunk):
            fileName = randomFileName()
            folder =  getTempDir()
            if folder[-1] not in ('\\', '/'):
                folder = folder + '/'
            path = folder + fileName
            async with curio.aopen(path, 'ab') as out_file:
                await out_file.write(bytechunk)
            self.taskList[taskid]['result'] = fileName
        await  urlRequest(url, cookies, params, data, method)

    async def taskGo(self):
        try:
            async with curio.TaskGroup() as g:
                for key, task in enumerate(self.taskList):
                    await g.spawn(self.taskRequest(task['url'], cookies=self.cookies,
                                              params=task['params'], data=task['data'], method = self.method,
                                              taskid=key))
        except curio.TaskGroupError as e:
            pass
        return  self.taskList



