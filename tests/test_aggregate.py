import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from aggregate import aggregate, parse_source, AggregationError


def mk(tag, policy):
    return {'tag':tag,'url':f'https://cdn.jsdelivr.net/{tag}.list','policy':policy,'segment':'前段'}


class AggregationTests(unittest.TestCase):
    def test_preserves_order_policy_and_flags(self):
        a=mk('A','direct'); b=mk('B','TikTok服务')
        parts, report=aggregate([a,b], lambda url: {
            a['url']:'HOST-SUFFIX,snssdk.com,OLD\nIP-CIDR,10.0.0.0/8,OLD,no-resolve',
            b['url']:'HOST,tiktok.com,old\nHOST-SUFFIX,snssdk.com,old',
        }[url])
        text=parts['前段']
        self.assertIn('HOST-SUFFIX,snssdk.com,direct',text)
        self.assertIn('HOST-SUFFIX,snssdk.com,TikTok服务',text)
        self.assertIn('IP-CIDR,10.0.0.0/8,direct,no-resolve',text)
        self.assertLess(text.find('HOST-SUFFIX,snssdk.com,direct'),text.find('HOST-SUFFIX,snssdk.com,TikTok服务'))
        self.assertEqual(len(report['完全相同条件但策略不同的冲突']),1)

    def test_removes_exact_duplicates_only(self):
        a=mk('A','默认代理');b=mk('B','默认代理')
        parts,report=aggregate([a,b], lambda _: 'HOST-SUFFIX,github.com,old')
        self.assertEqual(parts['前段'].count('HOST-SUFFIX,github.com,默认代理'),1)
        self.assertEqual(report['移除完全重复规则数'],1)
        self.assertEqual(report['输出规则总数'],1)

    def test_splits_before_after_tiktok(self):
        a=mk('Before','direct'); b=mk('After','默认代理')
        b['segment']='后段'
        parts,report=aggregate([a,b],lambda url: 'HOST,tiktok.com,old')
        self.assertIn('HOST,tiktok.com,direct',parts['前段'])
        self.assertIn('HOST,tiktok.com,默认代理',parts['后段'])
        self.assertEqual(len(report['完全相同条件但策略不同的冲突']),1)

    def test_rejects_unapproved_script_or_config(self):
        a=mk('A','direct')
        with self.assertRaises(AggregationError):
            parse_source('URL-REWRITE,^https://x,hi',a)
        with self.assertRaises(AggregationError):
            parse_source('[mitm]\npassphrase = foo',a)
        with self.assertRaises(AggregationError):
            parse_source('# only comments',a)

    def test_fail_closed_if_one_source_fails(self):
        a=mk('A','direct');b=mk('B','默认代理')
        def fetch(url):
            if url == b['url']:
                raise RuntimeError('下载失败')
            return 'HOST,example.org,direct'
        with self.assertRaises(AggregationError):
            aggregate([a,b],fetch)

if __name__=='__main__': unittest.main()
