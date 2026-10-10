"""V1.10 增量策略及首次发布审计回归测试。"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.audit_rules_v110 import check_generated

ROOT = Path(__file__).resolve().parents[1]

class V110Tests(unittest.TestCase):
    def test_count_and_order(self):
        s = json.loads((ROOT/'sources_v110.json').read_text(encoding='utf-8'))['sources']
        self.assertEqual(len(s),105)
        self.assertEqual(s[-2]['tag'],'Proxy')
        self.assertEqual(s[-1]['tag'],'China')
        self.assertEqual([x['tag'] for x in s if x['segment']=='前段'][-1],'抖音国内')
        self.assertEqual(len(set(x['url'] for x in s)),105)

    def test_groups_and_special_policy(self):
        s = json.loads((ROOT/'sources_v110.json').read_text(encoding='utf-8'))['sources']
        allowed = set(json.loads((ROOT/'config/policies_v110.json').read_text(encoding='utf-8'))['allowed_policies'])
        self.assertTrue({x['policy'] for x in s}.issubset(allowed))
        dic={x['tag']:x['policy'] for x in s}
        for tag, policy in [('Spotify','分流-海外音乐'),('PayPal','分流-跨境购物'),('Amazon','分流-跨境购物'),('抖音国内','direct'),('支付宝','direct')]:
            self.assertEqual(dic[tag],policy)

    def audit(self, *, legacy=True, broad=None, prior_v110=False):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td); out=d/'rules/v1.10'; rep=d/'reports/v1.10'; out.mkdir(parents=True); rep.mkdir(parents=True)
            before=''.join(f'HOST-SUFFIX,example{i}.test,direct\n' for i in range(1002))
            after='HOST-SUFFIX,cn,direct\n'
            if broad: after+=broad+'\n'
            payload={'前段':before,'后段':after}
            (rep/'summary.json').write_text(json.dumps({'sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in payload.items()},'各段字节数':{k:len(v.encode()) for k,v in payload.items()},'输出规则总数':1003+bool(broad),'完全相同条件但策略不同的冲突':[]}),encoding='utf-8')
            for k,p in [('前段','BeforeTikTok.list'),('后段','AfterTikTok.list')]: (out/p).write_text(payload[k],encoding='utf-8')
            old={'rules/v1.9/BeforeTikTok.list':'HOST-SUFFIX,old.test,direct\n','rules/v1.9/AfterTikTok.list':'HOST-SUFFIX,cn,direct\n','config/policies_v19.json':json.dumps({'allowed_policies':['direct']})} if legacy else {}
            if prior_v110: old.update({'rules/v1.10/BeforeTikTok.list':before,'rules/v1.10/AfterTikTok.list':after})
            result=check_generated(out,rep,ROOT/'config/policies_v110.json',15,False,head_reader=old.get,head_rule_prefix='rules/v1.10',head_report_prefix='reports/v1.10',report_version='V1.10')
            return result, (rep/'audit.md').read_text(encoding='utf-8')

    def test_legacy_cn_kept(self):
        issues,report=self.audit()
        self.assertFalse(issues,issues)
        self.assertIn('V1.9 稳定基线',report)

    def test_new_broad_rule_blocked(self):
        issues,report=self.audit(broad='HOST-SUFFIX,com,分流-海外通用')
        self.assertTrue(any('极宽范围' in x for x in issues))
        self.assertIn('HOST-SUFFIX,com,分流-海外通用',report)

    def test_missing_v19_baseline_fail_closed(self):
        issues,report=self.audit(legacy=False)
        self.assertTrue(any('极宽范围' in x for x in issues))

if __name__ == '__main__': unittest.main()
