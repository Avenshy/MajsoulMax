from ruamel.yaml import YAML
from loguru import logger

class replace:
    def __init__(self):
        self.yaml = YAML()
        self.LoadSettings()
        logger.success('已载入replace')

    def LoadSettings(self):
        self.settings = self.yaml.load('''\
config:
  http: []
  lq: []
''')
        try:
            with open('./config/settings.replace.yaml', 'r', encoding='utf8') as f:
                self.settings.update(self.yaml.load(f))
        except:
            logger.warning(
                '未检测到replace配置文件，已生成默认配置，如需自定义replace配置请手动修改 ./config/settings.replace.yaml')
            self.SaveSettings()

    def SaveSettings(self):
        with open('./config/settings.replace.yaml', 'w', encoding='utf8') as f:
            self.yaml.dump(self.settings, f)

    def main(self, request):
        for path in self.settings['config']['http']:
            if path in request.path:
                return path 
        return ''