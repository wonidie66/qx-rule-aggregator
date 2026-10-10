"""验证 V1.9 版本目录隔离与策略名称迁移。"""
import json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from aggregate import load_manifest
from audit_rules import check_generated

class V19Tests(unittest.TestCase):
    def test_manifest_uses_only_declared_groups(self):
        import os
        # This test runs from repo root, also works for a local copy.
        root=Path.cwd()
        man=load_manifest(root/'sources_v19.json')
        allowed=set(json.loads((root/'config/policies_v19.json').read_text(encoding='utf-8'))['allowed_policies'])
        self.assertTrue(set(x['policy'] for x in man).issubset(allowed))
        self.assertTrue(len(man)>74)
        self.assertTrue(all(x['segment']=='后段' for x in man if x['tag'] in {'Wikipedia','LinkedIn','CSDN'}))

    def test_old_manifest_keeps_original_policy(self):
        root=Path.cwd()
        old=load_manifest(root/'sources.json')
        self.assertEqual(next(x['policy'] for x in old if x['tag']=='OpenAI'), 'AI服务')

    def test_default_audit_paths_are_backwards_compatible(self):
        # Do not alter existing V1.8 interface.
        import inspect
        self.assertIn('head_rule_prefix',inspect.signature(check_generated).parameters)
        self.assertEqual(inspect.signature(check_generated).parameters['head_rule_prefix'].default,'rules')

if __name__=='__main__':unittest.main()
