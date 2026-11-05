import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone, timedelta
from scripts.session_cli import (initialize_session, validate_session, authorize_create,
    record_voice_observation, record_browser_preflight, record_create_submission, record_generation)

class SimpleSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.now = datetime(2026,10,9,tzinfo=timezone.utc)
        self.path = Path(initialize_session(Path(self.temp.name), 'Room to move', 'song',
                            'Make space after pressure', now=self.now, output_mode='simple')['session_dir'])
        self.cells = ['Give me room to move', 'Let the light come through']
        (self.path/'prompt.md').write_text('An intimate song opening into movement. Preserve and loop:\n'+ '\n'.join(self.cells)+'\nWrite the remainder.', encoding='utf-8')
        (self.path/'hook-cells.json').write_text(json.dumps(self.cells), encoding='utf-8')
        (self.path/'review.md').write_text('SCOPE: prompt\nREVIEWER: craft-review\nEVIDENCE: Exact repeated cells fit the movement premise and the sparse opening.\nVERDICT: PASS\nHARD VETOES: none\n',encoding='utf-8')
    def authorize(self):
        return authorize_create(self.path,'create-one','operator-request',
                                (self.now+timedelta(hours=1)).isoformat(),now=self.now)
    def observe_voice(self):
        record_voice_observation(self.path,'not_applicable','generic vocal',
                                 'Simple UI has generic vocals with no persona control',
                                 'no persona selector visible',now=self.now)
    def preflight(self,mode='simple'):
        return record_browser_preflight(self.path,'create-one','observed-model',mode,
                                        'redacted-ui-receipt','a'*64,now=self.now)
    def test_exact_cells_without_full_lyrics_or_score_are_valid(self):
        self.assertTrue(validate_session(self.path)['ready_for_suno'])
        self.assertFalse((self.path/'lyrics.md').exists())
    def test_mismatched_cell_and_audio_scope_are_rejected(self):
        (self.path/'hook-cells.json').write_text(json.dumps(['changed line',self.cells[1]]))
        self.assertFalse(validate_session(self.path)['ready_for_suno'])
        (self.path/'hook-cells.json').write_text(json.dumps(self.cells))
        (self.path/'review.md').write_text('SCOPE: audio\nREVIEWER: x\nEVIDENCE: x\nVERDICT: PASS\nHARD VETOES: none\n')
        self.assertFalse(validate_session(self.path)['ready_for_suno'])
    def test_mode_and_voice_are_observed_before_spend(self):
        self.authorize()
        with self.assertRaises(RuntimeError): self.preflight()
        self.observe_voice()
        with self.assertRaises(RuntimeError): self.preflight('custom')
        self.preflight()
        action=record_create_submission(self.path,'create-one',now=self.now)
        self.assertEqual(action['mode'],'simple')
        with self.assertRaises(RuntimeError): record_create_submission(self.path,'create-one',now=self.now)
        receipt=record_generation(self.path,'https://suno.com/song/take-one','take-one',1,'Observed result',
                                  'create-one','observed-model','Room to move',mode='simple',now=self.now)
        self.assertEqual(receipt['create_action']['mode'],'simple')
    def test_edited_prompt_invalidates_authorization(self):
        self.authorize();self.observe_voice()
        with (self.path/'prompt.md').open('a') as f:f.write('\nChange the drum pocket.')
        with self.assertRaises(RuntimeError):self.preflight()
    def test_instrumental_has_zero_cells_and_meditation_keeps_script_lane(self):
        path=Path(initialize_session(Path(self.temp.name),'Still room','instrumental','Quiet movement',output_mode='simple')['session_dir'])
        (path/'prompt.md').write_text('Quiet instrumental, no vocals, suspended piano and a soft ending.')
        (path/'review.md').write_text((self.path/'review.md').read_text())
        self.assertTrue(validate_session(path)['ready_for_suno'])
        with self.assertRaises(ValueError): initialize_session(Path(self.temp.name),'Guidance','meditation','Return gently',output_mode='simple')
    def test_legacy_api_default_and_unknown_mode(self):
        legacy=initialize_session(Path(self.temp.name),'Legacy','song','Keep original contract')['manifest']
        self.assertEqual(legacy['schema_version'],5)
        data=json.loads((self.path/'manifest.json').read_text());data['output_mode']='invented'
        (self.path/'manifest.json').write_text(json.dumps(data))
        self.assertFalse(validate_session(self.path)['ready_for_suno'])
