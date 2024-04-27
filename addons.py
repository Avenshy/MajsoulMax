from loguru import logger
from mitmproxy import http, ctx
import liqi_new
from plugin import helper, mod
from ruamel.yaml import YAML
from sys import stdout
from plugin import update_liqi

logger.remove()
logger.add(stdout, colorize=True,
           format='<cyan>[{time:HH:mm:ss.SSS}]</cyan> <level>{message}</level>')
# 导入配置
yaml = YAML()
SETTINGS = yaml.load('''\
# 插件配置，true为开启，false为关闭
plugin_enable:
  mod: true  # mod用于解锁全部角色、皮肤、装扮等
  helper: false  # helper用于将对局发送至雀魂小助手，不使用小助手请勿开启
# liqi用于解析雀魂消息
liqi:
  auto_update: true  # 是否自动更新
  liqi_version: 'v0.11.36.w'  # 本地liqi文件版本
''')
try:
    with open('./config/settings.yaml', 'r', encoding='utf-8') as f:
        SETTINGS.update(yaml.load(f))
except:
    logger.warning(
        '''首次运行，默认启用mod，禁用helper\n
        如需使用，请修改./config/settings.yaml文件\n
        修改完成后重新启动即可\n
        ''')


MOD_ENABLE = SETTINGS['plugin_enable']['mod']
HELPER_ENABLE = SETTINGS['plugin_enable']["helper"]
if SETTINGS['liqi']['auto_update']:
    logger.info('正在检测liqi文件更新，请稍候……')
    try:
        SETTINGS['liqi']['liqi_version'] = update_liqi.update(
            SETTINGS['liqi']['liqi_version'])
    except:
        logger.critical('liqi文件更新失败！可能会导致部分消息无法解析！')
with open('./config/settings.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(SETTINGS, f)
logger.success(
    f'''已载入配置：\n
    启用mod: {MOD_ENABLE}\n
    启用helper：{HELPER_ENABLE}\n
    ''')
if MOD_ENABLE:
    mod_plugin = mod.mod()
if HELPER_ENABLE:
    helper_plugin = helper.helper()
liqi_proto = liqi_new.LiqiProto()
if not (MOD_ENABLE or HELPER_ENABLE):
    logger.warning('请注意，当前没有开启任何功能，请修改./config/settings.yaml文件并重新启动！')


class WebSocketAddon:
    def websocket_message(self, flow: http.HTTPFlow):
        # 在捕获到WebSocket消息时触发
        assert flow.websocket is not None  # make type checker happy
        message = flow.websocket.messages[-1]
        # 不解析ob消息
        if flow.request.path == '/ob':
            if message.from_client is False:
                logger.debug(f'接收到（未解析）：{message.content}')
            else:
                logger.debug(f'已发送（未解析）：{message.content}')
            return
        # 解析proto消息
        if MOD_ENABLE:
            # 如果启用mod，就把消息丢进mod里
            if not message.injected:
                modify, drop, msg, inject, inject_msg = mod_plugin.main(message, liqi_proto)
                if drop:
                    message.drop()
                if inject:
                    ctx.master.commands.call(
                        "inject.websocket", flow, True, inject_msg, False)
                if modify:
                    # 如果被mod修改就同步变更
                    message.content = msg
        try:
            result = liqi_proto.parse(message)
        except:
            if message.from_client is False:
                logger.error(f'接收到(error):{result}')
            else:
                logger.error(f'已发送(error):{result}')
        else:
            if message.from_client is False:
                if HELPER_ENABLE:
                    # 如果启用helper，就把消息丢进helper里
                    helper_plugin.main(result)
            else:
                    logger.info(f'已发送：{result}')


addons = [
    WebSocketAddon()
]
