"""Test HTTP hooks without executing addons.py's startup/config side effects."""
import ast
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from loguru import logger
from mitmproxy import http
from plugin.unity_emoji import PATCH_TAG, patch_panel

ROOT = Path(__file__).resolve().parent.parent
module = ast.parse((ROOT / 'addons.py').read_text())
addon_class = next(node for node in module.body if isinstance(node, ast.ClassDef) and node.name == 'MajsoulMaxAddon')
GLOBALS = {'http': http, 'json': json, 'logger': logger, 'BASE_DIR': ROOT,
           'MOD_ENABLE': True, 'REPLACE_ENABLE': False}
exec(compile(ast.Module(body=[addon_class], type_ignores=[]), str(ROOT / 'addons.py'), 'exec'), GLOBALS)
MajsoulMaxAddon = GLOBALS['MajsoulMaxAddon']


def flow(path, body=b'original'):
    return SimpleNamespace(request=http.Request.make('GET', 'https://game.maj-soul.com'+path),
                           response=http.Response.make(200, body), metadata={})


class UnityEmojiTests(unittest.TestCase):
    def test_panel_filter_does_not_modify_skin_ownership(self):
        source = 'function UI_BlockEmo:InitRoom()local j=DesktopMgr.Inst:get_main_role_character_info()self.emos=EmojiMgr.GetUnlockEmojiList(j.charid)self:ShowEmo()end'
        patched = patch_panel(source)
        self.assertIn('j.enabled_emoji', patched)
        self.assertIn('allowed[emo.emoji_id]', patched)
        self.assertNotIn('skin_map', patched)
        with self.assertRaises(ValueError):
            patch_panel('return UI_BlockEmo')

    def test_panel_http_response_and_cache_headers(self):
        addon = MajsoulMaxAddon()
        addon.emoji_panel_assets['/assetbundles/ASTC/panel.majset'] = {'name':'panel.majset', 'url':'/assetbundles/ASTC/panel.majset'}
        request = flow('/assetbundles/ASTC/panel.majset')
        request.request.headers['if-none-match'] = 'old'
        addon.request(request)
        self.assertNotIn('if-none-match', request.request.headers)
        with patch('plugin.unity_emoji.patch_bundle', return_value=b'filtered'):
            addon.response(request)
        self.assertEqual(request.response.content, b'filtered')
        self.assertEqual(request.response.headers['x-majsoulmax-emoji-panel'], PATCH_TAG)

    def test_unrelated_responses_never_decode_content(self):
        class UnreadResponse:
            status_code = 200
            accessed = False
            @property
            def content(self):
                self.accessed = True
                raise AssertionError('unrelated response must not be decoded')
        addon = MajsoulMaxAddon()
        for path in ['/1/Build/game.wasm.gz', '/assetbundles/ASTC/texture.majset', '/1/image.png']:
            with self.subTest(path=path):
                request = flow(path)
                request.response = UnreadResponse()
                addon.response(request)
                self.assertFalse(request.response.accessed)

    def test_disabled_mod_and_other_hosts_are_untouched(self):
        addon = MajsoulMaxAddon()
        request = flow('/1/Build/game.loader.js')
        with patch.dict(GLOBALS, {'MOD_ENABLE': False}):
            addon.request(request)
            addon.response(request)
        self.assertEqual(request.response.content, b'original')
        request.request.host = 'example.com'
        addon.request(request)
        addon.response(request)
        self.assertEqual(request.response.content, b'original')

    def test_resource_patch_failure_preserves_original(self):
        request = flow('/assetbundles/ASTC/bundle_info_so.majset')
        with patch('plugin.unity_emoji.panel_bundle_names', side_effect=ValueError('changed format')):
            MajsoulMaxAddon().response(request)
        self.assertEqual(request.response.content, b'original')

    def test_asset_manifest_and_loader(self):
        addon = MajsoulMaxAddon()
        addon.emoji_panel_assets['/assetbundles/ASTC/panel.majset'] = {'name':'panel.majset', 'url':'/assetbundles/ASTC/panel.majset'}
        request = flow('/_majsoulmax/emoji-panel-assets')
        addon.request(request)
        self.assertEqual(json.loads(request.response.content)['tag'], PATCH_TAG)
        request = flow('/1/Build/game.loader.js', b'var createUnityInstance=function(){};')
        addon.response(request)
        self.assertIn(b'window.createUnityInstance = async', request.response.content)
        self.assertIn(b"key.endsWith('/' + asset.name)", request.response.content)

    def test_startup_deadline_and_cache_cancellation(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is needed for the browser bootstrap harness')
        for scenario in ['success_empty', 'success_write', 'already_patched', 'timeout_fetch', 'timeout_body', 'timeout_open', 'timeout_write']:
            with self.subTest(scenario=scenario):
                subprocess.run([node, str(ROOT / 'tests/fixtures/unity_emoji_bootstrap.cjs'),
                    str(ROOT / 'plugin/unity_emoji_bootstrap.js'), scenario],
                    check=True, capture_output=True, text=True, timeout=10)
