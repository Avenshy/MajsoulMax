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
                '--mode', 'upstream:'+proxy,  # ���ö��δ���
            ]
        options += [
        '-p', str(port),  # ָ���˿�
        '-s', 'addons.py',  # ָ���ű�
        '--set', 'ssl_insecure=true',
        '--no-http2',
        '--ignore-hosts', "game.*",
        '--ignore-hosts', ".*ali.*",
        #'--allow-hosts', '^common-v2.*',
        #'--allow-hosts', '^gateway-hw.*',
        #'--tcp-hosts', '^gateway-hw.*'
        ]
        mitmdump(options)