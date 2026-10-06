"""Map only server-unlocked emojis to the local character's corresponding set."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _catalog():
    path = Path(__file__).resolve().parent.parent / 'config' / 'emoji_catalog.json'
    rows = json.loads(path.read_text(encoding='utf-8'))['rows']
    by_id = {}
    by_character = {}
    for emoji_id, index, kind, characters in rows:
        row = (emoji_id, index, kind)
        by_id[emoji_id] = row
        for character in characters.split(','):
            by_character.setdefault(int(character), []).append(row)
    return by_id, by_character


def unlocked_mapping(server_character, local_character, enabled_emoji):
    """Match by legacy index AND kind; shared emoji variants may have different IDs.

    enabled_emoji is copied from the original authGame response, before MOD
    changes skin/contract/extra_emoji. Never infer ownership from local settings.
    Older protocol responses without this list retain only basic emojis.
    """
    by_id, by_character = _catalog()
    allowed = list(enabled_emoji) or [
        (server_character % 100000) * 10000 + index for index in range(9)]
    local_rows = by_character.get(local_character, [])
    local_ids = {row[0] for row in local_rows}
    candidates = {}
    for emoji_id, index, kind in local_rows:
        if index is not None:
            candidates.setdefault((index, kind), []).append(emoji_id)
    forward = {}
    for remote_id in allowed:
        if server_character == local_character or remote_id in local_ids:
            forward[remote_id] = remote_id
            continue
        remote = by_id.get(remote_id)
        if remote is None or remote[1] is None:
            continue
        matches = candidates.get((remote[1], remote[2]), [])
        if len(matches) == 1:
            forward[matches[0]] = remote_id
    reverse = {remote: local for local, remote in forward.items()}
    indices = [by_id[local][1] for local in forward if local in by_id
               and by_id[local][1] is not None and by_id[local][1] > 8]
    return forward, reverse, indices


def remap_content(content, mapping):
    try:
        payload = json.loads(content)
    except (ValueError, TypeError):
        return None
    if not isinstance(payload, dict) or type(payload.get('emo_id')) is not int:
        return None
    original = payload['emo_id']
    target = mapping.get(original)
    if target is None or target == original:
        return None
    payload['emo_id'] = target
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

