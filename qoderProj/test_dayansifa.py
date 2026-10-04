#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序测试文件
用于验证各个功能模块的正确性
"""

import unittest
from dayansifa import DaYanShiFa
# 数据源：GuaDatabase_V3.0.json（断言值取自该 JSON 原文，保留繁体字形）
from gua_data_json import get_gua_info, get_bagua_symbol, get_yao_meaning


class TestDaYanShiFa(unittest.TestCase):
    """测试大衍筮法类"""
    
    def setUp(self):
        """测试前准备"""
        self.diviner = DaYanShiFa()
    
    def test_divide_yarrow_sticks(self):
        """测试蓍草分堆功能"""
        total = 49
        left, right = self.diviner.divide_yarrow_sticks(total)
        
        # 检查分堆结果
        self.assertEqual(left + right, total)
        self.assertTrue(1 <= left <= total - 1)
        self.assertTrue(1 <= right <= total - 1)
    
    def test_single_change(self):
        """测试单次变化过程"""
        sticks = 49
        remaining, taken = self.diviner.single_change(sticks)
        
        # 检查取出的蓍草数应该是5或9
        self.assertIn(taken, [5, 9])
        # 检查剩余蓍草数
        self.assertEqual(remaining + taken, sticks)
        self.assertTrue(remaining > 0)
    
    def test_get_yao_value(self):
        """测试获取爻值"""
        yao_value, taken_list = self.diviner.get_yao_value()
        
        # 检查爻值应该在6-9之间
        self.assertIn(yao_value, [6, 7, 8, 9])
        # 检查三次变化
        self.assertEqual(len(taken_list), 3)
        # 检查每次取出的蓍草数
        for taken in taken_list:
            self.assertTrue(taken > 0)
    
    def test_get_trigram_name(self):
        """测试三爻卦名获取"""
        # 测试乾卦
        trigram = (9, 7, 9)  # 全阳
        name = self.diviner.get_trigram_name(trigram)
        self.assertEqual(name, "乾")
        
        # 测试坤卦
        trigram = (6, 8, 6)  # 全阴
        name = self.diviner.get_trigram_name(trigram)
        self.assertEqual(name, "坤")
    
    def test_analyze_hexagram(self):
        """测试卦象分析"""
        # 测试乾卦（全阳）
        hexagram = [9, 7, 9, 9, 7, 9]
        analysis = self.diviner.analyze_hexagram(hexagram)
        
        self.assertEqual(analysis['lower_trigram'], "乾")
        self.assertEqual(analysis['upper_trigram'], "乾")
        self.assertIn("乾", analysis['full_name'])
        
        # 检查变爻
        expected_changing_yaos = [1, 3, 4, 6]  # 老阳的位置
        self.assertEqual(analysis['changing_yaos'], expected_changing_yaos)


class TestGuaDatabase(unittest.TestCase):
    """测试卦象数据库"""
    
    def test_get_gua_info(self):
        """测试获取卦象信息"""
        info = get_gua_info("乾", "乾")
        
        self.assertEqual(info['name'], "乾為天")
        self.assertEqual(info['number'], 1)
        self.assertIn("元亨", info['gua_ci'])
    
    def test_get_bagua_symbol(self):
        """测试获取八卦符号"""
        symbol = get_bagua_symbol("乾")
        self.assertEqual(symbol, "☰")
        
        symbol = get_bagua_symbol("坤")
        self.assertEqual(symbol, "☷")
        
        # 测试未知卦象
        symbol = get_bagua_symbol("未知")
        self.assertEqual(symbol, "?")
    
    def test_get_yao_meaning(self):
        """测试获取爻含义"""
        meaning = get_yao_meaning(1, 9)
        self.assertIn("初爻", meaning)
        self.assertIn("老阳", meaning)
        
        meaning = get_yao_meaning(5, 7)
        self.assertIn("君位", meaning)
        self.assertIn("少阳", meaning)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_divination_process(self):
        """测试完整占卜流程"""
        diviner = DaYanShiFa()
        
        # 生成卦象
        hexagram, processes = diviner.generate_hexagram()
        
        # 验证卦象结构
        self.assertEqual(len(hexagram), 6)
        self.assertEqual(len(processes), 6)
        
        # 验证每个爻值
        for yao in hexagram:
            self.assertIn(yao, [6, 7, 8, 9])
        
        # 验证每个过程记录
        for process in processes:
            self.assertEqual(len(process), 3)  # 三次变化
        
        # 分析卦象
        analysis = diviner.analyze_hexagram(hexagram)
        
        # 验证分析结果结构
        required_keys = ['lower_trigram', 'upper_trigram', 'full_name', 
                        'changing_yaos', 'hexagram_values', 'gua_info']
        for key in required_keys:
            self.assertIn(key, analysis)


class TestTrigramOrderRegression(unittest.TestCase):
    """上下卦顺序回归测试

    历史 Bug：卦象数据库的键为 (上卦, 下卦)，但查询时按 (下卦, 上卦) 组键，
    导致返回上下颠倒的综卦（如算出「天风姤」却显示「风天小畜」）。
    由于 64 个组合全部收录，该错误不会报错，只会静默返回错误卦象。
    本组用例全部使用上下不对称的卦，确保此类错误能被发现。
    """

    # (上卦, 下卦, 卦名, 卦序)
    ASYMMETRIC_CASES = [
        ("乾", "巽", "天風姤", 44),
        ("巽", "乾", "風天小畜", 9),
        ("坎", "离", "水火既濟", 63),
        ("离", "坎", "火水未濟", 64),
        ("乾", "坤", "天地否", 12),
        ("坤", "乾", "地天泰", 11),
        ("艮", "坤", "山地剝", 23),
        ("坤", "艮", "地山謙", 15),
        ("兑", "艮", "澤山咸", 31),
        ("艮", "兑", "山澤損", 41),
        ("震", "巽", "雷風恆", 32),
        ("巽", "震", "風雷益", 42),
    ]

    def test_get_gua_info_upper_before_lower(self):
        """数据库查询必须区分上下卦，不能返回颠倒的综卦"""
        for upper, lower, name, number in self.ASYMMETRIC_CASES:
            with self.subTest(upper=upper, lower=lower):
                info = get_gua_info(upper, lower)
                self.assertEqual(info["name"], name)
                self.assertEqual(info["number"], number)

    def test_reversed_trigrams_yield_different_hexagram(self):
        """上下卦互换必须得到不同的卦，否则说明查询未区分上下"""
        pairs = [("乾", "巽"), ("坎", "离"), ("艮", "坤"), ("兑", "艮"), ("震", "巽")]
        for upper, lower in pairs:
            with self.subTest(upper=upper, lower=lower):
                normal = get_gua_info(upper, lower)["name"]
                reversed_ = get_gua_info(lower, upper)["name"]
                self.assertNotEqual(normal, reversed_)

    def test_analyze_hexagram_asymmetric(self):
        """端到端：上艮下坤应为山地剥(23)，而非地山谦(15)"""
        diviner = DaYanShiFa()
        # 爻值自下而上：下卦坤(8,8,8)，上卦艮(8,8,9)
        analysis = diviner.analyze_hexagram([8, 8, 8, 8, 8, 9])

        self.assertEqual(analysis["lower_trigram"], "坤")
        self.assertEqual(analysis["upper_trigram"], "艮")
        self.assertEqual(analysis["full_name"], "山地剝")
        self.assertEqual(analysis["gua_info"]["number"], 23)

    def test_analyze_hexagram_reversed_asymmetric(self):
        """端到端：上坤下艮应为地山谦(15)"""
        diviner = DaYanShiFa()
        # 爻值自下而上：下卦艮(8,8,9)，上卦坤(8,8,8)
        analysis = diviner.analyze_hexagram([8, 8, 9, 8, 8, 8])

        self.assertEqual(analysis["lower_trigram"], "艮")
        self.assertEqual(analysis["upper_trigram"], "坤")
        self.assertEqual(analysis["full_name"], "地山謙")
        self.assertEqual(analysis["gua_info"]["number"], 15)

    def test_analyze_hexagram_tianfeng_gou(self):
        """端到端：上乾下巽应为天风姤(44)"""
        diviner = DaYanShiFa()
        # 下卦巽(8,7,7)，上卦乾(7,7,7)
        analysis = diviner.analyze_hexagram([8, 7, 7, 7, 7, 7])

        self.assertEqual(analysis["lower_trigram"], "巽")
        self.assertEqual(analysis["upper_trigram"], "乾")
        self.assertEqual(analysis["full_name"], "天風姤")
        self.assertEqual(analysis["gua_info"]["number"], 44)


class TestV2TrigramNames(unittest.TestCase):
    """v2 版本卦名回归测试

    历史 Bug：DaYanShiFaV2.gua_names 使用拼音（kun/gen），
    而 get_gua_info()/get_bagua_symbol() 以中文卦名为键，
    导致卦名退化为「genkun」、卦序为 0、卦辞丢失。
    """

    def setUp(self):
        try:
            from dayansifa_v2 import DaYanShiFaV2
        except ImportError as exc:  # pragma: no cover
            self.skipTest(f"无法导入 dayansifa_v2: {exc}")
        self.diviner = DaYanShiFaV2(use_logging=False, save_history=False)

    def test_trigram_names_are_chinese(self):
        """卦名必须是中文，才能命中卦象数据库"""
        chinese = {"乾", "坤", "震", "巽", "坎", "离", "艮", "兑"}
        self.assertEqual(set(self.diviner.gua_names.values()), chinese)

    def test_analyze_hexagram_returns_real_hexagram(self):
        """v2 分析结果必须是真实卦名，而非拼音拼接"""
        analysis = self.diviner.analyze_hexagram([8, 8, 8, 8, 8, 9])

        self.assertEqual(analysis["lower_trigram"], "坤")
        self.assertEqual(analysis["upper_trigram"], "艮")
        self.assertEqual(analysis["full_name"], "山地剝")
        self.assertEqual(analysis["gua_info"]["number"], 23)
        self.assertTrue(analysis["gua_info"].get("gua_ci"))


def run_manual_test():
    """手动测试：运行一次完整的占卜过程"""
    print("🧪 开始手动测试...")
    print("=" * 50)
    
    diviner = DaYanShiFa()
    
    # 测试单次变化
    print("测试单次变化过程：")
    remaining, taken = diviner.single_change(49)
    print(f"剩余蓍草：{remaining}，取出：{taken}")
    
    print("\n测试获取爻值：")
    yao_value, taken_list = diviner.get_yao_value()
    print(f"爻值：{yao_value}，变化过程：{taken_list}")
    
    print("\n测试卦象数据库：")
    info = get_gua_info("乾", "乾")
    print(f"乾卦信息：{info['name']} - {info['gua_ci']}")
    
    print("\n🎯 手动测试完成！")


if __name__ == "__main__":
    print("🔍 大衍筮法程序测试")
    print("=" * 60)
    
    # 运行单元测试
    print("1. 运行单元测试...")
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    
    # 运行手动测试
    print("2. 运行手动测试...")
    run_manual_test()