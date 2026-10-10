"""V1.9 首次发布审计：继承已验证 V1.8 基线，不绕过对新增宽范围规则的拦截。"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_rules import check_generated


class FirstPublishRiskBaselineTests(unittest.TestCase):
    def case(self, *, include_legacy=True, injected_rule=None, legacy_rule='HOST-SUFFIX,cn,direct'):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            out=root/'rules'/'v1.9'
            rep=root/'reports'/'v1.9'
            out.mkdir(parents=True)
            rep.mkdir(parents=True)
            (root/'config').mkdir()
            new_allowed=['direct','分流-海外通用']
            (root/'config'/'policies_v19.json').write_text(json.dumps({'allowed_policies':new_allowed}),encoding='utf-8')
            # 保证模拟生成结果超过低规模保护阈值。
            before='\n'.join(f'HOST-SUFFIX,test{i}.example,direct' for i in range(1010))+'\n'
            after='HOST-SUFFIX,cn,direct\n'
            if injected_rule:
                after += injected_rule+'\n'
            files={'前段':before,'后段':after}
            hashes={}
            sizes={}
            for seg,file in zip(('前段','后段'),('BeforeTikTok.list','AfterTikTok.list')):
                data=files[seg].encode('utf-8')
                (out/file).write_bytes(data)
                hashes[seg]=hashlib.sha256(data).hexdigest()
                sizes[seg]=len(data)
            summary={'sha256':hashes,'各段字节数':sizes,
                     '输出规则总数':1011+(1 if injected_rule else 0),
                     '完全相同条件但策略不同的冲突':[]}
            (rep/'summary.json').write_text(json.dumps(summary,ensure_ascii=False),encoding='utf-8')
            legacy_files={
                'rules/BeforeTikTok.list':'HOST-SUFFIX,legacy.example,direct\n',
                'rules/AfterTikTok.list':legacy_rule+'\n',
                'config/policies.json':json.dumps({'allowed_policies':['direct','默认代理']})
            } if include_legacy else {}
            issues=check_generated(out,rep,root/'config'/'policies_v19.json',
                                   15,False,head_reader=legacy_files.get,
                                   head_rule_prefix='rules/v1.9',
                                   head_report_prefix='reports/v1.9',
                                   report_version='V1.9')
            return issues, (rep/'audit.md').read_text(encoding='utf-8')

    def test_existing_v18_cn_rule_is_not_false_positive(self):
        issues,report=self.case()
        self.assertEqual(issues,[])
        self.assertIn('继承完全相同',report)
        self.assertIn('新出现极宽范围规则：0',report)

    def test_truly_new_broad_rule_remains_blocked(self):
        issues,report=self.case(injected_rule='HOST-SUFFIX,com,分流-海外通用')
        self.assertTrue(any('新增的极宽范围危险规则' in i for i in issues))
        self.assertIn('HOST-SUFFIX,com,分流-海外通用',report)

    def test_missing_legacy_baseline_fails_closed(self):
        issues,report=self.case(include_legacy=False)
        self.assertTrue(any('新增的极宽范围危险规则' in i for i in issues))
        self.assertIn('不豁免任何宽范围规则',report)

    def test_renamed_broad_rule_is_not_automatically_allowed(self):
        issues,_=self.case(legacy_rule='HOST-SUFFIX,cn,默认代理')
        self.assertTrue(any('新增的极宽范围危险规则' in i for i in issues))


if __name__=='__main__':
    unittest.main()
