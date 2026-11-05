import json
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.validate_skill_contracts import validate
ROOT=Path(__file__).resolve().parents[1]
class SkillContractTests(unittest.TestCase):
    def test_live_source_graph(self):self.assertEqual(validate(ROOT),[])
    def test_unknown_route_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);shutil.copytree(ROOT/'docs',root/'docs');shutil.copytree(ROOT/'skills',root/'skills')
            path=root/'docs/WORKFLOW-CONTRACTS.json';data=json.loads(path.read_text());data['workflows'][0]['specialists'].append('absent-agent');path.write_text(json.dumps(data))
            self.assertTrue(any('absent-agent' in e for e in validate(root)))
