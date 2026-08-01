"""Integration test for generated cross-language coordinates."""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import validate_alignment  # noqa: E402


class GeneratedAlignmentTest(unittest.TestCase):
    """Verify BB, DC, and NGC generated data remain parallel."""

    def test_all_versions_and_languages_are_aligned(self):
        errors, summaries = validate_alignment.validate_all()

        self.assertEqual(errors, [])
        self.assertEqual(set(summaries), {"bb", "dc", "ngc"})


if __name__ == "__main__":
    unittest.main()
