import requests
from loguru import logger


def get_version():
    req = requests.get('https://game.maj-soul.com/1/version.json', timeout=10)
    return req.json()['version']


def get_prefix(version):
    req = requests.get(f'https://game.maj-soul.com/1/resversion{version}.json',timeout=10)
    return req.json()['res']['res/proto/liqi.json']['prefix']


def update(version,token):
    new_version ='v'+ get_version()
    #prefix = get_prefix(new_version['version'])
    if new_version == version:
        logger.success(f'liqi文件无需更新，当前版本：{new_version}')
        return new_version
    else:
        if token != '':
            req = requests.get(
                f'https://api.github.com/repos/Avenshy/AutoLiqi/releases/latest', timeout=10,headers={'Authorization':f'Bearer {token}','X-GitHub-Api-Version':'2022-11-28'})
        else:
            req = requests.get(
                f'https://api.github.com/repos/Avenshy/AutoLiqi/releases/latest', timeout=10)
        if req.headers['X-RateLimit-Remaining'] == '0':
            logger.error('''\
github api额度用完，无法更新liqi文件！请尝试以下方法：\n
1. 在 ./config/settings.yaml 中填入你的Github Token后重试\n
2. 在 https://github.com/Avenshy/AutoLiqi/releases/latest 手动下载liqi.json、liqi.proto、liqi_pb2.py，放入 ./proto 中，覆盖同名文件\n
3. 使用或更换代理\n
4. 等待1个小时后再试''')
            return version
        liqi = req.json()
        if liqi['tag_name'][:len(new_version)] != new_version :
            logger.error('liqi文件需要更新，但AutoLiqi项目还未更新，晚点再来试试吧！')
            logger.error('详细信息请看 https://github.com/Avenshy/AutoLiqi')
            return version
        else:
            for item in liqi['assets']:
                match item['name']:
                    case 'liqi.json' | 'liqi.proto' | 'liqi_pb2.py':
                        logger.warning(f'下载 {item["name"]} 中……')
                        req = requests.get(item['browser_download_url'],timeout=10)
                        with open(f'proto/{item["name"]}', 'w') as f:
                            f.write(req.text)
                        logger.success(f'下载 {item["name"]} 成功！')
            logger.success(f'liqi文件更新成功：{new_version}')
            return new_version
