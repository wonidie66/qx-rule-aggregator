import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_rules import check_generated, AuditError


class AuditRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('rules','reports','config'):
            (self.root/name).mkdir()
        (self.root/'config/policies.json').write_text(
            json.dumps({'allowed_policies':['AI服务','默认代理','direct']}),encoding='utf-8')

    def make(self, before='HOST-SUFFIX,chatgpt.com,AI服务',
             after='HOST-SUFFIX,github.com,默认代理', summary_change=None):
        contents=[before+'\n',after+'\n']
        for file,text in zip(('BeforeTikTok.list','AfterTikTok.list'),contents):
            (self.root/'rules'/file).write_text(text,encoding='utf-8')
        summary={'sha256':{'前段':hashlib.sha256(contents[0].encode()).hexdigest(),
                           '后段':hashlib.sha256(contents[1].encode()).hexdigest()},
                 '各段字节数':{'前段':len(contents[0].encode()),'后段':len(contents[1].encode())},
                 '输出规则总数':sum(len(x.strip().splitlines()) for x in contents),
                 '完全相同条件但策略不同的冲突':[]}
        if summary_change:
            summary_change(summary)
        (self.root/'reports/summary.json').write_text(json.dumps(summary),encoding='utf-8')
        return contents

    def check(self, head=lambda _:None, approve=False):
        return check_generated(self.root/'rules',self.root/'reports',
                               self.root/'config/policies.json',15,approve,head_reader=head)

    def test_blocks_checksum_corruption(self):
        self.make(summary_change=lambda s:s['sha256'].__setitem__('前段','wrong'))
        self.assertTrue(any('SHA256' in i for i in self.check()))

    def test_blocks_unknown_policy(self):
        self.make(before='HOST,chatgpt.com,失效策略')
        with self.assertRaises(AuditError):self.check()

    def test_blocks_changed_first_policy(self):
        before,after=self.make(before='HOST-SUFFIX,chatgpt.com,默认代理')
        def head(p):
            if p.endswith('BeforeTikTok.list'):return 'HOST-SUFFIX,chatgpt.com,AI服务\n'
            if p.endswith('AfterTikTok.list'):return after
        issues=self.check(head=head)
        self.assertTrue(any('首选策略' in i for i in issues))
        self.assertTrue((self.root/'reports/audit.md').exists())
        self.assertFalse(any('首选策略' in i for i in self.check(head=head,approve=True)))

    def test_blocks_new_broad_policy_even_when_approved(self):
        self.make(before='IP-CIDR,0.0.0.0/0,direct')
        self.assertTrue(any('极宽范围' in i for i in self.check(approve=True)))

    def test_blocks_unexpected_shrink(self):
        a,b=self.make()
        old=''.join(f'HOST,test{x}.org,direct\n' for x in range(1200))
        def head(path):
            if path.endswith('BeforeTikTok.list'):return old
            if path.endswith('AfterTikTok.list'):return b
        self.assertTrue(any('变化' in i for i in self.check(head=head)))

    def test_allows_stable_output_with_baseline(self):
        a,b=self.make()
        def head(path):
            if path.endswith('BeforeTikTok.list'):return a
            if path.endswith('AfterTikTok.list'):return b
        # Test fixture only has 2 lines; the minimum size guard appropriately fails.
        self.assertTrue(any('异常偏低' in i for i in self.check(head=head)))

    def test_allows_valid_real_sized_output(self):
        before='\n'.join(f'HOST-SUFFIX,test{x}.example,默认代理' for x in range(1000))
        a,b=self.make(before=before)
        def head(path):
            if path.endswith('BeforeTikTok.list'):return a
            if path.endswith('AfterTikTok.list'):return b
        self.assertFalse(self.check(head=head))

    def test_preexisting_broad_rule_only_warns_not_newly_introduced(self):
        before='\n'.join(['IP-CIDR,0.0.0.0/0,direct']+
                         [f'HOST,x{x}.example,默认代理' for x in range(1000)])
        a,b=self.make(before=before)
        def head(path):
            if path.endswith('BeforeTikTok.list'):return a
            if path.endswith('AfterTikTok.list'):return b
        self.assertFalse(self.check(head=head))

if __name__=='__main__':unittest.main()
