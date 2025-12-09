"""
测试跨平台去重功能

测试内容：
1. 标题相似度计算（RapidFuzz）
2. URL标准化
3. 跨平台去重逻辑
"""

import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import (
    _calculate_title_similarity,
    _normalize_url,
    _deduplicate_cross_platform,
)


class TestTitleSimilarity(unittest.TestCase):
    """测试标题相似度计算"""

    def test_identical_titles(self):
        """测试完全相同标题"""
        title1 = "苹果发布新iPhone"
        title2 = "苹果发布新iPhone"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertEqual(similarity, 1.0, "完全相同标题应该返回1.0")

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        title1 = "苹果发布新iPhone"
        title2 = "苹果发布新IPHONE"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertEqual(similarity, 1.0, "大小写不同但内容相同应该返回1.0")

    def test_similar_titles(self):
        """测试相似标题"""
        title1 = "苹果发布新iPhone"
        title2 = "苹果发布新款iPhone"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertGreater(similarity, 0.8, "相似标题应该返回高相似度")

    def test_word_order_insensitive(self):
        """测试词序不敏感（RapidFuzz token_sort_ratio的优势）"""
        title1 = "苹果发布新手机"
        title2 = "新手机苹果发布"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertGreater(similarity, 0.85, "词序不同但内容相同的标题应该返回高相似度")

    def test_different_titles(self):
        """测试完全不同标题"""
        title1 = "苹果发布新iPhone"
        title2 = "特斯拉发布新车型"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertLess(similarity, 0.5, "完全不同标题应该返回低相似度")

    def test_partial_match(self):
        """测试部分匹配"""
        title1 = "苹果公司发布新款iPhone 15 Pro Max"
        title2 = "苹果发布iPhone 15 Pro Max"
        similarity = _calculate_title_similarity(title1, title2)
        self.assertGreater(similarity, 0.7, "部分匹配应该返回中等相似度")

    def test_empty_titles(self):
        """测试空标题"""
        similarity = _calculate_title_similarity("", "")
        self.assertEqual(similarity, 1.0, "两个空标题应该返回1.0")

    def test_one_empty_title(self):
        """测试一个空标题"""
        similarity = _calculate_title_similarity("苹果发布新iPhone", "")
        self.assertEqual(similarity, 0.0, "一个空标题应该返回0.0")


class TestURLNormalization(unittest.TestCase):
    """测试URL标准化"""

    def test_http_url(self):
        """测试HTTP URL"""
        url = "http://example.com/article"
        normalized = _normalize_url(url)
        self.assertEqual(normalized, "example.com/article")

    def test_https_url(self):
        """测试HTTPS URL"""
        url = "https://example.com/article"
        normalized = _normalize_url(url)
        self.assertEqual(normalized, "example.com/article")

    def test_www_prefix(self):
        """测试www前缀"""
        url = "https://www.example.com/article"
        normalized = _normalize_url(url)
        self.assertEqual(normalized, "example.com/article")

    def test_trailing_slash(self):
        """测试末尾斜杠"""
        url = "https://example.com/article/"
        normalized = _normalize_url(url)
        self.assertEqual(normalized, "example.com/article")

    def test_combined(self):
        """测试组合情况"""
        url = "https://www.example.com/article/"
        normalized = _normalize_url(url)
        self.assertEqual(normalized, "example.com/article")

    def test_empty_url(self):
        """测试空URL"""
        normalized = _normalize_url("")
        self.assertEqual(normalized, "")

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        url1 = "HTTPS://EXAMPLE.COM/ARTICLE"
        url2 = "https://example.com/article"
        normalized1 = _normalize_url(url1)
        normalized2 = _normalize_url(url2)
        self.assertEqual(normalized1, normalized2)


class TestCrossPlatformDeduplication(unittest.TestCase):
    """测试跨平台去重"""

    def test_empty_input(self):
        """测试空输入"""
        result = _deduplicate_cross_platform({})
        self.assertEqual(result, {})

    def test_single_news(self):
        """测试单条新闻"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://example.com/1",
                }
            }
        }
        result = _deduplicate_cross_platform(new_titles)
        self.assertEqual(len(result["weibo"]), 1)

    def test_identical_titles_across_platforms(self):
        """测试跨平台完全相同标题"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://weibo.com/1",
                }
            },
            "zhihu": {
                "苹果发布新iPhone": {
                    "ranks": [2],
                    "url": "https://zhihu.com/1",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 应该只保留一个平台的新闻
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 1, "完全相同标题应该只保留一条")

    def test_same_url_across_platforms(self):
        """测试跨平台相同URL"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://example.com/article",
                }
            },
            "zhihu": {
                "苹果公司发布新款iPhone": {
                    "ranks": [2],
                    "url": "https://example.com/article",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 应该只保留一个平台的新闻
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 1, "相同URL应该只保留一条")

    def test_similar_titles_across_platforms(self):
        """测试跨平台相似标题"""
        new_titles = {
            "weibo": {
                "苹果发布新手机": {
                    "ranks": [1],
                    "url": "https://weibo.com/1",
                }
            },
            "zhihu": {
                "新手机苹果发布": {
                    "ranks": [2],
                    "url": "https://zhihu.com/1",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles, similarity_threshold=0.85)
        # 应该只保留一个平台的新闻（因为相似度很高）
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 1, "相似标题应该合并为一条")

    def test_merge_ranks(self):
        """测试合并ranks"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1, 3],
                    "url": "https://example.com/article",
                }
            },
            "zhihu": {
                "苹果发布新iPhone": {
                    "ranks": [2, 4],
                    "url": "https://example.com/article",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 检查ranks是否合并
        for platform_titles in result.values():
            for title_data in platform_titles.values():
                ranks = title_data.get("ranks", [])
                self.assertIn(1, ranks)
                self.assertIn(2, ranks)
                self.assertIn(3, ranks)
                self.assertIn(4, ranks)

    def test_preserve_url(self):
        """测试保留URL"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "",
                }
            },
            "zhihu": {
                "苹果发布新iPhone": {
                    "ranks": [2],
                    "url": "https://example.com/article",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 检查URL是否保留
        for platform_titles in result.values():
            for title_data in platform_titles.values():
                url = title_data.get("url", "")
                self.assertEqual(url, "https://example.com/article", "应该保留非空URL")

    def test_different_news(self):
        """测试不同新闻（不应该去重）"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://weibo.com/1",
                }
            },
            "zhihu": {
                "特斯拉发布新车型": {
                    "ranks": [2],
                    "url": "https://zhihu.com/1",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 应该保留两条新闻
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 2, "不同新闻应该保留两条")

    def test_mobile_url(self):
        """测试移动端URL"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://example.com/article",
                    "mobileUrl": "https://m.example.com/article",
                }
            },
            "zhihu": {
                "苹果公司发布新款iPhone": {
                    "ranks": [2],
                    "url": "https://example.com/article",
                    "mobileUrl": "https://m.example.com/article",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 应该只保留一条（因为URL相同）
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 1, "相同移动端URL应该只保留一条")

    def test_multiple_platforms(self):
        """测试多个平台"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://example.com/article",
                }
            },
            "zhihu": {
                "苹果发布新iPhone": {
                    "ranks": [2],
                    "url": "https://example.com/article",
                }
            },
            "baidu": {
                "苹果发布新iPhone": {
                    "ranks": [3],
                    "url": "https://example.com/article",
                }
            },
        }
        result = _deduplicate_cross_platform(new_titles)
        # 应该只保留一条
        total_titles = sum(len(titles) for titles in result.values())
        self.assertEqual(total_titles, 1, "多个平台的相同新闻应该只保留一条")

    def test_similarity_threshold(self):
        """测试相似度阈值"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://weibo.com/1",
                }
            },
            "zhihu": {
                "苹果发布新iPhone Pro": {
                    "ranks": [2],
                    "url": "https://zhihu.com/1",
                }
            },
        }
        # 使用高阈值（0.95），可能不会合并
        result_high = _deduplicate_cross_platform(new_titles, similarity_threshold=0.95)
        total_high = sum(len(titles) for titles in result_high.values())
        
        # 使用低阈值（0.7），应该会合并
        result_low = _deduplicate_cross_platform(new_titles, similarity_threshold=0.7)
        total_low = sum(len(titles) for titles in result_low.values())
        
        self.assertGreaterEqual(total_high, total_low, "低阈值应该合并更多新闻")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_real_world_scenario(self):
        """测试真实场景：多个平台，混合相同和不同新闻"""
        new_titles = {
            "weibo": {
                "苹果发布新iPhone": {
                    "ranks": [1],
                    "url": "https://example.com/apple-iphone",
                },
                "特斯拉股价上涨": {
                    "ranks": [5],
                    "url": "https://example.com/tesla",
                },
            },
            "zhihu": {
                "苹果公司发布新款iPhone": {  # 相似标题
                    "ranks": [2],
                    "url": "https://example.com/apple-iphone",  # 相同URL
                },
                "特斯拉发布新车型": {  # 不同新闻
                    "ranks": [3],
                    "url": "https://example.com/tesla-car",
                },
            },
            "baidu": {
                "苹果发布新手机": {  # 相似标题（词序不同）
                    "ranks": [4],
                    "url": "https://example.com/apple-phone",
                },
            },
        }
        result = _deduplicate_cross_platform(new_titles, similarity_threshold=0.85)
        
        # 验证结果
        total_titles = sum(len(titles) for titles in result.values())
        # 应该合并：weibo和zhihu的"苹果发布新iPhone"（相同URL）
        # 可能合并：weibo和baidu的"苹果发布新iPhone"和"苹果发布新手机"（相似标题）
        # 保留：weibo的"特斯拉股价上涨"和zhihu的"特斯拉发布新车型"（不同新闻）
        
        # 至少应该有2条不同的新闻（苹果相关和特斯拉相关）
        self.assertGreaterEqual(total_titles, 2, "应该至少保留2条不同新闻")
        # 最多应该有4条（如果相似度阈值不够高，可能不会合并）
        self.assertLessEqual(total_titles, 4, "不应该超过4条新闻")


if __name__ == "__main__":
    unittest.main()
