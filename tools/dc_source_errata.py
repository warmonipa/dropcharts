"""DC v2 source corrections verified in docs/dc-source-audit.md."""

from drop_data import SECTION_IDS


def correct_source_rows(parsed, difficulty):
    """Correct known source errors before translation; reject source drift."""
    rows = {row['name']: row for row in parsed['monsters']['Episode 1']}
    corrections = []
    if difficulty == 'Normal':
        corrections = [
            ('Delsaber', 'Pinkal', '1.367188%', '1.269531%'),
            ('Chaos Bringer', 'Pinkal', '1.269531%', '1.367188%'),
        ]
    elif difficulty == 'Very Hard':
        corrections = [
            ('Dark Belra', sid, '', '0.000429%')
            for sid in ('Greenill', 'Bluefull', 'Purplenum', 'Pinkal', 'Yellowboze', 'Whitill')
        ]
    for monster, sid, before, after in corrections:
        cell = rows[monster]['drops'][SECTION_IDS.index(sid)]
        if cell['rate'] != before:
            raise ValueError(f'DC source changed: {difficulty}/{monster}/{sid}: {cell}')
        cell['rate'] = after
