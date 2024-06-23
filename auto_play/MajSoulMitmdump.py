from mitmproxy.tools.main import mitmdump

class MajSoulMitmdump:
    def __init__(
        self,
        proxy:str|None=None,
        port:int|str=23410,
    ):
        options=[]
        if proxy:
            options += [
                '--mode', 'upstream:'+proxy,  # 设置二次代理
            ]
        options += [
        '-p', str(port),  # 指定端口
        '-s', 'addons.py'  # 指定脚本
        ]
        mitmdump(options)