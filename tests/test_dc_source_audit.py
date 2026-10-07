"""DC v2 ingestion and generated-data regressions (see dc-source-audit.md)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from bs4 import BeautifulSoup
from drop_data import load_js_data
from parse_dc import DIFFICULTIES, parse_dc_cell, parse_dc_html
from dc_source_errata import correct_source_rows

FIXTURES = Path(__file__).parent / 'fixtures' / 'dc-v2'


class DcSourceAuditTest(unittest.TestCase):
    def test_malformed_rate_markup_is_not_an_item(self):
        for raw in ('40.625000%<', '0.781250%)', '>0.000191%'):
            td = BeautifulSoup(f'<td>Item<br>{raw}</td>', 'html.parser').td
            self.assertEqual(parse_dc_cell(td), {
                'item': 'Item', 'rate': raw.strip('<>)'),
            })

    def test_corrected_source_rates_reproduce_all_languages(self):
        for filename, difficulty in DIFFICULTIES:
            source = parse_dc_html((FIXTURES / filename).read_text(encoding='utf-8'))
            correct_source_rows(source, difficulty)
            expected = source['monsters']['Episode 1']
            self.assertEqual(len(expected), 45)
            for language in ('en', 'ja', 'zh'):
                data = load_js_data(ROOT / 'dc' / 'data' / f'{language}.js')
                actual = data['data'][difficulty]['monsters']['Episode 1']
                self.assertEqual(len(actual), len(expected))
                for a, e in zip(actual, expected):
                    self.assertEqual(a['dropRate'], e['dropRate'])
                    self.assertEqual([c['rate'] for c in a['drops']],
                                     [c['rate'] for c in e['drops']],
                                     (language, difficulty, a['name']))
                    for cell in a['drops']:
                        if cell['item']:
                            self.assertRegex(cell['rate'], r'^\d+(?:\.\d+)?%$')

    def test_v2_item_identities(self):
        data = load_js_data(ROOT / 'dc/data/en.js')['data']
        normal = data['Normal']['monsters']['Episode 1']
        hard = data['Hard']['monsters']['Episode 1']
        self.assertEqual(normal[33]['drops'][6]['item'], 'Dragon Frame')
        self.assertEqual(normal[33]['drops'][7]['item'], 'Lockgun')
        self.assertEqual([c['item'] for c in hard[29]['drops']],
                         ['HP/Generate'] * 5 + ['TP/Generate'] * 5)
        self.assertEqual(hard[32]['drops'][7]['item'], 'HP/Generate')
        for raw, expected in [('Dragonフレーム', 'Dragon Frame'),
                              ('ロックガン', 'Lockgun'),
                              ('ＨＰ/ジェネレイト', 'HP/Generate'),
                              ('ＴＰ/ジェネレイト', 'TP/Generate')]:
            td = BeautifulSoup(f'<td>{raw}<br>1%</td>', 'html.parser').td
            self.assertEqual(parse_dc_cell(td)['item'], expected)

    def test_corrected_rates_match_independent_v2_fractions(self):
        data = load_js_data(ROOT / 'dc/data/en.js')['data']
        normal = data['Normal']['monsters']['Episode 1']
        very_hard = data['Very Hard']['monsters']['Episode 1']
        self.assertEqual(normal[35]['drops'][5]['rate'], f'{100 * 13 / 1024:.6f}%')
        self.assertEqual(normal[43]['drops'][5]['rate'], f'{100 * 7 / 512:.6f}%')
        for sid_index in (1, 3, 4, 5, 8, 9):
            self.assertEqual(very_hard[39]['drops'][sid_index]['rate'],
                             f'{100 * 9 / 2097152:.6f}%')

    def test_corrected_identities_translate_without_changing_item(self):
        import json
        from build_i18n import build_translation_lookup, translate_name

        names = json.loads((ROOT / 'i18n_names.json').read_text())
        lookup = build_translation_lookup(names['monsters'], names['items'], {})['items']
        for item in ('Dragon Frame', 'Lockgun', 'HP/Generate', 'TP/Generate'):
            for language in ('ja', 'zh'):
                self.assertEqual(translate_name(item, lookup, language),
                                 names['items'][item][language])

    def test_changed_source_is_rejected(self):
        source = parse_dc_html((FIXTURES / 'n.html').read_text(encoding='utf-8'))
        source['monsters']['Episode 1'][35]['drops'][5]['rate'] = '99%'
        with self.assertRaisesRegex(ValueError, 'DC source changed'):
            correct_source_rows(source, 'Normal')
