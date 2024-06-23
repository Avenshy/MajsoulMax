import argparse
import yaml
from auto_play.MahjongHelper import MahjongHelper
from auto_play.MajSoulMitmdump import MajSoulMitmdump
from auto_play.MajSoulWeb import MajSoulWeb

def update_helper_config(helper_port):
    config_data = {
        'config': {
            'api_url': f'https://localhost:{helper_port}/'
        }
    }
    
    with open('config/settings.helper.yaml', 'w') as file:
        yaml.dump(config_data, file, default_flow_style=False)
        
def update_proxy_config(proxy):
    config_data = {
        'config': {
            'proxy': proxy
        }
    }
    
    with open('config/settings.proxy.yaml', 'w') as file:
        yaml.dump(config_data, file, default_flow_style=False)

parser = argparse.ArgumentParser(description='设置代理和端口配置')
parser.add_argument('-proxy', type=str, default=None, help='指定代理上网，流量出接口,http://host:port')
parser.add_argument('-mit_port', type=int, default=23410, help='指定中间代理监听端口')
parser.add_argument('-helper_port', type=int, default=12121, help='指定小助手端监听口')

args = parser.parse_args()

update_helper_config(args.helper_port)
if args.proxy:
    update_proxy_config(args.proxy)

helper = MahjongHelper(port=args.helper_port)
web = MajSoulWeb(proxy_port=args.mit_port)
mitmdump = MajSoulMitmdump(proxy=args.proxy,port=args.mit_port)