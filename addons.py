import liqi_new
import json
from pathlib import Path
import asyncio
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options
from loguru import logger
from mitmproxy import http, ctx
from plugin import helper, mod,replace
from ruamel.yaml import YAML
from sys import stdout
from plugin import update

BASE_DIR = Path(__file__).resolve().parent

VERSION = "v2026.07.07"
logger.warning(
    f"\n\n雀魂MAX        作者：Avenshy        版本：{VERSION}\n\
开源地址：https://github.com/Avenshy/MajsoulMax\n\n\
本工具完全免费、开源，如果您为此付费，说明您被骗了！\n\
本工具仅供学习交流，请在下载后24小时内删除，不得用于商业用途，否则后果自负！\n\
本工具有可能导致账号被封禁，给猫粮充钱才是正道！\n\n\
请作者喝咖啡：\n\
爱发电，支持支付宝、微信：https://afdian.net/a/Avenshy\n\
Patreon，支持Paypal、信用卡：https://patreon.com/Avenshy\n\n\
再次重申：脚本完全免费使用，没有收费功能，请喝咖啡完全自愿，作者非常感谢您！\n\n"
)

logger.remove()
logger.add(
    stdout,
    colorize=True,
    format="<cyan>[{time:HH:mm:ss.SSS}]</cyan> <level>{message}</level>",
)
# 导入配置
yaml = YAML()
SETTINGS = yaml.load("""\
# 插件配置，true为开启，false为关闭
plugin_enable:
  mod: true  # mod用于解锁全部角色、皮肤、装扮等
  helper: false  # helper用于将对局发送至雀魂小助手，不使用小助手请勿开启
  replace: false  # replace用于替换雀魂的游戏内容
# liqi用于解析雀魂消息
liqi:
  auto_update: true  # 是否自动更新
  github_token: '' # 仅供自己使用，请勿泄漏给任何人
  liqi_version: '0.16.243-4.0.45'  # 本地liqi文件版本
""")
try:
    with open("./config/settings.yaml", "r", encoding="utf-8") as f:
        SETTINGS.update(yaml.load(f))
except:
    logger.warning(
        """首次运行，默认启用mod，禁用helper\n
        如需使用，请修改 ./config/settings.yaml 文件\n
        修改完成后重新启动即可\n
        """
    )


MOD_ENABLE = SETTINGS["plugin_enable"]["mod"]
HELPER_ENABLE = SETTINGS["plugin_enable"]["helper"]
REPLACE_ENABLE = SETTINGS['plugin_enable']["replace"]
if SETTINGS["liqi"]["auto_update"]:
    logger.info("正在检测更新，请稍候……")
    try:
        result = update.update(
            max_version = VERSION,
            liqi_version = SETTINGS["liqi"]["liqi_version"],
            token = SETTINGS["liqi"]["github_token"]
        )
        SETTINGS["liqi"]["liqi_version"] = result
    except:
        logger.critical("更新失败！可能会导致部分消息无法解析！")
with open("./config/settings.yaml", "w", encoding="utf-8") as f:
    yaml.dump(SETTINGS, f)
logger.success(
    f"""已载入配置：\n
    启用mod: {MOD_ENABLE}\n
    启用helper：{HELPER_ENABLE}\n
    启用replace：{REPLACE_ENABLE}\n
    """
)
if MOD_ENABLE:
    mod_plugin = mod.mod(VERSION)
if HELPER_ENABLE:
    helper_plugin = helper.helper()
if REPLACE_ENABLE:
    replace_plugin = replace.replace()
liqi_proto = liqi_new.LiqiProto()
if not (MOD_ENABLE or HELPER_ENABLE or REPLACE_ENABLE):
    logger.warning(
        "请注意，当前没有开启任何功能，请修改./config/settings.yaml文件并重新启动！"
    )


class MajsoulMaxAddon:
    _hosts = ('maj-soul.com', 'mahjongsoul.com', 'majsoul', 'catmjstudio', 'yo-star.com')

    def __init__(self):
        self.emoji_panel_assets = {}

    def websocket_message(self, flow: http.HTTPFlow):
        # 在捕获到WebSocket消息时触发
        assert flow.websocket is not None  # make type checker happy
        message = flow.websocket.messages[-1]
        # 不解析ob消息
        if flow.request.path == "/ob":
            if message.from_client is False:
                logger.debug(f"接收到（未解析）：{message.content}")
            else:
                logger.debug(f"已发送（未解析）：{message.content}")
            return
        # 解析proto消息
        if MOD_ENABLE:
            # 如果启用mod，就把WS消息丢进mod里
            if not message.injected: # 不解析MAX自己插入的WS消息
                modify, drop, msg, inject, inject_msg = mod_plugin.main(
                    message, liqi_proto
                )
                if drop: 
                    message.drop()
                if inject:
                    ctx.master.commands.call(
                        "inject.websocket", flow, True, inject_msg, False
                    )
                if modify:
                    # 如果被mod修改就同步变更
                    message.content = msg
        try:
            result = liqi_proto.parse(message) # 解析消息
        except:
            if message.from_client is False:
                logger.error(f"接收到(error):{message.content}")
            else:
                logger.error(f"已发送(error):{message.content}")
        else:
            if message.from_client is False:
                if message.injected:
                    logger.success(f"接收到(injected)：{result}")
                elif MOD_ENABLE and modify:
                    logger.success(f"接收到(modify)：{result}")
                elif MOD_ENABLE and drop:
                    logger.success(f"接收到(drop)：{result}")
                else:
                    logger.info(f"接收到：{result}")
                if HELPER_ENABLE:
                    # 如果启用helper，就把消息丢进helper里
                    helper_plugin.main(result)
            else:
                if MOD_ENABLE and modify:
                    logger.success(f"已发送(modify)：{result}")
                else:
                    logger.info(f"已发送：{result}")
    def request(self,flow: http.HTTPFlow):
        # 在捕获到HTTP消息时触发
        if MOD_ENABLE and any(k in flow.request.host for k in self._hosts):
            from plugin.unity_emoji import PATCH_TAG
            path = flow.request.path.partition('?')[0]
            if path == '/_majsoulmax/emoji-panel-assets':
                body = json.dumps({'tag': PATCH_TAG, 'assets': list(self.emoji_panel_assets.values())}).encode()
                flow.response = http.Response.make(200, body, {'content-type': 'application/json', 'cache-control': 'no-store'})
                return
            if path in self.emoji_panel_assets:
                flow.metadata['max_emoji_panel'] = True
            if flow.metadata.get('max_emoji_panel') or path.endswith('.loader.js') or path.endswith('/bundle_info_so.majset'):
                for header in ('if-none-match', 'if-modified-since'):
                    flow.request.headers.pop(header, None)
        if REPLACE_ENABLE:
            # 如果启用replace，就把HTTP消息丢进replace里
            path = replace_plugin.main(flow.request)
            if path != '':
                with open(f"./replace{path}","rb") as f:
                    if (body := f.read() )!=b"":
                        flow.response = http.Response.make(200, body) #,  {"Content-Type": "image/png"})
                        logger.success(f"已替换(replace)：{flow.request.path}")
                    else:
                        logger.error(f"替换错误(error):{flow.request.path}")

    def response(self, flow: http.HTTPFlow):
        if not MOD_ENABLE or not any(k in flow.request.host for k in self._hosts):
            return
        path = flow.request.path.partition('?')[0]
        if flow.response.status_code != 200:
            return
        is_loader = path.endswith('.loader.js') and '/Build/' in path
        is_index = path.startswith('/assetbundles/') and path.endswith('/bundle_info_so.majset')
        is_panel = flow.metadata.get('max_emoji_panel', False)
        if not (is_loader or is_index or is_panel):
            return
        from plugin.unity_emoji import PATCH_TAG, patch_bundle, panel_bundle_names
        try:
            body = flow.response.content
            if is_loader:
                bootstrap = (BASE_DIR / 'plugin' / 'unity_emoji_bootstrap.js').read_bytes()
                patched = body + b'\n' + bootstrap
            elif is_index:
                prefix = path.rsplit('/', 1)[0]
                for name in panel_bundle_names(body):
                    url = prefix + '/' + name
                    self.emoji_panel_assets[url] = {'name': name, 'url': url}
                return
            elif is_panel:
                patched = patch_bundle(body)
                flow.response.headers['x-majsoulmax-emoji-panel'] = PATCH_TAG
                logger.info('已更新 Unity 对局表情面板')
            else:
                return
        except Exception as e:
            logger.warning('Unity 表情面板补丁失败，保留原资源：{}', e)
            return
        flow.response.content = patched
        for header in ('etag', 'last-modified'):
            flow.response.headers.pop(header, None)
        flow.response.headers['cache-control'] = 'no-store'


addons = [MajsoulMaxAddon()]

async def start_mitm():
    # 创建 mitmproxy 配置
    opts = Options(listen_host="0.0.0.0", listen_port=23410, ssl_insecure=True)
    # 创建 DumpMaster，类似于 mitmdump 的功能
    master = DumpMaster(opts)
    # 加载自定义插件
    master.addons.add(MajsoulMaxAddon())
    try:
        # 启动 mitmproxy
        await master.run()
        master
    except KeyboardInterrupt:
        master.shutdown()


if __name__ == "__main__":
    asyncio.run(start_mitm())
