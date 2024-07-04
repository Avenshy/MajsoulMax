from ruamel.yaml import YAML
from loguru import logger
import liqi_new
import requests
from struct import unpack
from proto import liqi_pb2, config_pb2, sheets_pb2, basic_pb2
from google.protobuf import json_format
from .update_liqi import get_version


class mod:
    def __init__(self):
        self.safe = {}
        self.yaml = YAML()
        self.LoadSettings()
        logger.success('已载入mod')

    def LoadSettings(self):
        self.settings = self.yaml.load('''\
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
# 资源文件lqc.lqbin的配置                            
resource:
  auto_update: true # 自动更新lqc.lqbin
  lqc_lqbin_version: 'v0.11.56.w' # lqc.lqbin文件版本
# 下面是游戏的资源文件内容，包括需要获得的角色、物品等，不需要修改，除非你要自定义
mod: {}
''')
        try:
            with open('./config/settings.mod.yaml', 'r', encoding='utf-8') as f:
                temp = YAML()
                localyaml = temp.load(f)
                for i in self.settings.keys():
                    if i in localyaml.keys():
                        for j in self.settings[i]:
                            if j in localyaml[i].keys():
                                self.settings[i][j] = localyaml[i][j]
        except:
            logger.warning(
                '未检测到mod配置文件，已生成默认配置，如需自定义mod配置请手动修改 ./config/settings.mod.yaml')
        if self.settings['resource']['auto_update']:
            logger.info('正在检测lqc.lqbin文件更新，请稍候……')
            try:
                self.update_resource()
            except:
                logger.critical('更新lqc.lqbin文件失败！可能会导致角色和物品不全！')
        with open('./proto/lqc.lqbin', 'rb') as f:
            self.load_lqc_lqbin(f.read())
        self.SaveSettings()

    def SaveSettings(self):
        with open('./config/settings.mod.yaml', 'w', encoding='utf-8') as f:
            self.yaml.dump(self.settings, f)

    def get_prefix(self, version):
        req = requests.get(
            f'https://game.maj-soul.com/1/resversion{version}.json', timeout=10)
        return req.json()['res']['res/config/lqc.lqbin']['prefix']

    def get_lqc_lqbin(self, prefix):
        req = requests.get(
            f'https://game.maj-soul.com/1/{prefix}/res/config/lqc.lqbin', timeout=10)
        return req.content

    def load_lqc_lqbin(self, lqc_lqbin):
        config_table = config_pb2.ConfigTables()
        config_table.ParseFromString(lqc_lqbin)
        self.settings['mod']['character'] = []
        self.settings['mod']['skin'] = []
        self.settings['mod']['title'] = []
        self.settings['mod']['item'] = []
        self.settings['mod']['loading_image'] = []
        self.settings['mod']['emoji'] = {}
        self.settings['mod']['endings'] = []
        for data in config_table.datas:
            class_words = f"{data.table}_{data.sheet}".split("_")
            class_name = "".join(name.capitalize() for name in class_words)
            match class_name:
                case 'ItemDefinitionCharacter':
                    pb = sheets_pb2.ItemDefinitionCharacter()
                    for item in data.data:
                        pb.ParseFromString(item)
                        # if pb.id not in self.settings['mod']['character']:
                        self.settings['mod']['character'].append(pb.id)
                case 'ItemDefinitionSkin':
                    pb = sheets_pb2.ItemDefinitionSkin()
                    for item in data.data:
                        pb.ParseFromString(item)
                        # if pb.id not in self.settings['mod']['skin']:
                        self.settings['mod']['skin'].append(pb.id)
                case 'ItemDefinitionTitle':
                    pb = sheets_pb2.ItemDefinitionTitle()
                    for item in data.data:
                        pb.ParseFromString(item)
                        # if pb.id not in self.settings['mod']['title']:
                        self.settings['mod']['title'].append(pb.id)
                case 'ItemDefinitionItem':
                    pb = sheets_pb2.ItemDefinitionItem()
                    for item in data.data:
                        pb.ParseFromString(item)
                        match pb.category:
                            case 5:
                                # if pb.id not in self.settings['mod']['item']:
                                self.settings['mod']['item'].append(pb.id)
                            # 加了就会无法变更称号 这到底是为什么呢
                            # case 7:
                            #     if pb.id not in self.settings['mod']['title']:
                            #         self.settings['mod']['title'].append(pb.id)
                            case 8:
                                if pb.id not in self.settings['mod']['loading_image']:
                                    self.settings['mod']['loading_image'].append(
                                        pb.id)
                case 'ItemDefinitionLoadingImage':
                    pb = sheets_pb2.ItemDefinitionLoadingImage()
                    for item in data.data:
                        pb.ParseFromString(item)
                        if pb.id not in self.settings['mod']['loading_image']:
                            self.settings['mod']['loading_image'].append(
                                pb.id)
                case 'CharacterEmoji':
                    pb = sheets_pb2.CharacterEmoji()
                    for item in data.data:
                        pb.ParseFromString(item)
                        if pb.charid not in self.settings['mod']['emoji'].keys():
                            self.settings['mod']['emoji'][pb.charid] = []
                        self.settings['mod']['emoji'][pb.charid].append(
                            pb.sub_id)
                case 'SpotRewards':
                    pb = sheets_pb2.SpotRewards()
                    for item in data.data:
                        pb.ParseFromString(item)
                        self.settings['mod']['endings'].append(pb.id)

    def update_resource(self):
        # 获取资源文件版本
        new_version = get_version()

        prefix = self.get_prefix(new_version['version'])

        # 校验版本是否相同
        if self.settings['resource']['lqc_lqbin_version'] == prefix:
            logger.success(f'lqc.lqbin文件无需更新，当前版本：{prefix}')
        else:
            # 更新lqc.lqbin
            lqc_lqbin = self.get_lqc_lqbin(prefix)
            with open('proto/lqc.lqbin', 'wb') as f:
                f.write(lqc_lqbin)
            self.settings['resource']['lqc_lqbin_version'] = prefix
            logger.success(f'lqc.lqbin文件更新成功：{prefix}')

    def main(self, message, liqi_proto):
        modify = False
        drop = False
        fake = False
        msg = b''
        inject = False
        inject_msg = b''
        from_client = message.from_client
        buf = message.content
        msg_type = liqi_new.MsgType(buf[0])
        msg_block = basic_pb2.BaseMessage()
        if msg_type == liqi_new.MsgType.Notify:
            # Notify没有msg_id
            msg_block.ParseFromString(buf[1:])
            method_name = msg_block.method_name
            match method_name:
                case '.lq.NotifyAccountUpdate':
                    data = liqi_pb2.NotifyAccountUpdate()
                    data.ParseFromString(msg_block.data)
                    if data.update.HasField('character'):
                        drop = True
                case '.lq.NotifyRoomPlayerUpdate':
                    modify = True
                    data = liqi_pb2.NotifyRoomPlayerUpdate()
                    data.ParseFromString(msg_block.data)
                    for p in data.player_list:
                        if p.account_id == self.safe['account_id']:
                            p.avatar_id = self.settings['config']['characters'][self.settings['config']['character']]
                            if self.settings['config']['nickname'] != '':
                                p.nickname = self.settings['config']['nickname']
                            p.title = self.settings['config']['title']
                        if self.settings['config']['show_server']:
                            p.nickname =self.get_zone_id(p.account_id)+p.nickname
                    for p in data.update_list:
                        if p.account_id == self.safe['account_id']:
                            p.avatar_id = self.settings['config']['characters'][self.settings['config']['character']]
                            if self.settings['config']['nickname'] != '':
                                p.nickname = self.settings['config']['nickname']
                            p.title = self.settings['config']['title']
                        if self.settings['config']['show_server']:
                            p.nickname =self.get_zone_id(p.account_id)+p.nickname
                case '.lq.NotifyGameFinishRewardV2':
                    modify = True
                    data = liqi_pb2.NotifyGameFinishRewardV2()
                    data.ParseFromString(msg_block.data)
                    for c in self.safe['characters']:
                        if c.charid == self.safe['main_character_id']:
                            c.exp = data.main_character.exp
                            c.level = data.main_character.level
                            break
                    data.main_character.add = 0
                    data.main_character.exp = 0
                    data.main_character.level = 5
                case '.lq.NotifyCustomContestSystemMsg':
                    if self.settings['config']['show_server']:
                        modify = True
                        data = liqi_pb2.NotifyCustomContestSystemMsg()
                        data.ParseFromString(msg_block.data)
                        for p in data.game_start.players:
                            p.nickname =self.get_zone_id(p.account_id)+p.nickname
        else:
            msg_id = unpack('<H', buf[1:3])[0]
            msg_block.ParseFromString(buf[3:])
            if msg_type == liqi_new.MsgType.Req:
                # Req类型必定是客户端发出的消息
                assert (from_client)
                assert (msg_id < 1 << 16)
                # assert (len(msg_block) == 2)
                assert (msg_id not in liqi_proto.res_type)
                method_name = msg_block.method_name
                # 根据method_name判断是否需要修改
                match method_name:
                    case '.lq.Lobby.changeMainCharacter':  # 修改看板娘
                        fake = True
                        data = liqi_pb2.ReqChangeMainCharacter()
                        data.ParseFromString(msg_block.data)
                        self.settings['config']['character'] = data.character_id
                        self.SaveSettings()
                    case '.lq.Lobby.changeCharacterSkin':  # 修改角色皮肤
                        fake = True
                        inject = True
                        data = liqi_pb2.ReqChangeCharacterSkin()
                        data.ParseFromString(msg_block.data)
                        # 保存角色和皮肤
                        self.settings['config']['characters'][data.character_id] = data.skin
                        self.SaveSettings()
                        update_data = liqi_pb2.NotifyAccountUpdate()
                        character = update_data.update.character.characters.add()
                        character.charid = data.character_id
                        character.skin = data.skin
                        character.exp = 0
                        character.is_upgraded = True
                        character.level = 5
                        character.rewarded_level.extend([1, 2, 3, 4, 5])
                        if self.settings['config']['emoji']:
                            character.extra_emoji.extend(
                                self.settings['mod']['emoji'][character.charid])
                        update_data_block = [{'id': 1, 'type': 'string', 'data': '.lq.NotifyAccountUpdate'.encode(
                        )}, {'id': 2, 'type': 'string', 'data': update_data.SerializeToString()}]
                        inject_msg = b'\x01' + \
                            liqi_new.toProtobuf(update_data_block)
                    case '.lq.Lobby.addFinishedEnding':  # 角色传记
                        drop = True
                    case '.lq.Lobby.updateCharacterSort':  # 角色星标
                        fake = True
                        data = liqi_pb2.ReqUpdateCharacterSort()
                        data.ParseFromString(msg_block.data)
                        # 保存星标角色
                        self.settings['config']['star_chars'] = list(data.sort)
                        self.SaveSettings()
                    case '.lq.Lobby.useTitle':  # 使用称号
                        fake = True
                        data = liqi_pb2.ReqUseTitle()
                        data.ParseFromString(msg_block.data)
                        self.settings['config']['title'] = data.title
                        self.SaveSettings()
                    case '.lq.Lobby.setLoadingImage':  # 加载CG
                        fake = True
                        data = liqi_pb2.ReqSetLoadingImage()
                        data.ParseFromString(msg_block.data)
                        # self.safe['loading_image'] = []
                        self.settings['config']['loading_image'] = list(
                            data.images)
                        self.SaveSettings()
                    case '.lq.Lobby.saveCommonViews':  # 保存装扮
                        fake = True
                        modify = True
                        data = liqi_pb2.ReqSaveCommonViews()
                        data.ParseFromString(msg_block.data)
                        views = json_format.MessageToDict(
                            data, including_default_value_fields=True, preserving_proto_field_name=True)
                        self.settings['config']['views'][views['save_index']
                                                         ] = views['views']
                        if views['is_use'] == 1:
                            self.settings['config']['views_index'] = views['save_index']
                        self.SaveSettings()
                    case '.lq.Lobby.useCommonView':  # 修改装扮页
                        data = liqi_pb2.ReqUseCommonView()
                        data.ParseFromString(msg_block.data)
                        self.settings['config']['views_index'] = data.index
                        self.SaveSettings()
                    case '.lq.Lobby.loginBeat':
                        data = liqi_pb2.ReqLoginBeat()
                        data.ParseFromString(msg_block.data)
                        self.contract = data.contract
                    case '.lq.Lobby.readAnnouncement':
                        data = liqi_pb2.ReqReadAnnouncement()
                        data.ParseFromString(msg_block.data)
                        if data.announcement_id == 666666:
                            fake = True
                    case '.lq.Lobby.receiveCharacterRewards':
                        fake = True



                if fake:
                    modify = True
                    data = liqi_pb2.ReqLoginBeat()
                    data.contract = self.contract
                    msg_block.method_name = '.lq.Lobby.loginBeat'
            elif msg_type == liqi_new.MsgType.Res:
                # Res类型必定是客户端收到的消息
                assert (not from_client)
                assert (len(msg_block.method_name) == 0)
                assert (msg_id in liqi_proto.res_type)
                method_name, liqi_pb2_res = liqi_proto.res_type[msg_id]
                # 根据method_name判断是否需要修改
                match method_name:
                    case '.lq.Lobby.fetchCharacterInfo':  # 获取角色和皮肤信息
                        modify = True
                        data = liqi_pb2.ResCharacterInfo()
                        data.ParseFromString(msg_block.data)
                        self.safe['main_character_id'] = data.main_character_id
                        self.safe['characters'] = data.characters
                        # self.safe['skins'] = data.skins
                        # self.safe['character_sort'] = data.character_sort
                        # START
                        data.ClearField('characters')
                        character_keys = self.settings['config']['characters'].keys(
                        )
                        for c in self.settings['mod']['character']:
                            character = data.characters.add()
                            character.charid = c
                            character.exp = 0
                            character.is_upgraded = True
                            character.level = 5
                            character.rewarded_level.extend([1, 2, 3, 4, 5])
                            if c not in character_keys:
                                self.settings['config']['characters'][c] = int(
                                    '40'+str(c)[4:6]+'01')
                            character.skin = self.settings['config']['characters'][c]
                            if self.settings['config']['emoji']:
                                character.extra_emoji.extend(
                                    self.settings['mod']['emoji'][character.charid])
                        data.ClearField('skins')
                        data.skins.extend(self.settings['mod']['skin'])
                        data.main_character_id = self.settings['config']['character']
                        data.ClearField('character_sort')
                        data.character_sort.extend(
                            self.settings['config']['star_chars'])
                        data.ClearField('hidden_characters')
                        data.ClearField('finished_endings')
                        data.ClearField('rewarded_endings')
                        data.finished_endings.extend(
                            self.settings['mod']['endings'])
                        data.rewarded_endings.extend(
                            self.settings['mod']['endings'])
                    case '.lq.Lobby.login' | '.lq.Lobby.oauth2Login':  # 登录时

                        modify = True
                        data = liqi_pb2.ResLogin()
                        data.ParseFromString(msg_block.data)
                        self.safe['account_id'] = data.account_id
                        self.safe['nickname'] = data.account.nickname
                        self.safe['skin'] = data.account.avatar_id
                        self.safe['title'] = data.account.title
                        self.safe['loading_image'] = data.account.loading_image
                        # START
                        if self.settings['config']['character'] in self.settings['config']['characters'].keys():
                            data.account.avatar_id = self.settings['config'][
                                'characters'][self.settings['config']['character']]
                        else:
                            data.account.avatar_id = int(
                                '40'+str(self.settings['config']['character'])[4:6]+'01')
                        for view in self.settings['config']['views'][self.settings['config']['views_index']]:
                            if view['slot'] == 5:
                                data.account.avatar_frame = view['item_id']
                        if self.settings['config']['nickname'] != '':
                            data.account.nickname = self.settings['config']['nickname']
                        data.account.title = self.settings['config']['title']
                        data.account.ClearField('loading_image')
                        data.account.loading_image.extend(
                            self.settings['config']['loading_image'])
                        data.account.verified = self.settings['config']['verified']
                    case '.lq.Lobby.createRoom':  # 友人房 创建房间
                        modify = True
                        data = liqi_pb2.ResCreateRoom()
                        data.ParseFromString(msg_block.data)
                        for p in data.room.persons:
                            p.character.is_upgraded = True
                            p.character.level = 5
                            if p.account_id == self.safe['account_id']:
                                p.avatar_id = self.settings['config']['characters'][self.settings['config']['character']]
                                p.character.charid = self.settings['config']['character']
                                p.character.exp = 0
                                p.character.rewarded_level.extend(
                                    [1, 2, 3, 4, 5])
                                p.character.skin = self.settings['config'][
                                    'characters'][self.settings['config']['character']]
                                if self.settings['config']['emoji']:
                                    p.character.extra_emoji.extend(
                                        self.settings['mod']['emoji'][p.character.charid])
                                if self.settings['config']['nickname'] != '':
                                    p.nickname = self.settings['config']['nickname']
                                p.title = self.settings['config']['title']
                                p.character.ClearField('views')
                                for view in self.settings['config']['views'][self.settings['config']['views_index']]:
                                    view_slot = p.character.views.add()
                                    json_format.ParseDict(view, view_slot)
                                p.verified = self.settings['config']['verified']
                            if self.settings['config']['show_server']:
                                p.nickname =self.get_zone_id(p.account_id)+p.nickname
                    case '.lq.FastTest.authGame':  # 进入麻将桌
                        modify = True
                        data = liqi_pb2.ResAuthGame()
                        data.ParseFromString(msg_block.data)
                        if self.settings['config']['bianjietishi']:
                            data.game_config.mode.detail_rule.bianjietishi = True
                            if data.game_config.meta.mode_id == 15 :
                                data.game_config.meta.mode_id =11
                            elif data.game_config.meta.mode_id == 16:
                                data.game_config.meta.mode_id =12
                            elif data.game_config.meta.mode_id == 25:
                                data.game_config.meta.mode_id =23
                            elif data.game_config.meta.mode_id == 26:
                                data.game_config.meta.mode_id =24
                    
                        for p in data.players:
                            p.character.level = 5
                            p.character.is_upgraded = True
                            p.character.rewarded_level.extend([1, 2, 3, 4, 5])
                            if p.account_id == self.safe['account_id']:
                                p.avatar_id = self.settings['config']['characters'][self.settings['config']['character']]
                                p.character.charid = self.settings['config']['character']
                                p.character.exp = 0
                                p.character.skin = self.settings['config'][
                                    'characters'][self.settings['config']['character']]
                                if self.settings['config']['emoji']:
                                    p.character.extra_emoji.extend(
                                        self.settings['mod']['emoji'][p.character.charid])
                                if self.settings['config']['nickname'] != '':
                                    p.nickname = self.settings['config']['nickname']
                                p.title = self.settings['config']['title']
                                p.ClearField('views')
                                for view in self.settings['config']['views'][self.settings['config']['views_index']]:
                                    view_slot = p.views.add()
                                    json_format.ParseDict(view, view_slot)
                                    if view['slot'] == 5:
                                        p.avatar_frame = view['item_id']
                                p.verified = self.settings['config']['verified']

                            if self.settings['config']['show_server']:
                                p.nickname =self.get_zone_id(p.account_id)+p.nickname
                    case '.lq.Lobby.fetchAccountInfo':  # 个人信息页和游戏结束
                        data = liqi_pb2.ResAccountInfo()
                        data.ParseFromString(msg_block.data)
                        if data.account.account_id == self.safe['account_id']:
                            modify = True
                            data.account.avatar_id = self.settings['config'][
                                'characters'][self.settings['config']['character']]
                            for view in self.settings['config']['views'][self.settings['config']['views_index']]:
                                if view['slot'] == 5:
                                    data.account.avatar_frame = view['item_id']
                            if self.settings['config']['nickname'] != '':
                                data.account.nickname = self.settings['config']['nickname']
                            data.account.title = self.settings['config']['title']
                            data.account.ClearField('loading_image')
                            data.account.loading_image.extend(
                                self.settings['config']['loading_image'])
                            data.account.verified = self.settings['config']['verified']
                        # if self.settings['config']['show_server']:
                        #     match self.get_zone_id(data.account.account_id):
                        #         case 0:
                        #             data.account.nickname = '[C' + b'\xef\xbb\xbf'.decode('utf-8') +'N]'+data.account.nickname
                        #         case 1:
                        #             data.account.nickname = '[JP]'+data.account.nickname
                        #         case 3:
                        #             data.account.nickname = '[EN]'+data.account.nickname
                        #         case _:
                        #             data.account.nickname = '[??]'+data.account.nickname
                    case '.lq.Lobby.fetchTitleList':  # 获取称号列表
                        modify = True
                        data = liqi_pb2.ResTitleList()
                        data.ParseFromString(msg_block.data)
                        # self.safe['title_list'] = data.title_list
                        data.ClearField('title_list')
                        data.title_list.extend(self.settings['mod']['title'])
                    case '.lq.Lobby.fetchRoom':  # 获取友人房信息
                        modify = True
                        data = liqi_pb2.ResSelfRoom()
                        data.ParseFromString(msg_block.data)
                        for p in data.room.persons:
                            p.character.is_upgraded = True
                            p.character.level = 5
                            p.character.rewarded_level.extend([1, 2, 3, 4, 5])
                            if p.account_id == self.safe['account_id']:
                                p.avatar_id = self.settings['config']['characters'][self.settings['config']['character']]
                                p.character.charid = self.settings['config']['character']
                                p.character.exp = 0

                                p.character.skin = self.settings['config'][
                                    'characters'][self.settings['config']['character']]
                                if self.settings['config']['emoji']:
                                    p.character.extra_emoji.extend(
                                        self.settings['mod']['emoji'][p.character.charid])
                                if self.settings['config']['nickname'] != '':
                                    p.nickname = self.settings['config']['nickname']
                                p.title = self.settings['config']['title']
                                p.character.ClearField('views')
                                for view in self.settings['config']['views'][self.settings['config']['views_index']]:
                                    view_slot = p.character.views.add()
                                    json_format.ParseDict(view, view_slot)
                                p.verified = self.settings['config']['verified']
                            if self.settings['config']['show_server']:
                                p.nickname =self.get_zone_id(p.account_id)+p.nickname
                    case '.lq.Lobby.fetchBagInfo':  # 获取背包
                        modify = True
                        data = liqi_pb2.ResBagInfo()
                        data.ParseFromString(msg_block.data)
                        self.safe['items'] = data.bag.items
                        data.bag.ClearField('items')
                        # 添加原背包物品
                        for item in self.safe['items']:
                            if item.item_id not in self.settings['mod']['item']:
                                myitem = data.bag.items.add()
                                myitem.item_id = item.item_id
                                myitem.stack = item.stack
                        # 添加其他物品
                        for id in self.settings['mod']['item']:
                            item = data.bag.items.add()
                            item.item_id = id
                            item.stack = 1
                        # 添加加载插图
                        for id in self.settings['mod']['loading_image']:
                            item = data.bag.items.add()
                            item.item_id = id
                            item.stack = 1
                    case '.lq.Lobby.fetchAllCommonViews':  # 获取装扮
                        modify = True
                        data = liqi_pb2.ResAllcommonViews()
                        data.use = self.settings['config']['views_index']
                        for i, view in self.settings['config']['views'].items():
                            views = data.views.add()
                            json_format.ParseDict(
                                {'index': i, 'values': view}, views)
                    case '.lq.Lobby.fetchAnnouncement':
                        modify = True
                        data = liqi_pb2.ResAnnouncement()
                        data.ParseFromString(msg_block.data)
                        MyAnnouncement = liqi_pb2.Announcement()
                        MyAnnouncement.title = '雀魂MAX载入成功'
                        MyAnnouncement.id = 666666
                        MyAnnouncement.header_image = 'internal://2.jpg'
                        MyAnnouncement.content = '<color=#f9963b>作者：Avenshy        版本：20240508</color>\n\
<b>本工具完全免费、开源，如果您为此付费，说明您被骗了！</b>\n\
<b>本工具仅供学习交流，请在下载后24小时内删除，不得用于商业用途，否则后果自负！</b>\n\
<b>本工具有可能导致账号被封禁，给猫粮充钱才是正道！</b>\n\n\
<color=#f9963b>开源地址：</color>\n\
<href=https://github.com/Avenshy/MajsoulMax>https://github.com/Avenshy/MajsoulMax</href>\n\n\
<color=#f9963b>请作者喝咖啡：</color>\n\
<href=https://afdian.net/a/Avenshy>爱发电，支持支付宝、微信</href>\n\
<href=https://patreon.com/Avenshy>Patreon，支持Paypal、信用卡</href>\n\
<color=#f9963b>再次重申：脚本完全免费使用，没有收费功能，请喝咖啡完全自愿，作者非常感谢您！</color>'
                        data.announcements.insert(0, MyAnnouncement)
                    case '.lq.Lobby.fetchInfo':  # 网页版特殊处理
                        modify = True
                        data = liqi_pb2.ResFetchInfo()
                        data.ParseFromString(msg_block.data)
                        
                        # 处理角色和皮肤
                        self.safe['main_character_id'] = data.character_info.main_character_id
                        self.safe['characters'] = data.character_info.characters
                        data.character_info.ClearField('characters')
                        character_keys = self.settings['config']['characters'].keys(
                        )
                        for c in self.settings['mod']['character']:
                            character = data.character_info.characters.add()
                            character.charid = c
                            character.exp = 0
                            character.is_upgraded = True
                            character.level = 5
                            character.rewarded_level.extend([1, 2, 3, 4, 5])
                            if c not in character_keys:
                                self.settings['config']['characters'][c] = int(
                                    '40'+str(c)[4:6]+'01')
                            character.skin = self.settings['config']['characters'][c]
                            if self.settings['config']['emoji']:
                                character.extra_emoji.extend(
                                    self.settings['mod']['emoji'][character.charid])
                        data.character_info.ClearField('skins')
                        data.character_info.skins.extend(
                            self.settings['mod']['skin'])
                        data.character_info.main_character_id = self.settings['config']['character']
                        data.character_info.ClearField('character_sort')
                        data.character_info.character_sort.extend(
                            self.settings['config']['star_chars'])
                        data.character_info.ClearField('hidden_characters')
                        data.character_info.ClearField('finished_endings')
                        data.character_info.ClearField('rewarded_endings')
                        data.character_info.finished_endings.extend(
                            self.settings['mod']['endings'])
                        data.character_info.rewarded_endings.extend(
                            self.settings['mod']['endings'])

                        # 处理背包
                        self.safe['items'] = data.bag_info.bag.items
                        data.bag_info.bag.ClearField('items')
                        # 添加原背包物品
                        for item in self.safe['items']:
                            if item.item_id not in self.settings['mod']['item']:
                                myitem = data.bag_info.bag.items.add()
                                myitem.item_id = item.item_id
                                myitem.stack = item.stack
                        # 添加其他物品
                        for id in self.settings['mod']['item']:
                            item = data.bag_info.bag.items.add()
                            item.item_id = id
                            item.stack = 1
                        # 添加加载插图
                        for id in self.settings['mod']['loading_image']:
                            item = data.bag_info.bag.items.add()
                            item.item_id = id
                            item.stack = 1

                        # 处理装扮
                        data.ClearField('all_common_views')
                        data.all_common_views.use = self.settings['config']['views_index']
                        for i, view in self.settings['config']['views'].items():
                            views = data.all_common_views.views.add()
                            json_format.ParseDict(
                                {'index': i, 'values': view}, views)
                        # 处理称号
                        data.ClearField('title_list')
                        data.title_list.title_list.extend(self.settings['mod']['title'])
                    case '.lq.Lobby.fetchServerSettings':
                        data = liqi_pb2.ResServerSettings()
                        data.ParseFromString(msg_block.data)
                        if self.settings['config']['anti_replace_nickname']:
                            modify = True
                            data.settings.nickname_setting.enable = 0
                            data.settings.nickname_setting.ClearField(
                                'nicknames')
                    case '.lq.Lobby.fetchGameRecord':
                        data = liqi_pb2.ResGameRecord()
                        data.ParseFromString(msg_block.data)
                        uuid = data.head.uuid
                        result = '发现读入牌谱！\n'
                        for account in data.head.accounts:
                            if account.account_id == self.safe['account_id']:
                                result+='（自己）'
                            result += f'{self.get_zone_id(account.account_id)}{account.nickname}\n\
账号id: {account.account_id}   加好友id: {self.encode_account_id2(account.account_id)}\n\
主视角牌谱链接: {uuid}_a{self.encode_account_id(account.account_id)}\n\
主视角牌谱链接（匿名）: {self.encodePaipuUUID(uuid)}_a{self.encode_account_id(account.account_id)}_2\n\n'
                        result+='注意：只有在同一服务器才能添加好友！'
                        logger.success(result)

            else:
                logger.error(f'unknown msgtype: {msg_type}')
        if modify:
            msg_block.data = data.SerializeToString()
            if msg_type == liqi_new.MsgType.Notify:
                msg = b'\x01' + msg_block.SerializeToString()
            else:
                msg = buf[:3] + msg_block.SerializeToString()
            self.SaveSettings()

        return modify, drop, msg, inject, inject_msg

    def get_zone_id(self, id:int):
        i = id >> 23
        if 0 <= i <= 6:
            return '[C' + b'\xef\xbb\xbf'.decode('utf-8') + 'N]'
        elif 7 <= i <= 12:
            return '[JP]'
        elif 13 <= i <= 15:
            return '[EN]'
        else:
            return '[??]'
    def encodePaipuUUID(self,uuid) :
        result = ''
        code0=ord('0')
        codeA=ord('a')
        for i,char in enumerate(uuid):
            code = ord(char)
            temp = -1
            if code >= code0 and code0+ 10 > code :
                temp = code - code0
            elif code >= codeA and codeA + 26 > code:
                temp= code - codeA + 10
            if -1 != temp:
                temp = (temp + 17 + i) % 36
                if 10 > temp:
                    result += chr(temp + code0)
                else:
                    result +=  chr(temp + codeA - 10)
                
            else:
                result += char
        return result
    def encode_account_id(self,id:int) :
            return int((7 * id + 1117113 ^ 86216345) + 1358437)
        
    def encode_account_id2(self,p:int):
        p = 6139246 ^ p
        H = 67108863
        S = p & ~H
        Z = p & H
        for i in range(5):
            Z = (511 & Z) << 17 | Z >> 9
        return int(Z + S + 1e7)
    