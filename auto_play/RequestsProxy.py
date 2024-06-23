import requests
import yaml
def init_proxy_config():
    config_data = {
        'config': {
            'proxy': None
        }
    }
    
    with open('config/settings.proxy.yaml', 'w') as file:
        yaml.dump(config_data, file, default_flow_style=False)
        
def get_proxy():
    try:
        with open('config/settings.proxy.yaml', 'r') as file:
            proxy = yaml.load(file, Loader=yaml.FullLoader)["config"]["proxy"]
        return proxy
    except:
        init_proxy_config()
        return None

class RequestsProxy:
    def __init__(self):
        proxy = get_proxy()
        if proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy,
            }
        else:
            self.proxies = None

    def get(self, url, **kwargs):
        kwargs['proxies'] = self.proxies
        return requests.get(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        kwargs['proxies'] = self.proxies
        return requests.post(url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        kwargs['proxies'] = self.proxies
        return requests.put(url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        kwargs['proxies'] = self.proxies
        return requests.delete(url, **kwargs)

# 创建一个RequestsProxy的实例并赋值给requests
proxy = RequestsProxy()
