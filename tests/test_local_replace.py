import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'scripts'))
from local_replace import replace

class ReplaceTests(unittest.TestCase):
    def test_private_sections_unmodified(self):
        original='''[policy]\nstatic = AI服务, 美国节点\n[filter_remote]\nhttps://cdn.jsdelivr.net/gh/blackmatrix7/ios_rule_script@master/rule/QuantumultX/Advertising/Advertising.list, tag=广告, force-policy=reject, enabled=true\nhttps://cdn.jsdelivr.net/gh/abc/xyz, tag=test, force-policy=AI服务\nhttps://cdn.jsdelivr.net/gh/Semporia/TikTok-Unlock@master/Quantumult-X/TikTok.list, tag=TikTok, force-policy=TikTok服务\nFILTER_LAN, tag=局域网, force-policy=direct, inserted-resource=true, enabled=true\n[filter_local]\nfinal, 默认代理\n[mitm]\npassphrase = PRIVATE\np12 = SECRET\n'''
        after=replace(original,'foo','bar')
        self.assertIn('passphrase = PRIVATE\np12 = SECRET',after)
        self.assertIn('rules/BeforeTikTok.list',after)
        self.assertIn('rules/AfterTikTok.list',after)
        self.assertIn('Semporia/TikTok-Unlock',after)
        self.assertNotIn('gh/abc/xyz',after)
        self.assertIn('FILTER_LAN',after)
        self.assertIn('force-policy=reject',after)
    def test_refuse_no_ad(self):
        with self.assertRaises(ValueError):
            replace('[filter_remote]\nFILTER_LAN, tag=LAN\n[mitm]\np12 = XXX\n','x','y')

if __name__=='__main__':unittest.main()
