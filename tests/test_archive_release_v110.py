"""更新历史索引的回归测试：每次实质发布保留快照，不记录空更新。"""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from scripts.archive_release_v110 import TITLE, build_snapshot, save


class ArchiveReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.history = self.root / 'history'
        self.summary = self.root / 'summary.json'
        self.data = {
            '来源文件数': 105, '输出规则总数': 22019,
            'sha256': {'前段': 'a' * 64, '后段': 'b' * 64},
            '完全相同条件但策略不同的冲突': [{}, {}],
        }
        self.summary.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')
        self.when = datetime(2026, 10, 10, 15, 30, tzinfo=timezone.utc)

    def test_saved_immutable_snapshot_and_index(self):
        changed = ['rules/v1.10/BeforeTikTok.list', 'reports/v1.10/audit.md']
        first = save(self.history, self.summary, changed, '123456', '42', 'wonidie66/qx-rule-aggregator', self.when)
        self.assertEqual(first.name, 'run-123456.md')
        text = first.read_text(encoding='utf-8')
        self.assertIn('SHA256', text)
        self.assertIn('22,019', text)
        self.assertIn('https://github.com/wonidie66/qx-rule-aggregator/actions/runs/123456', text)
        self.assertTrue((self.history / 'updates.md').read_text(encoding='utf-8').startswith(TITLE))
        self.assertEqual((self.history / 'updates.md').read_text(encoding='utf-8').count('123456'), 1)
        with self.assertRaises(ValueError):
            save(self.history, self.summary, changed, '123456', '42', 'wonidie66/qx-rule-aggregator', self.when)

        save(self.history, self.summary, ['reports/v1.10/priority_audit.md'],
             '123457', '43', 'wonidie66/qx-rule-aggregator', self.when)
        index = (self.history / 'updates.md').read_text(encoding='utf-8')
        self.assertEqual(index.count('/actions/runs/'), 2)
        self.assertIn('仅报告更新', index)

    def test_no_empty_publication_and_invalid_inputs(self):
        with self.assertRaises(ValueError):
            build_snapshot(self.data, [], '123', '1', 'wonidie66/qx-rule-aggregator', self.when)
        with self.assertRaises(ValueError):
            build_snapshot(self.data, ['rules/v1.10/BeforeTikTok.list'], 'bad', '1', 'wonidie66/qx-rule-aggregator', self.when)
        with self.assertRaises(ValueError):
            build_snapshot(self.data, ['.env'], '123', '1', 'wonidie66/qx-rule-aggregator', self.when)
        with self.assertRaises(ValueError):
            build_snapshot(self.data, ['reports/v1.10/audit.md'], '123', '1', 'bad-repo', self.when)

    def test_rule_changes_distinguish_report_only(self):
        _, rule_row, _ = build_snapshot(self.data, ['rules/v1.10/AfterTikTok.list'],
                                        '123', '1', 'wonidie66/qx-rule-aggregator', self.when)
        _, report_row, _ = build_snapshot(self.data, ['reports/v1.10/audit.md'],
                                          '124', '2', 'wonidie66/qx-rule-aggregator', self.when)
        self.assertIn('规则与报告更新', rule_row)
        self.assertIn('仅报告更新', report_row)


if __name__ == '__main__':
    unittest.main()
