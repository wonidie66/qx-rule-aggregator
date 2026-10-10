"""V1.10.2 分流静态覆盖、IP包含、输出不变的回归测试。"""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.analyze_rules_v1102 import analyze, save, direct_first_review

class V1102Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.a=self.root/'BeforeTikTok.list'
        self.b=self.root/'AfterTikTok.list'
        self.a.write_text('# 来源：AI\nHOST-SUFFIX,google.com,分流-海外通用\nHOST-SUFFIX,gemini.google.com,分流-AI服务\nHOST,api.gemini.google.com,分流-AI服务\nHOST-KEYWORD,gemini,分流-海外通用\nHOST-WILDCARD,*.google.com,分流-视频直播\nIP-CIDR,13.32.0.0/15,分流-跨境购物\nIP-CIDR,13.33.142.0/24,分流-流媒体解锁\n',encoding='utf-8')
        self.b.write_text('# 来源：国内\nHOST-SUFFIX,cn,direct\nHOST-SUFFIX,video.cn,分流-视频直播\nIP6-CIDR,2001:db8::/32,direct\nIP6-CIDR,2001:db8:1::/48,分流-海外通用\n',encoding='utf-8')

    def test_type_and_overlap(self):
        types,domain,ip=analyze(self.a,self.b)
        self.assertEqual(sum(types.values()),11)
        self.assertIn('关键词/域名',{r['关系'] for r in domain})
        self.assertIn('通配符/域名',{r['关系'] for r in domain})
        self.assertIn('域名/父级后缀',{r['关系'] for r in domain})
        self.assertEqual(len(ip),2)
        self.assertTrue(any('2001:db8' in x['A规则'] for x in ip))

    def test_output_is_read_only(self):
        old=(self.a.read_bytes(),self.b.read_bytes())
        out=self.root/'reports'
        save(self.a,self.b,out)
        for name in ['rule_types.md','domain_overlap.csv','ip_overlap.csv',
                     'priority_audit.md','priority_audit.json','rule_analysis_diff.md']:
            self.assertTrue((out/name).exists())
        d=json.loads((out/'priority_audit.json').read_text(encoding='utf-8'))
        self.assertEqual(d['rule_count'],11)
        self.assertFalse(d['baseline_found'])
        self.assertEqual(old,(self.a.read_bytes(),self.b.read_bytes()))

    def test_direct_first_candidates_file_order(self):
        _, domain, _ = analyze(self.a, self.b)
        examples = direct_first_review(domain)
        self.assertTrue(any(x['先出现规则'] == 'HOST-SUFFIX,cn' for x in examples))
        # 在文件中更早出现的直连父级规则需要单独列入人工复核。
        self.a.write_text(
            'HOST-SUFFIX,steamchina.com,direct\n'
            'HOST-SUFFIX,cdn.steamchina.com,分流-游戏平台\n',
            encoding='utf-8')
        self.b.write_text('HOST-SUFFIX,example.org,分流-海外通用\n', encoding='utf-8')
        _, domain, _ = analyze(self.a, self.b)
        findings = direct_first_review(domain)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['先出现规则'], 'HOST-SUFFIX,steamchina.com')
        self.assertEqual(findings[0]['后出现策略'], '分流-游戏平台')

    def test_bad_input_fail_closed(self):
        self.a.write_text('HOST,missing-policy\n',encoding='utf-8')
        with self.assertRaises(ValueError):
            analyze(self.a,self.b)

if __name__=='__main__':
    unittest.main()
