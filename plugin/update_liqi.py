from auto_play.RequestsProxy import proxy as requests
from loguru import logger


def get_version():
    req = requests.get('https://game.maj-soul.com/1/version.json', timeout=10)
    return req.json()


def get_prefix(version):
    req = requests.get(f'https://game.maj-soul.com/1/resversion{version}.json',timeout=10)
    return req.json()['res']['res/proto/liqi.json']['prefix']


def update(version):
    new_version = get_version()
    prefix = get_prefix(new_version['version'])
    if prefix == version:
        logger.success(f'liqi文件无需更新，当前版本：{prefix}')
        return version
    else:
        req = requests.get(
            f'https://api.github.com/repos/Avenshy/AutoLiqi/releases/latest', timeout=10)
        if req.headers['X-RateLimit-Remaining'] == '0':
            logger.error('''\
    github api额度用完，无法更新liqi文件！请尝试以下方法：\n
    1. 使用或更换代理\n
    2. 在 https://github.com/Avenshy/AutoLiqi/releases/latest 下载liqi.json、liqi.proto和liqi_pb2.py，放入proto文件夹中
    3. 等待1个小时后再试''')
            return version
        liqi = req.json()
        if liqi['tag_name'] != prefix :
            logger.error('liqi文件需要更新，但AutoLiqi项目还未更新，晚点再来试试吧！')
            logger.error('详细信息请看 https://github.com/Avenshy/AutoLiqi')
            return version
        else:
            for item in liqi['assets']:
                match item['name']:
                    case 'liqi.json' | 'liqi.proto' | 'liqi_pb2.py':
                        req = requests.get(item['browser_download_url'])
                        with open(f'proto/{item["name"]}', 'w') as f:
                            f.write(req.text)
            logger.success(f'liqi文件更新成功：{prefix}')
            return prefix
