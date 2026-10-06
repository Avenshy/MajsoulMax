"""Run from the project root: python -m unittest discover -s tests -v.

Exercises the actual mod/protocol frame processing without loading personal
configuration, accessing the network, or writing settings.
"""
import json
import unittest
from types import SimpleNamespace

import liqi_new
from plugin.mod import mod
from proto import basic_pb2, liqi_pb2


def request(method, data, msg_id=1):
    block = basic_pb2.BaseMessage(method_name=method, data=data.SerializeToString())
    return SimpleNamespace(content=b"\x02" + msg_id.to_bytes(2, "little") +
                           block.SerializeToString(), from_client=True)


def response(data, msg_id=1):
    block = basic_pb2.BaseMessage(data=data.SerializeToString())
    return SimpleNamespace(content=b"\x03" + msg_id.to_bytes(2, "little") +
                           block.SerializeToString(), from_client=False)


def notification(seat, content):
    data = liqi_pb2.NotifyGameBroadcast(seat=seat, content=content)
    block = basic_pb2.BaseMessage(method_name='.lq.NotifyGameBroadcast',
                                 data=data.SerializeToString())
    return SimpleNamespace(content=b"\x01" + block.SerializeToString(), from_client=False)


class EmojiTests(unittest.TestCase):
    def setUp(self):
        self.mod = mod.__new__(mod)
        self.mod.safe = {}
        self.mod.max_data = {'emoji': {}}
        self.mod.settings = {'config': {
            'character': 200050, 'characters': {200050: 400501},
            'random_character': {'enabled': False, 'pool': []},
            'bianjietishi': False, 'emoji': False, 'nickname': '', 'title': 0,
            'views': {0: []}, 'views_index': 0, 'verified': 0,
            'show_server': False, 'safe_mode': False,
        }}
        self.mod.SaveSettings = lambda: None
        self.protocol = liqi_new.LiqiProto()

    def process(self, message):
        modify, drop, content, inject, _ = self.mod.main(message, self.protocol)
        self.assertFalse(drop)
        self.assertFalse(inject)
        if modify:
            message.content = content
        self.protocol.parse(message)
        return message

    def auth(self, server_character=200001, enabled=None):
        self.process(request('.lq.FastTest.authGame',
                             liqi_pb2.ReqAuthGame(account_id=111)))
        data = liqi_pb2.ResAuthGame(seat_list=[222, 111, 333])
        player = data.players.add(account_id=111)
        player.character.charid = server_character
        if enabled is not None:
            player.character.enabled_emoji.extend(enabled)
        return self.process(response(data))

    def test_captured_unity_request_roundtrip(self):
        for server_character, prefix in ((200001, 10000), (200002, 20000),
                                         (20000107, 1070000)):
            self.auth(server_character)
            for index in range(9):
                with self.subTest(server=server_character, index=index):
                    payload = {'emo_id': 500000 + index, 'other': True}
                    message = self.process(request('.lq.FastTest.broadcastInGame',
                        liqi_pb2.ReqBroadcastInGame(content=json.dumps(payload),
                                                   except_self=True), 9))
                    self.assertEqual(message.content[:3], b"\x02\x09\x00")
                    block = basic_pb2.BaseMessage.FromString(message.content[3:])
                    self.assertEqual(block.method_name, '.lq.FastTest.broadcastInGame')
                    sent = liqi_pb2.ReqBroadcastInGame.FromString(block.data)
                    self.assertTrue(sent.except_self)
                    self.assertEqual(json.loads(sent.content),
                                     {'emo_id': prefix + index, 'other': True})
                    self.process(response(liqi_pb2.ResCommon(), 9))
                    self.assertNotIn(9, self.protocol.res_type)
                    # The live Unity broadcast includes both old and new fields.
                    message = self.process(notification(1, json.dumps(
                        {'emo_id': prefix + index, 'emo': index})))
                    block = basic_pb2.BaseMessage.FromString(message.content[1:])
                    shown = liqi_pb2.NotifyGameBroadcast.FromString(block.data)
                    self.assertEqual(json.loads(shown.content),
                                     {'emo_id': 500000 + index, 'emo': index})

    def test_unrelated_content_unchanged(self):
        self.auth()
        for content in ('{"emo":1}', '{"emo_id":500010}', '{"emo_id":99990001}',
                        '{"emo_id":10001}', '{"emo_id":"500001"}', 'bad JSON', '[]'):
            with self.subTest(content=content):
                message = request('.lq.FastTest.broadcastInGame',
                    liqi_pb2.ReqBroadcastInGame(content=content), 9)
                original = message.content
                self.process(message)
                self.assertEqual(message.content, original)
                self.process(response(liqi_pb2.ResCommon(), 9))

    def test_other_seat_unchanged(self):
        self.auth()
        message = notification(0, '{"emo_id":10001}')
        original = message.content
        self.process(message)
        self.assertEqual(message.content, original)

    def test_missing_game_snapshot_unchanged(self):
        message = request('.lq.FastTest.broadcastInGame',
            liqi_pb2.ReqBroadcastInGame(content='{"emo_id":500001}'))
        original = message.content
        self.process(message)
        self.assertEqual(message.content, original)

    def test_random_character_snapshot(self):
        self.mod.settings['config']['random_character'] = {
            'enabled': True, 'pool': [{'character_id': 200002, 'skin_id': 400201}]}
        self.auth()
        self.assertEqual(self.mod.safe['emoji_mapping']['local'], 200002)
        message = self.process(request('.lq.FastTest.broadcastInGame',
            liqi_pb2.ReqBroadcastInGame(content='{"emo_id":20001}'), 9))
        block = basic_pb2.BaseMessage.FromString(message.content[3:])
        self.assertEqual(json.loads(liqi_pb2.ReqBroadcastInGame.FromString(
            block.data).content)['emo_id'], 10001)

    def test_failed_reauth_clears_snapshot(self):
        self.auth()
        self.process(request('.lq.FastTest.authGame',
                             liqi_pb2.ReqAuthGame(account_id=222), 10))
        data = liqi_pb2.ResAuthGame()
        data.error.code = 1
        self.process(response(data, 10))
        self.assertNotIn('emoji_mapping', self.mod.safe)

    def test_missing_seat_does_not_rewrite_broadcast(self):
        self.auth()
        self.mod.safe['emoji_mapping']['seat'] = None
        message = notification(0, '{"emo_id":10001}')
        original = message.content
        self.process(message)
        self.assertEqual(message.content, original)

    def test_real_permissions_filter_local_list_and_map_mooncake(self):
        message = self.auth(enabled=list(range(10000, 10009)) + [99990007])
        block = basic_pb2.BaseMessage.FromString(message.content[3:])
        shown = liqi_pb2.ResAuthGame.FromString(block.data).players[0].character
        self.assertEqual(list(shown.enabled_emoji), list(range(500000, 500009)) + [99990005])
        self.assertEqual(list(shown.extra_emoji), [14])
        self.assertTrue(shown.is_upgraded)
        self.assertEqual(shown.skin, self.mod.settings['config']['characters'][200050])
        sent = self.process(request('.lq.FastTest.broadcastInGame',
            liqi_pb2.ReqBroadcastInGame(content='{"emo_id":99990005}'), 9))
        payload = liqi_pb2.ReqBroadcastInGame.FromString(basic_pb2.BaseMessage.FromString(sent.content[3:]).data)
        self.assertEqual(json.loads(payload.content)['emo_id'], 99990007)
        self.process(response(liqi_pb2.ResCommon(), 9))
        received = self.process(notification(1, '{"emo_id":99990007,"emo":14}'))
        payload = liqi_pb2.NotifyGameBroadcast.FromString(basic_pb2.BaseMessage.FromString(received.content[1:]).data)
        self.assertEqual(json.loads(payload.content), {'emo_id':99990005,'emo':14})

    def test_expired_limited_emoji_disappears_on_next_auth(self):
        self.auth(enabled=list(range(10000, 10009)) + [99990007])
        self.assertIn(99990005, self.mod.safe['emoji_mapping']['send'])
        self.auth(enabled=list(range(10000, 10009)))
        self.assertNotIn(99990005, self.mod.safe['emoji_mapping']['send'])


if __name__ == '__main__':
    unittest.main()
