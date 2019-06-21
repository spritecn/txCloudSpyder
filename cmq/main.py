
from cmqClient import topicPush
import curio
url = [f'http://www.fantansy.cn/index.php/linux/{i}.html' for i in range(1,201)]

msg = {
    'url':url,
    'listFlag':'url',
    'clientid':0
}

print(curio.run(topicPush('task',msg)))
