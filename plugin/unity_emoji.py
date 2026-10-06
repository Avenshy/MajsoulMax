"""Filter Unity's in-game emoji panel without changing skin ownership."""
import re
import warnings
from functools import lru_cache

PATCH_TAG = '__max_emoji_v1'
LUA_KEY = b'wrelupqezdfrqdsd'


def xor_lua(data):
    return bytes(value ^ LUA_KEY[i % len(LUA_KEY)] for i, value in enumerate(data))


def patch_panel(source):
    pattern = r'self\.emos=EmojiMgr\.GetUnlockEmojiList\((\w+)\.charid\)'
    def replace(match):
        character = match[1]
        return (match[0] + ';do local allowed={} '
                f'for _,id in ipairs({character}.enabled_emoji or {{}})do allowed[id]=true end;'
                'local filtered={} for _,emo in ipairs(self.emos)do '
                'if allowed[emo.emoji_id]then table.insert(filtered,emo)end end;'
                'self.emos=filtered end;')
    patched, count = re.subn(pattern, replace, source)
    if count != 1:
        raise ValueError('Unity emoji panel changed; expected one list initializer')
    return patched


@lru_cache(maxsize=8)
def patch_bundle(body):
    import UnityPy
    UnityPy.config.FALLBACK_UNITY_VERSION = '2022.3.62f2c1'
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='No valid Unity version found.*')
        env = UnityPy.load(body)
        changed = False
        for obj in env.objects:
            if obj.type.name == 'TextAsset':
                asset = obj.read()
                if asset.m_Name == 'UI_BlockEmo.lua':
                    raw = asset.m_Script.encode('utf-8', 'surrogateescape')
                    source = xor_lua(raw).decode('utf-8')
                    patched = xor_lua(patch_panel(source).encode('utf-8'))
                    asset.m_Script = patched.decode('utf-8', 'surrogateescape')
                    asset.save()
                    changed = True
        if not changed:
            raise ValueError('Unity emoji panel asset not found')
        return env.file.save(packer='lz4')


@lru_cache(maxsize=4)
def panel_bundle_names(body):
    import UnityPy
    UnityPy.config.FALLBACK_UNITY_VERSION = '2022.3.62f2c1'
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='No valid Unity version found.*')
        env = UnityPy.load(body)
        for obj in env.objects:
            if obj.type.name != 'MonoBehaviour':
                continue
            tree = obj.read_typetree()
            if 'assetInfos' not in tree or 'bundleInfos' not in tree:
                continue
            owners = {a['ownerBundleIndex'] for a in tree['assetInfos']
                      if a['assetPath'] == 'LuaByte/Lua/UI/UI_BlockEmo.lua.bytes'}
            return tuple(tree['bundleInfos'][owner]['name'] for owner in owners)
    raise ValueError('Unity emoji panel not found in resource index')
