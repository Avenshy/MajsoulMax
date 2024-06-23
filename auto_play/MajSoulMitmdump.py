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
        '-s', 'addons.py'  # ָ���ű�
        ]
        mitmdump(options)