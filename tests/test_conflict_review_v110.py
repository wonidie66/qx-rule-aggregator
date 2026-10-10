"""V1.10.1 冲突分类报告回归测试：确保报告本身不改变规则。"""
import json
import unittest

from scripts.conflict_review_v110 import analyze, classify, markdown


def row(match, first, last, before='Scholar', after='China'):
    return {
        '匹配类型': 'HOST-SUFFIX', '匹配值': match,
        '先出现策略': first, '后出现策略': last,
        '先出现来源': before, '后出现来源': after,
    }


class ConflictReportTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(classify('分流-学术科研', 'direct'), '直连与代理重叠')
        self.assertEqual(classify('分流-AI服务', '分流-海外通用'), '不同代理策略重叠')
        self.assertEqual(classify('reject', 'direct'), '拦截与放行重叠')

    def test_count_records_vs_distinct_selectors(self):
        data = {'来源文件数': 105, '输出规则总数': 22019,
                '完全相同条件但策略不同的冲突': [
                    row('acm.org', '分流-学术科研', 'direct'),
                    row('acm.org', '分流-学术科研', '分流-海外通用', after='Proxy'),
                    row('openai.com', '分流-AI服务', '分流-海外通用', before='OpenAI', after='Proxy'),
                ]}
        report = analyze(data)
        self.assertEqual(report['summary']['跨策略重叠记录数'], 3)
        self.assertEqual(report['summary']['涉及独立选择器数'], 2)
        self.assertEqual(report['summary']['各类重叠数']['直连与代理重叠'], 1)
        self.assertIn('不自动删除或调整任何规则', markdown(report))

    def test_deterministic_and_no_input_mutation(self):
        data = {'来源文件数': 2, '输出规则总数': 10,
                '完全相同条件但策略不同的冲突': [
                    row('a.cn', 'direct', '分流-海外通用'),
                ]}
        before = json.dumps(data, sort_keys=True)
        self.assertEqual(markdown(analyze(data)), markdown(analyze(data)))
        self.assertEqual(json.dumps(data, sort_keys=True), before)

    def test_unexpected_fields_fail_closed(self):
        with self.assertRaises(ValueError):
            analyze({'完全相同条件但策略不同的冲突': [{'匹配值': 'x'}]})
        with self.assertRaises(ValueError):
            analyze({'完全相同条件但策略不同的冲突': None})

    def test_zero_conflict(self):
        report = analyze({'来源文件数': 1, '输出规则总数': 1,
                          '完全相同条件但策略不同的冲突': []})
        self.assertEqual(report['summary']['跨策略重叠记录数'], 0)
        self.assertEqual(report['top_pairs'], [])


if __name__ == '__main__':
    unittest.main()
