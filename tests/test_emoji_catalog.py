import unittest
from plugin.emoji import remap_content, unlocked_mapping


class CatalogTests(unittest.TestCase):
    def test_real_ichihime_mooncake_is_mapped_to_akagi_variant(self):
        enabled = list(range(10000, 10009)) + [99990007]
        forward, reverse, indices = unlocked_mapping(200001, 200050, enabled)
        assert forward == {**{500000 + i: 10000 + i for i in range(9)},
                           99990005: 99990007}
        assert reverse[99990007] == 99990005
        assert indices == [14]
        assert 500010 not in forward
        assert 501001 not in forward


    def test_contract_emojis_only_when_server_explicitly_unlocked(self):
        forward, reverse, indices = unlocked_mapping(
            200001, 200050, list(range(10000, 10009)) + [10010, 10011, 10012])
        assert forward[500010] == 10010
        assert forward[500011] == 10011
        assert forward[500012] == 10012
        assert indices == [10, 11, 12]


    def test_skin_emoji_without_correspondence_is_hidden(self):
        forward, _, _ = unlocked_mapping(200001, 200050, [10001, 11001])
        assert forward == {500001: 10001}


    def test_same_actual_character_keeps_owned_skin_emoji(self):
        forward, reverse, indices = unlocked_mapping(200001, 200001, [10001, 11001])
        assert forward == {10001: 10001, 11001: 11001}
        assert reverse == forward
        assert indices == [997]


    def test_old_snapshot_without_enabled_list_only_has_basics(self):
        forward, _, indices = unlocked_mapping(200001, 200050, [])
        assert len(forward) == 9
        assert not indices


    def test_character_with_missing_catalog_indices_still_has_all_basics(self):
        forward, _, indices = unlocked_mapping(200001, 20000126, list(range(10000, 10009)))
        assert forward == {1260000 + i: 10000 + i for i in range(9)}
        assert not indices


    def test_shared_variant_remapping_preserves_old_ordinal(self):
        assert remap_content('{"emo_id":99990007,"emo":14}',
                             {99990007: 99990005}) == '{"emo_id":99990005,"emo":14}'

