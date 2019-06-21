#simple tencent cmq client
#
#author:spx

import hmac
import json
from hashlib import sha1
from base64 import b64encode
from config import _config
import time
import asks
asks.init('curio')

    
_domain = f"cmq-queue-{_config['Region']}.api.qcloud.com"
_enport = _domain + _config['path']
_enportUrl = 'https://' + _enport

_topicDomain = f"cmq-topic-{_config['Region']}.api.qcloud.com"
_topicEnport = _domain + _config['path']
_topicEnportUrl = 'https://' + _enport


def signGen(enport = _enport, param = {}, method = 'GET'):
    '''
    param为cmq的请求参数字典，比如：
    Action=SendMessage
    Nonce=2889712707386595659
    '''
    method = method.upper()
    if not param:
        return ''
    _tmpKeySort = sorted(param.keys())
    _tmpDict = []
    for k in _tmpKeySort:
        _tmpDict.append(k.replace("_", ".") + '=' + str(param[k]))
    
    srcStr = method + enport + '?' + '&'.join(_tmpDict)
    #print(srcStr)
    return  _hamcsha1(_config['secretKey'],srcStr)
    
def _hamcsha1(key,msg):
    key = key if type(key) == bytes else key.encode('utf8')
    msg = msg if type(msg) == bytes else msg.encode('utf8')
    return b64encode(hmac.new(key,msg,sha1).digest()).decode('utf8')
    

async def msgPush(queName,msg):
    '''
    msg支持字典和字符，如果是字典会json
    '''
    if isinstance(msg, dict):
        msgBody = json.dumps(msg, ensure_ascii = False)
    else:
        msgBody = str(msg)
    method = "POST"
    _t = time.time()
    params = {
    'Action': 'SendMessage',
    'Timestamp': int(_t),
    'Nonce': str(_t)[-3:],
    'SecretId': _config['secretId'],
    'queueName': queName,
    'msgBody':msgBody
    }
    params.update({'Signature':signGen(params,method)})
    _r = await asks.post(_enportUrl,data=params)
    return _r.json()

async def msgRecv(queName):
    method = "GET"
    _t = time.time()
    params = {
    'Action': 'ReceiveMessage',
    'Timestamp': int(_t),
    'Nonce': str(_t)[-3:],
    'SecretId': _config['secretId'],
    'queueName': queName
    }
    params.update({'Signature':signGen(params,method)})
    print(params)
    _r =  await asks.get(_enportUrl,params=params,max_redirects=10)
    return _r.json()


async def msgDel(queName,receiptHandle):
    #receiptHandle 是接收消息时返回的句柄
    method = "POST"
    _t = time.time()
    params = {
    'Action': 'ReceiveMessage',
    'Timestamp': int(_t),
    'Nonce': str(_t)[-3:],
    'SecretId': _config['secretId'],
    'queueName': queName,
    'receiptHandle':receiptHandle
    }
    params.update({'Signature':signGen(params,method)})
    #print(params)
    _r =  await asks.POST(_enportUrl,data=params)
    return _r.json()


async def topicPush(topicName,msg):
    '''
    msg支持字典和字符，如果是字典会json
    '''
    if isinstance(msg, dict):
        msgBody = json.dumps(msg, ensure_ascii = False)
    else:
        msgBody = str(msg)
    method = "POST"
    _t = time.time()
    params = {
    'Action': 'PublishMessage',
    'Timestamp': int(_t),
    'Nonce': str(_t)[-3:],
    'SecretId': _config['secretId'],
    'topicName': topicName,
    'msgBody':msgBody
    }
    params.update({'Signature':signGen(_topicEnport,params,method)})
    _r = await asks.post(_topicEnportUrl,data=params)
    return _r.json()
