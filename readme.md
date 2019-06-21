# 基于腾讯CMQ和CSF的异步采集
- 使用CSF云函数来异步采集数据
- 使用CMQ的主题模型来给CSF发送任务数据
    - 实现了一个简单的cmqClient
- 使用mysql来保存任务(腾讯云数据库比较贵，用了一个小vps)
- treeSql 的数据库restfull api用来读写数据
    - https://github.com/mevdschee/php-crud-api
    - 如果觉得不方便可以使用源生数据为读写,taskDb.py


## 平台搭建
- 腾讯云同一个区域 建一个csf函数，一个cmq主题模型实例
- 将csf的触发方式改为 cmq主题定订阅触发
- 找个数据库来做任务记录
- 找个可以运行php的地方来放treesql的api

##  发送任务
- 使用cmq客户端发送cmqClient.topicPush(msg)即可
    - msg是一字典，主要参数如下：
    ```
    client:客户端标识，用来标明请求是哪个客户端发起的
    useage:标识task用途 200字符内
    listFlag:url|params|data|other,用来标识哪一个参数是一个list
             根据这个list生成任务队列  
             对于params这种字典，如果有多个参数，只有一个参数是list
             可以写在成{‘param1':['v1','v2'],'param2':'xxx'}
             会转换在一个列表,见tools/dictToList()
    connections:并发连接数，asks.session(connections)
    mothed:get|post
    url:'http://www.qq.com'
    cookies:cookies字典
    headers:headers字典
    params:get参数字典
    data:post数据，字典或是str
    responseType:text|json|stream  仅在为stream时result保存的是stream的临时文件，否则保存返回的text
                 json可以为用来标示结果是否为json，默认为text
    ```
    - 不需要参数可以不填，headers默认是一个chrome的
    -  请求失败会重试，默认0.5到2秒 随机时间重试2次
## 处理结果
- 结果和请求参数都保存在taskList里，
    - {'url': 'http://www.qq.com/',
      'requestOk': 0,
      'result': '',
      'retryTime': 1,
      'response': None,
      'error': "<class 'asks.errors.RequestTimeout'>:",
      'responseType': 'text',
      'params': None}
    - response 为请求的原始asks.response   
- 可以在csf,index.py,main_hanlder底部填加处理


## TODO
- ~~任务保存 2/23~~
- 数据库uaeage 来标识任务用途,方便后续数据处理
- ~~精简taskList,cookies|headers,等公共参数不需要出现在tasklist里~~
- ~~用class重写请求~~
---
- 给dbapi 添加basicAuth
- 