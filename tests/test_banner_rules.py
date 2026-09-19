"""Ephinea named-banner boundaries and lossless multilingual generation."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from banner_rules import banner_hit, WEAPONS_BY_HIT, NON_WEAPONS
from drop_data import load_js_data, write_generated_js, iter_data_drops, cell_shape_errors
import mark_ss


class BannerRulesTest(unittest.TestCase):
    def test_named_weapons_and_thresholds(self):
        for hit, names in WEAPONS_BY_HIT.items():
            for name in names:
                self.assertEqual(banner_hit(name, 'monsters'), hit, name)
                self.assertIsNone(banner_hit(name, 'boxes'), name)
        self.assertEqual(banner_hit('Frozen Shooter', 'monsters'), 30)
        self.assertEqual(banner_hit('Spread Needle', 'monsters'), 40)
        self.assertEqual(banner_hit('Viridia Card', 'monsters'), 0)

    def test_non_weapons_and_exclusions(self):
        for name in NON_WEAPONS:
            for kind in ('monsters', 'boxes'):
                self.assertEqual(banner_hit(name, kind), 0)
        for name in ('Agito (1975)', 'Foie Lv30', 'Megid Lv30', 'Heart of Poumn',
                     'Heart of Morolian', 'Heart of Twin Chakram', 'Saber', 'Varista'):
            self.assertIsNone(banner_hit(name, 'monsters'), name)
        self.assertFalse(mark_ss.is_ss('Viridia Card'))
        self.assertTrue(mark_ss.is_ss('Psycho Wand'))

    def test_nested_generation_is_aligned_lossless_and_idempotent(self):
        sample = {'data': {'Ultimate': {'monsters': {'Episode 1': [
            {'name': 'Example', 'drops': [{'items': [
                {'item': 'Frozen Shooter', 'rate': '1/2', 'ss': True},
                {'item': 'Red Ring', 'rate': '1/64', 'bannerHit': 50},
                {'item': 'Agito (1975)', 'rate': '1/21', 'ss': True},
            ]}]}]}, 'boxes': {'Episode 1': [
            {'name': 'Forest 1', 'drops': [{'item': 'Vjaya', 'rate': '1/3', 'bannerHit': 50}]}]}}}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'bb/data').mkdir(parents=True)
            for lang in ('en', 'ja', 'zh'):
                data = copy.deepcopy(sample)
                if lang != 'en':
                    for i, drop in enumerate(iter_data_drops(data)):
                        drop['item'] = f'{lang}-{i}'
                write_generated_js(root / f'bb/data/{lang}.js', data, language=lang,
                                   generator='test', source='test')
            with patch.object(mark_ss, 'ROOT', root):
                self.assertEqual(mark_ss.mark_version('bb'), 2)
                once = {p: p.read_bytes() for p in (root / 'bb/data').glob('*.js')}
                mark_ss.mark_version('bb')
                self.assertEqual(once, {p: p.read_bytes() for p in once})
            for lang in ('en', 'ja', 'zh'):
                drops = list(iter_data_drops(load_js_data(root / f'bb/data/{lang}.js', lang)))
                self.assertEqual([d.get('ss', False) for d in drops], [False, True, False, False])
                self.assertEqual([d.get('bannerHit') for d in drops], [30, None, None, None])
                self.assertEqual([d['rate'] for d in drops], ['1/2', '1/64', '1/21', '1/3'])
                if lang != 'en':
                    self.assertEqual([d['item'] for d in drops], [f'{lang}-{i}' for i in range(4)])

    def test_invalid_metadata_is_rejected(self):
        self.assertTrue(cell_shape_errors({'item': 'X', 'rate': '1/2', 'bannerHit': True}))
        self.assertTrue(cell_shape_errors({'item': 'X', 'rate': '1/2', 'bannerHit': 30, 'ss': True}))


if __name__ == '__main__':
    unittest.main()
