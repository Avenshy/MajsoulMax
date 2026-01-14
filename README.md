# 雀魂 MAX

雀魂解锁全角色、皮肤、装扮等，基于 [mitmproxy](https://github.com/mitmproxy/mitmproxy) 的中间人攻击方式，支持网页版和客户端 / Steam 端。

同时支持将雀魂的牌局发到 [日本麻将助手 mahjong-helper](https://github.com/EndlessCheng/mahjong-helper)，不支持牌谱分析。

本工具完全免费、开源，如果您为此付费，说明您被骗了！

## 🧭 当前雀魂各服版本（实时更新）

![CHINESE](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgame.maj-soul.com%2F1%2Fversion.json&label=CHINESE&query=$.version&color=FF8C00&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAACsklEQVQ4ja2Tf0zMcRjHX9/7Ud0l59RCFssWmemGom5mNysbLb+GuM2G8mOMCGu0rD9aNuRHymxnNqbGqcwMG1lrRLmkRXOESoit311X1/34+MO37YY/vf96Pu89z+f5fJ73+5H4G1nAWWAPkAzoZL4LeAiU+SdLfrESKAZOAzeAVpl3AiogABgD5gImwPNn5yYgDngAXANKgZbbFw+J+jsnBdAJvA8KUNnNqUYBaP2LrwFXgQrAAtjmzAwfFG23RHtNkUhNinMaYiJ7gI6c3SkeoA4Q/l+oAdqB/mPpSVsLTu3US6FpXwDF9nVL9RmbVwSHaCTcPiV5xZUj96oaPsp1lSpg/vSwENdhc+KGyHCdtmvIKxYkZA51PyucUf36Kxv3n+uKmBqqWGVapPGM9JG5KUFzr6ohWJ7NAQnIBmI1geoge/mh9f29fdR+HPZGTZ2kmBwRKRmiI3jywi6Mi2ZL+oXbPztsRbOiV+b2dnUPdAIxKmBKmE4b8qgwLZUxF0XWl+4Rj9LF4hiNVxGkvPGuQxgXRkt371f7ANWrNx84l71Jv/mopRMYVAE/50TqjZ9+OCi50+i+cnytOj79yvDwqMtRaUnR2Vvs0r7cy85qW2s3oG77Nugzxc1UAG5gIrJ0pUBFaU6KAL5PC9P1lOWbReaWZaOXcs2eoaarwmErEsD36yczPG+tBwXQCAyMy/gcsALNQFNZvlkAn0ae5ouHJXt98fOi+svPZIhtqxOd9ttZotayS8hS5qnkC6xALBBoWhA1wdnf7QUCghRuQrWSlGQI11Q+fuk4f2TNhJp6OxesdX3AEiDB30x1QEvBjqVe+XnNQGN6imFsoOqEuHlijVApFe2ATbZxqL+RxmEBlgOjgE/mBOAC1PLZAIz74J9IloczCgzLcScwxO8N/b/4BZ4sCAP6Ouu4AAAAAElFTkSuQmCC&logoWidth=16) ![ENGLISH](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fmahjongsoul.game.yo-star.com%2Fversion.json&label=ENGLISH&query=$.version&color=FF8C00&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAADT0lEQVQ4jUXN2WtcVQDA4d+520xmsbOkM5OYNJkak5hJNQtE2mCgkj6ILUVEoTSIG0KVgpT4oIjig4qi5k0U8cWttr5IoUGoFBrRSilN1DRdNBMbkzTNNklmJplz7tx7fPDB7x/4BMDJZ0/kDw4fznquj1/1AM3Ia5/hyQpVDQDzi7OkExl2ptLUJOKcuzbO2V8vCOv1x+s/MKans3LuIyIdRynd0ly7uoTcKpPt7mN2coKqlLRm2/B8jTYExcIa+1v28Ol7J7TIf9hRCaVigfDunQR2JHA3lxl+qYxhaBKpDCuLC3QPPgJas3j9KoZpQjhMOl1H+K4Y1sJs0agrCUztM/zxGMeH2gjYEaSSzM3O4FgO4+dGEQLC4Si1u5qRrqK0WUQrhTW3IrmnM45lC159vp1kMoowobauntvzc9i2hVKKUDiMcl0W/84jXUm5JowhQIzk7leTRW0fGfA4m0/QfsegIRpgNKDJZOqZmvmdvs5u1gvbuK6ivFXGlRLbMBGAtb5hkAraXPzRZSkh6acGUXbZdMu8eWyIny63MDVxk3+W5onVxHBxaWxuZGlhhYrcRjzduU/llGl3KY0SJnlHcysTx/VW+eP6DZoMh0LI4eT571GywtTYz1y8fIWp8VlCdg1W0AkS3VYULJMzVolUIkMgaPHOyLv8cPo8k59/SeqhfRTXitS2t/DgkQYSjfWE1Rl+ufIXljAMqgEHp1RBahfTsdHKRxgWj77wBLmeNpr2H0AIF9Bow+C7T74l29fL1tgkVkVJNu7OMDjQT/TUN6B9TMNEBwJQkTQ/cB+itASRHSAEIGgtbhOrzbArlUYcasqpunjSLhTXiIaieNojFkvSmmvj2NvHwXbAMEEDAnTVhdI6zww+RyaewPJ9g9urKwRtC9NyuLO6zuDe3RSki7YCCK1B6/92IRCmBaEohmUQb85iKe2vVIqbdenaDOubCoFg8OWnyJ8eRXo+QeGDAIQBmOAp3nrxDfDgz/wMAuDeUFL31LewXZGEgkFeOfoYyT2NLE/cxGpvpuvQAbTvUcXgyd6H0VWH3q5+Jm78tiH431pnvCGeSzZxsKODvQM9mKEwSkne/+Ir5pYXiVgRpCoSCcY4NX3paw1D/wJx5WDqjkxa0wAAAABJRU5ErkJggg==&logoWidth=16) ![JAPANESE](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgame.mahjongsoul.com%2Fversion.json&label=JAPANESE&query=$.version&color=FF8C00&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAA7EAAAOxAGVKw4bAAADT0lEQVQ4jUXN2WtcVQDA4d+520xmsbOkM5OYNJkak5hJNQtE2mCgkj6ILUVEoTSIG0KVgpT4oIjig4qi5k0U8cWttr5IoUGoFBrRSilN1DRdNBMbkzTNNklmJplz7tx7fPDB7x/4BMDJZ0/kDw4fznquj1/1AM3Ia5/hyQpVDQDzi7OkExl2ptLUJOKcuzbO2V8vCOv1x+s/MKans3LuIyIdRynd0ly7uoTcKpPt7mN2coKqlLRm2/B8jTYExcIa+1v28Ol7J7TIf9hRCaVigfDunQR2JHA3lxl+qYxhaBKpDCuLC3QPPgJas3j9KoZpQjhMOl1H+K4Y1sJs0agrCUztM/zxGMeH2gjYEaSSzM3O4FgO4+dGEQLC4Si1u5qRrqK0WUQrhTW3IrmnM45lC159vp1kMoowobauntvzc9i2hVKKUDiMcl0W/84jXUm5JowhQIzk7leTRW0fGfA4m0/QfsegIRpgNKDJZOqZmvmdvs5u1gvbuK6ivFXGlRLbMBGAtb5hkAraXPzRZSkh6acGUXbZdMu8eWyIny63MDVxk3+W5onVxHBxaWxuZGlhhYrcRjzduU/llGl3KY0SJnlHcysTx/VW+eP6DZoMh0LI4eT571GywtTYz1y8fIWp8VlCdg1W0AkS3VYULJMzVolUIkMgaPHOyLv8cPo8k59/SeqhfRTXitS2t/DgkQYSjfWE1Rl+ufIXljAMqgEHp1RBahfTsdHKRxgWj77wBLmeNpr2H0AIF9Bow+C7T74l29fL1tgkVkVJNu7OMDjQT/TUN6B9TMNEBwJQkTQ/cB+itASRHSAEIGgtbhOrzbArlUYcasqpunjSLhTXiIaieNojFkvSmmvj2NvHwXbAMEEDAnTVhdI6zww+RyaewPJ9g9urKwRtC9NyuLO6zuDe3RSki7YCCK1B6/92IRCmBaEohmUQb85iKe2vVIqbdenaDOubCoFg8OWnyJ8eRXo+QeGDAIQBmOAp3nrxDfDgz/wMAuDeUFL31LewXZGEgkFeOfoYyT2NLE/cxGpvpuvQAbTvUcXgyd6H0VWH3q5+Jm78tiH431pnvCGeSzZxsKODvQM9mKEwSkne/+Ir5pYXiVgRpCoSCcY4NX3paw1D/wJx5WDqjkxa0wAAAABJRU5ErkJggg==&logoWidth=16)

## 📢 用前须知

注意：解锁人物仅在本地有效，别人还是只能看到你原来的角色，发表情也是原来角色的表情。比如使用新角色发第 3 个表情，实际上其他人看到的是原来角色的第 3 个表情。

> [!CAUTION]
> 魔改千万条，安全第一条。
>
> 使用不规范，账号两行泪。
>
> 本项目仅供学习参考交流，请使用者于下载 24 小时内自行删除，不得用于商业用途，否则后果自负。
>
> 雀魂官方可能会检测并封号，如产生任何后果与作者无关。
>
> 使用本项目则表示你已知悉并同意以上条款。

![放铳放铳](https://memeprod.ap-south-1.linodeobjects.com/user-gif-post/1647655593730.gif)

### ✈️ Telegram 频道 & 交流群

| 频道                                                                                                               | 交流群                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| [![频道 https://t.me/Mahjong_Soul](https://s2.loli.net/2022/11/08/4vS2BLMGhudkXQy.jpg)](https://t.me/Mahjong_Soul) | [![交流 https://t.me/Mahjong_Soul_Chat](https://s2.loli.net/2022/11/08/KL8A7U9fDsZEmjp.jpg)](https://t.me/Mahjong_Soul_Chat) |

可以直接点击图片进入，也可以通过扫码进入。

### ☕ 请作者喝咖啡

-   [点我为作者发电（爱发电，支持微信/支付宝）](https://afdian.com/a/Avenshy)
-   [点我为作者发电（Patreon，支持信用卡/Paypal）](https://patreon.com/Avenshy)

再次重申：本程序完全免费使用，没有收费功能，请喝咖啡完全自愿，作者非常感谢您！

## 🥰 当前功能

程序包含三部分：包括 `mod` 、 `helper` 和 `replace` ，可以说是 [雀魂 mod_plus](https://github.com/Avenshy/majsoul_mod_plus) 和 [mahjong-helper-majsoul-mitmproxy](https://github.com/Avenshy/mahjong-helper-majsoul-mitmproxy) 的融合和升级。

程序默认配置为启用 `mod`、禁用 `helper` 和 `replace` 。如需自定义，请修改 `config/settings.yaml` 中的 `plugin_enable`。

### `mod` 功能

- [x] 解锁所有角色与皮肤
- [x] 解锁所有装扮
- [x] 解锁所有语音（报菜名）
- [x] 解锁所有称号
- [x] 解锁所有加载 CG
- [x] 解锁所有表情（不推荐开启）
- [x] 强制启用便捷提示
    -   由于雀魂本身代码限制，王座无法正常启用便捷提示，因此，**开启此功能后进入王座对局，左上角会变成 “玉之间”**。请注意，这不是 BUG！
- [x] 支持星标角色
- [x] 自定义名称
- [x] 显示玩家所在服务器
- [x] 显示主播 / Pro 标识
- [ ] 地铁模式
-   TODO……

### `helper` 功能

-   将对局发送到 [mahjong-helper（雀魂小助手）](https://github.com/EndlessCheng/mahjong-helper)

### `replace` 功能

-   替换游戏资源文件，仅支持网页版。
  
## 🧐 使用说明

### 视频教程（老方法，不推荐）

[雀魂 MAX 使用教程，2 分钟解锁所有角色皮肤装扮等](https://www.acfun.cn/v/ac44409913)

### 文字教程

1. 启动程序
    - 方式 1（懒人模式）：在 [Releases](https://github.com/Avenshy/MajsoulMax/releases/latest) 里下载，解压后直接运行 `run.exe`（Windows 限定）
    - 方式 2（源码运行）：在 `Python>=3.10` 环境下，打开命令行（PowerShell / 终端）
        ```shell
        # 下载源码
        git clone https://github.com/Avenshy/MajsoulMax.git
        # 安装依赖
        pip install -r requirements.txt
        # 安装依赖（国内清华源，如果上面那个太慢可以换这个）
        pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
        # 启动程序
        mitmdump -p 23410 -s addons.py
        ```
2. 关闭程序（`Ctrl+C`），修改配置，可自行根据程序提示和自身需求修改
3. 再次启动程序
4. 启动游戏，分为网页版和客户端 / Steam 端。需要确保雀魂相关流量会经过本地 `python` 代理（默认监听 `127.0.0.1:23410`），具体示例见下文 “代理与分流” 一节。
    - 网页版：通常只需让浏览器通过系统代理或规则分流使用 `python` 的代理节点，无需开启 `TUN` / 增强模式。
    - 客户端 / Steam 端：同样通过 `Clash` / `Surge` 将进程流量分流到 `python` 的代理节点，但需要在代理软件中开启 `TUN` / 增强模式，否则本地进程流量不会被劫持。
5. 登录游戏开始享受

## 🌐 代理与分流

`MajsoulMax` 默认在本地 `127.0.0.1:23410` 启动一个 HTTPS 代理（基于 mitmproxy）。推荐使用支持规则分流和覆写的代理软件（如 `Mihomo` 系的 `Clash Party` 或 `Clash Verge` / `Surge`），将雀魂相关流量导向该端口，并使用复合规则给 Python 进程做直连以避免回环。

### 信任证书

在配置分流规则前，请先在系统中导入并信任 `~/.mitmproxy/` 下的 `mitmproxy-ca-cert.cer` 证书。这个证书是本地自动生成的，非常安全。否则 HTTPS 流量可能会因为证书校验失败而无法正常工作。

#### Windows 用户

1. 开启文件资源管理器（按下 `Windows 键 + E`）
2. 在上方地址栏输入 `%homepath%\.mitmproxy`（mitmproxy 的默认证书存储路径）然后按 Enter
3. 找到名为 `mitmproxy-ca-cert.cer` 的证书文件
4. 双击该证书文件
5. 点选 `安装证书` 按钮
6. 若出现选项，请选 `本地计算机`，然后点选下一步
7. 选择 `将所有证书放入下列存储`，然后点 `浏览...`
8. 选择 `受信任的根证书颁发机构`，按下确定，再点选下一步与完成
9. 若系统要求权限，请点选是

#### macOS 用户

1. 打开 Finder
2. 按下 `Command + Shift + G` 打开前往文件夹对话框，输入 `~/.mitmproxy` 然后按 Enter
3. 找到名为 `mitmproxy-ca-cert.cer` 的证书文件
4. 双击该证书文件，进入钥匙串访问
5. 点选左边的 `系统钥匙串` 下的 `系统` 标签，右上角搜索 `mitmproxy`，找到导入的证书，此时是未信任状态
6. 右键名为 `mitmproxy` 的证书项，选择 `显示简介`，在弹出的窗口中展开 `信任`
7. 对于 `使用此证书时`，改为 `始终信任`
8. 关闭窗口，在弹出的认证框中完成认证即可。

#### iOS / iPadOS 用户

若你通过分离部署的形式将本项目改为了代理节点，则可以在 iOS / iPadOS 上使用，但此时仍需在对应设备上完成证书信任。

1. 首先将电脑上的 `mitmproxy-ca-cert.cer` 证书通过隔空传送或者其他方式发送到 iPhone/iPad 上，最好是隔空投送，可以自动完成导入。对于其他方式，须先保存到文件中，然后再在文件中点开该证书文件。
2. 进入 `设置-已下载描述文件`，点击安装
3. 前往 `通用-关于本机-证书信任设置`，打开 mitmproxy 的选项

#### Android 用户

无测试环境，可自行搜索。

> [!CAUTION]
>
> 本地客户端 / Steam 端等进程需要在代理软件中开启 `TUN` / 增强模式，才能保证进程流量经过 `python` 启动的代理节点；但请务必注意避免回环代理，即你要保证从 `python` 发出的流量不会被分流回自身。
>
> 网页版（浏览器）一般只要正确配置系统代理或域名规则即可，通常不需要开启增强模式。

### 使用 Clash / Surge 规则分流

以本地节点 `MajsoulMax`（HTTPS 127.0.0.1:23410）为例，规则中需要让 Python 进程直连，再把游戏 / 网页流量分流到该节点:

```yml
proxies:
    - name: MajsoulMax
      type: http
      server: 127.0.0.1
      port: 23410
      tls: true

proxy-groups:
    - name: 🀄 雀魂麻将
      type: select
      proxies:
          - MajsoulMax
          - DIRECT

rules:
    # 避免回环
    - AND, ((OR, ((PROCESS-NAME-REGEX, python.*?),(PROCESS-NAME, MajsoulMax.exe))), (OR, ((PROCESS-NAME,Jantama_MahjongSoul.exe),(PROCESS-NAME,雀魂麻將.exe),(DOMAIN-KEYWORD, majsoul), (DOMAIN-KEYWORD, maj-soul), (DOMAIN-KEYWORD, mahjongsoul), (DOMAIN-KEYWORD, catmjstudio)))), DIRECT
    # 客户端 / Steam
    - PROCESS-NAME,Jantama_MahjongSoul.exe,🀄 雀魂麻将
    - PROCESS-NAME,雀魂麻將.exe,🀄 雀魂麻将
    # 网页版
    - DOMAIN-KEYWORD,majsoul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,maj-soul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,mahjongsoul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,catmjstudio,🀄 雀魂麻将
```

在 Surge 中可写成:

```text
[Proxy]
MajsoulMax = https, 127.0.0.1, 23410

[Proxy Group]
🀄 雀魂麻将 = select, MajsoulMax, DIRECT

[Rule]
# 避免回环代理
AND, ((PROCESS-NAME, python*), (OR, ((DOMAIN-KEYWORD, majsoul), (DOMAIN-KEYWORD, maj-soul), (DOMAIN-KEYWORD, mahjongsoul), (DOMAIN-KEYWORD, catmjstudio)))), DIRECT
# 客户端 / Steam
PROCESS-NAME,雀魂麻將,🀄 雀魂麻将
# 网页版
DOMAIN-KEYWORD,majsoul,🀄 雀魂麻将
DOMAIN-KEYWORD,maj-soul,🀄 雀魂麻将
DOMAIN-KEYWORD,mahjongsoul,🀄 雀魂麻将
DOMAIN-KEYWORD,catmjstudio,🀄 雀魂麻将
```

### Clash Verge 全局扩展脚本（JS）示例

参考 [官方文档](https://www.clashverge.dev/guide/script.html)，可以按照如下方法进行配置。

在 “订阅” 页面右键 `全局扩展脚本`，选择 “编辑文件”:

```js
function main(config) {
    config.proxies.push({
        name: 'MajsoulMax',
        type: 'http',
        server: '127.0.0.1',
        port: 23410,
        tls: true,
    });

    config['proxy-groups'].push({
        name: '🀄 雀魂麻将',
        type: 'select',
        proxies: ['DIRECT', 'MajsoulMax'],
        icon: 'https://www.maj-soul.com/homepage/img/logotaiwan.png',
    });

    const bypass = [
        'AND, ((OR, ((PROCESS-NAME-REGEX, python.*?),(PROCESS-NAME, MajsoulMax.exe))), (OR, ((PROCESS-NAME,Jantama_MahjongSoul.exe),(PROCESS-NAME,雀魂麻將.exe),(DOMAIN-KEYWORD, majsoul), (DOMAIN-KEYWORD, maj-soul), (DOMAIN-KEYWORD, mahjongsoul), (DOMAIN-KEYWORD, catmjstudio)))), DIRECT',
    ];

    const clientRules = ['PROCESS-NAME,Jantama_MahjongSoul.exe,🀄 雀魂麻将', 'PROCESS-NAME,雀魂麻將.exe,🀄 雀魂麻将'];

    const webRules = [
        'DOMAIN-KEYWORD,majsoul,🀄 雀魂麻将',
        'DOMAIN-KEYWORD,maj-soul,🀄 雀魂麻将',
        'DOMAIN-KEYWORD,mahjongsoul,🀄 雀魂麻将',
        'DOMAIN-KEYWORD,catmjstudio,🀄 雀魂麻将',
    ];

    config.rules.unshift(...bypass, ...clientRules, ...webRules);
    return config;
}
```

### Clash Party（原 Mihomo Party）覆写 YAML 示例

参考 [官方文档](https://clashparty.org/docs/guide/override/yaml)，可以按照如下方式进行配置。

在 Clash Party 左侧 `覆写` 页面点击 `+` 号，选择 `新建 YAML`，然后复制如下内容，点击 `确认` 保存，然后点击对应覆写卡片右上角的 `...` 图标，选择 `编辑信息` - `全局启用`。

```yml
# https://mihomo.party/docs/guide/override/yaml
+proxies:
    - name: MajsoulMax
      type: http
      server: 127.0.0.1
      port: 23410
      tls: true
+proxy-groups:
    - name: 🀄 雀魂麻将
      proxies:
          - MajsoulMax
          - DIRECT
      type: select
+rules:
    - AND, ((OR, ((PROCESS-NAME-REGEX, python.*?),(PROCESS-NAME, MajsoulMax.exe))), (OR, ((PROCESS-NAME,Jantama_MahjongSoul.exe),(PROCESS-NAME,雀魂麻將.exe),(DOMAIN-KEYWORD,majsoul),(DOMAIN-KEYWORD,maj-soul),(DOMAIN-KEYWORD,mahjongsoul),(DOMAIN-KEYWORD,catmjstudio)))), DIRECT
    - PROCESS-NAME,Jantama_MahjongSoul.exe,🀄 雀魂麻将
    - PROCESS-NAME,雀魂麻將.exe,🀄 雀魂麻将
    - DOMAIN-KEYWORD,majsoul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,maj-soul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,mahjongsoul,🀄 雀魂麻将
    - DOMAIN-KEYWORD,catmjstudio,🀄 雀魂麻将
```

## 📄配置文件解释

### `settings.yaml`
这是主程序配置文件，用于存储插件配置和liqi依赖的更新信息。

```yml
# 插件配置，true为开启，false为关闭
plugin_enable:
  mod: true  # mod用于解锁全部角色、皮肤、装扮等
  helper: false  # helper用于将对局发送至雀魂小助手，不使用小助手请勿开启
  replace: false  # replace用于替换雀魂的游戏内容
# liqi用于解析雀魂消息
liqi:
  auto_update: true  # 是否自动更新
  github_token: '' # 仅供自己使用，请勿泄漏给任何人
  liqi_version: 'v0.11.210.w'  # 本地liqi文件版本
  liqi_hash: 'bda101be45d295fb525efd3c20124fa90cb39dd6fd2eca0aeb6e1dd086b6b622'  # 本地liqi文件hash
```

### `settings.mod.yaml`
这是mod的配置文件，大多数功能直接在游戏中设定即可，只有小部分无法在游戏中设定的，才在此处修改。

修改完成后需要重新启动MajsoulMax。

只有在启用mod插件后，才会生成该配置文件。

```yml
# 需要自定义的配置主要集中在这里，大多数无需修改，在游戏内设置即可更新
config:
  character: 200001  # 当前看板娘
  characters: {}  # 各角色使用的皮肤
  nickname: '' # 自定义你的名字
  star_chars: [] # 星标角色
  bianjietishi: false # 强制启用便捷提示，用于部分场没有宝牌指示、和牌指示等
  title: 0  # 当前使用的称号
  loading_image: [] # 加载CG
  emoji: false # 不建议开启，用于解锁角色全部emoji，如果你本身角色没有额外表情，在对局中却发送额外表情，这种行为相当于自爆卡车
  views: # 各装扮页的装扮
    0: []
    1: []
    2: []
    3: []
    4: []
    5: []
    6: []
    7: []
    8: []
    9: []
  views_index: 0 # 正在使用的装扮页
  show_server: true # 显示其他玩家所在服务器
  verified: 0 # 标识设置，0为无标识，1为主播标识，2为Pro标识，显示在名字后面
  anti_replace_nickname: true # 禁止将外服玩家设为默认名称，特殊时期必备
  random_character: # 对局随机角色皮肤
    enabled: false
    pool: []
# 资源文件lqc.lqbin的配置                            
resource:
  auto_update: true # 自动更新lqc.lqbin
  lqc_lqbin_version: 'v0.11.104.w' # lqc.lqbin文件版本
# 下面是游戏的资源文件内容，包括需要获得的角色、物品等，不需要修改，除非你要自定义
mod: {}
```
### `settings.helper.yaml`
这是helper的配置文件，若未更改过小助手的地址则无需手动修改。

修改完成后需要重新启动MajsoulMax。

只有在启用helper插件后，才会生成该配置文件。

```yml
config:
  api_url: https://localhost:12121/   # 小助手的地址
```
### `settings.replace.yaml`
这是replace的配置文件，用于存储需要进行替换的游戏文件地址，仅支持网页版，建议在替换前清除浏览器缓存，或在游戏页面使用 `Ctrl+F5` 刷新网页。

修改完成后需要重新启动MajsoulMax。

只有在启用replace插件后，才会生成该配置文件。

```yml
config:
  http: []
  lq: []
```
<details>

<summary>Example</summary>

例如，我需要替换如下3个文件，用于替换柚的足见独白动态皮肤：
- `https://game.maj-soul.com/1/v0.11.155.w/lang/base/extendRes/charactor/you_BL/spine/spine.skel.txt`
- `https://game.maj-soul.com/1/v0.11.155.w/lang/base/extendRes/charactor/you_BL/spine/spine.atlas.txt`
- `https://game.maj-soul.com/1/v0.11.155.w/lang/base/extendRes/charactor/you_BL/spine/you_bl.png`

可以直接在配置文件中填入这三个文件名：

```yml
config:
  http:
  - /spine.skel.txt
  - /spine.atlas.txt
  - /you_bl.png
  lq: []
```

并将这三个用于替换的文件，放入 `MajsoulMax/replace` 文件夹下即可。

但在这里会遇到一个问题，如果需要同时替换其他动态皮肤，这些动态皮肤同样也会使用 `spine.skel.txt` 和 `spine.atlas.txt` 文件，该如何避免冲突呢？

另外，我也希望在玩其他语言服务器时，同样也能将皮肤给替换掉。拿第一个文件 `spine.skel.txt` 来说，我们观察到不同服务器的地址虽然不同，但仍然有相同之处：
- CN: `https://game.maj-soul.com/1/v0.11.155.w/lang/base/extendRes/charactor/you_BL/spine/spine.skel.txt`
- EN: `https://mahjongsoul.game.yo-star.com/v0.11.155.w/en/extendRes/charactor/you_BL/spine/spine.skel.txt`
- JP: `https://game.mahjongsoul.com/v0.11.155.w/jp/extendRes/charactor/you_BL/spine/spine.skel.txt`

根据这些地址可以看出，末尾的 `charactor/you_BL/spine/spine.skel.txt` 这一段是相同的，因此在配置文件中可以据此进行填入：

```yml
config:
  http:
  - /charactor/you_BL/spine/spine.skel.txt
  - /charactor/you_BL/spine/spine.atlas.txt
  - /charactor/you_BL/spine/you_bl.png
  lq: []
```
而文件则需要根据配置文件进行放置，此时文件树如下：
```
MajsoulMax
├─ config
├─ plugin
├─ proto
├─ ...
└─ replace
   └─ charactor
      └─ you_BL
         └─ spine
            ├─ spine.skel.txt
            ├─ spine.atlas.txt
            └─ you_bl.png
```

最终效果如图所示：
<details>
    <summary>🔞NSFW🔞 小孩子不能点哦</summary>


顺便感谢yijyu老师制作的色色l2d动态皮肤，据说也有偿接各种改图，感兴趣的可以去[他的频道（@yijyuqos2）](https://t.me/yijyuqos2)看看

![image.png](https://s2.loli.net/2026/01/15/RZwfEaYVeHMzSId.png)

</details>


</details>

## 🤔Q&A

1. 为什么要自动更新 liqi 和 lqc.lqbin？更新失败有什么影响？

    - liqi:
        - 共有 3 个文件，包括 `liqi.json` 和根据其生成的 `liqi.proto` 和 `liqi.pb2.py`，用于解析雀魂 protobuf 消息
        - 如果更新失败，会导致部分消息无法解析（如更新后新活动的消息）
    - lqc.lqbin:
        - 用于获取全部角色、装扮、物品等游戏资源
        - 如果更新失败，会导致无法获取部分资源（如更新后的新角色、物品等）
    - 一般情况下，只有在游戏更新后才需要更新这些文件。
    - 如果自动更新失败，可以在 [AutoLiqi > Releases](https://github.com/Avenshy/AutoLiqi/releases/latest) 下载，并手动替换 `./proto` 文件夹下的同名文件

2. 如何同时启用代理？
    - 推荐使用支持规则和覆写的代理软件（如 `Clash` / `Surge` / `Clash Verge`），参考上文 “代理与分流” 添加本地节点，再把雀魂规则指向该节点。
    - 如果还需要机场 / VPN，可以将 `MajsoulMax` 节点放在游戏规则前，再在其他规则中继续使用原有节点；也可以写成单独覆写，需要玩雀魂时再启用。
3. 还有其它问题？
    - 提出你的 [Issue](https://github.com/Avenshy/MajsoulMax/issues)！
    - 在上方加入我们的 [Telegram 群](https://github.com/Avenshy/MajsoulMax?tab=readme-ov-file#%EF%B8%8Ftelegram%E9%A2%91%E9%81%93%E4%BA%A4%E6%B5%81%E7%BE%A4)
