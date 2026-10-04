#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序综合测试脚本
测试所有新功能和优化项
"""

import time
import json
import traceback
from datetime import datetime
from pathlib import Path

# 导入所有模块
try:
    from config import config, DevelopmentConfig, ProductionConfig
    from logger import LogManager, DivinationLogger, PerformanceLogger, get_logger
    from performance import (
        LRUCache, PerformanceMonitor, global_cache, performance_monitor,
        cache_result, monitor_performance, clear_all_caches, get_performance_summary
    )
    from dayansifa_v2 import DaYanShiFaV2
    
    print("✅ 所有模块导入成功")
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    traceback.print_exc()
    exit(1)


class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.logger = get_logger("test")
        self.test_results = []
        self.start_time = datetime.now()
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始综合测试...")
        print("=" * 60)
        
        tests = [
            ("配置模块测试", self.test_config_module),
            ("日志模块测试", self.test_logging_module),
            ("缓存模块测试", self.test_cache_module),
            ("性能监控测试", self.test_performance_module),
            ("核心算法测试", self.test_core_algorithm),
            ("装饰器功能测试", self.test_decorators),
            ("错误处理测试", self.test_error_handling),
            ("统计功能测试", self.test_statistics),
            ("内存优化测试", self.test_memory_optimization),
            ("集成测试", self.test_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔄 {test_name}...")
            try:
                result = test_func()
                self.test_results.append((test_name, "PASS", result))
                print(f"✅ {test_name} - 通过")
            except Exception as e:
                self.test_results.append((test_name, "FAIL", str(e)))
                print(f"❌ {test_name} - 失败: {e}")
                self.logger.error(f"测试失败: {test_name}", exc_info=True)
        
        self._print_summary()
    
    def test_config_module(self):
        """测试配置模块"""
        # 测试基本配置
        assert config.PROJECT_NAME == "大衍筮法"
        assert config.TOTAL_YARROW_STICKS == 50
        assert config.WORKING_YARROW_STICKS == 49
        
        # 测试配置验证
        assert config.validate_config() == True
        
        # 测试不同环境配置
        dev_config = DevelopmentConfig()
        prod_config = ProductionConfig()
        
        assert dev_config.DEBUG == True
        assert prod_config.DEBUG == False
        
        return "配置模块功能正常"
    
    def test_logging_module(self):
        """测试日志模块"""
        # 测试日志管理器
        log_manager = LogManager()
        test_logger = log_manager.get_logger("test")
        
        # 测试日志记录
        test_logger.info("这是一条测试信息")
        test_logger.debug("这是一条调试信息")
        
        # 测试占卜日志器
        divination_logger = DivinationLogger()
        divination_logger.start_session("测试问题")
        divination_logger.log_yao_generation(1, 7, [5, 4, 4])
        divination_logger.end_session()
        
        # 测试性能日志器
        with PerformanceLogger() as perf_logger:
            perf_logger.set_operation("测试操作")
            time.sleep(0.1)
        
        # 检查日志目录是否创建
        log_dir = Path("logs")
        assert log_dir.exists(), "日志目录未创建"
        
        return "日志模块功能正常"
    
    def test_cache_module(self):
        """测试缓存模块"""
        # 测试LRU缓存
        cache = LRUCache(max_size=3, ttl=60)
        
        # 测试基本缓存操作
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # 测试LRU淘汰
        cache.put("key4", "value4")  # 应该淘汰key1
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        
        # 测试缓存统计
        stats = cache.stats()
        assert stats["size"] == 3
        assert stats["max_size"] == 3
        
        # 测试清空缓存
        cache.clear()
        assert cache.stats()["size"] == 0
        
        return "缓存模块功能正常"
    
    def test_performance_module(self):
        """测试性能监控模块"""
        # 测试性能监控器
        monitor = PerformanceMonitor()
        
        # 记录一些性能数据
        monitor.record_execution_time("test_operation", 0.1)
        monitor.record_execution_time("test_operation", 0.2)
        monitor.record_execution_time("test_operation", 0.15)
        
        # 检查平均时间
        avg_time = monitor.get_average_time("test_operation")
        assert avg_time is not None
        assert 0.1 <= avg_time <= 0.2
        
        # 获取性能报告
        report = monitor.get_performance_report()
        assert "test_operation" in report
        assert report["test_operation"]["count"] == 3
        
        return "性能监控模块功能正常"
    
    def test_core_algorithm(self):
        """测试核心算法"""
        diviner = DaYanShiFaV2()
        
        # 测试蓍草分堆
        left, right = diviner.divide_yarrow_sticks(49)
        assert left + right == 49
        assert 1 <= left <= 48
        assert 1 <= right <= 48
        
        # 测试单次变化
        remaining, taken = diviner.single_change(49)
        assert taken in [5, 9]  # 理论上只能是5或9
        assert remaining + taken == 49
        
        # 测试爻值生成
        yao_value, taken_list = diviner.get_yao_value()
        assert yao_value in [6, 7, 8, 9]
        assert len(taken_list) == 3
        
        # 测试三爻卦识别
        trigram_name = diviner.get_trigram_name((7, 7, 7))
        assert trigram_name == "乾"
        
        trigram_name = diviner.get_trigram_name((6, 6, 6))
        assert trigram_name == "坤"
        
        return "核心算法功能正常"
    
    def test_decorators(self):
        """测试装饰器功能"""
        # 测试缓存装饰器
        @cache_result()
        def expensive_function(x, y):
            time.sleep(0.01)  # 模拟耗时操作
            return x + y
        
        # 第一次调用
        start_time = time.time()
        result1 = expensive_function(1, 2)
        first_call_time = time.time() - start_time
        
        # 第二次调用（应该从缓存获取）
        start_time = time.time()
        result2 = expensive_function(1, 2)
        second_call_time = time.time() - start_time
        
        assert result1 == result2 == 3
        # 缓存调用应该更快（如果启用了缓存）
        if config.ENABLE_CACHE:
            assert second_call_time < first_call_time
        
        # 测试性能监控装饰器
        @monitor_performance("test_monitored_function")
        def monitored_function():
            time.sleep(0.01)
            return "done"
        
        result = monitored_function()
        assert result == "done"
        
        # 检查性能记录
        report = performance_monitor.get_performance_report()
        if "test_monitored_function" in report:
            assert report["test_monitored_function"]["count"] >= 1
        
        return "装饰器功能正常"
    
    def test_error_handling(self):
        """测试错误处理"""
        diviner = DaYanShiFaV2()
        
        # 测试无效输入
        try:
            diviner.divide_yarrow_sticks(1)  # 应该抛出异常
            assert False, "应该抛出ValueError"
        except ValueError:
            pass  # 预期的异常
        
        try:
            diviner.single_change(3)  # 应该抛出异常
            assert False, "应该抛出ValueError"
        except ValueError:
            pass  # 预期的异常
        
        try:
            diviner.analyze_hexagram([1, 2, 3])  # 应该抛出异常
            assert False, "应该抛出ValueError"
        except ValueError:
            pass  # 预期的异常
        
        return "错误处理功能正常"
    
    def test_statistics(self):
        """测试统计功能"""
        diviner = DaYanShiFaV2()
        
        # 获取初始统计
        initial_stats = diviner.get_statistics()
        assert initial_stats["total_divinations"] == 0
        assert initial_stats["total_yaos_generated"] == 0
        
        # 生成一些数据
        for _ in range(3):
            yao_value, _ = diviner.get_yao_value()
        
        # 检查统计更新
        updated_stats = diviner.get_statistics()
        assert updated_stats["total_yaos_generated"] == 3
        assert updated_stats["runtime_seconds"] > 0
        
        return "统计功能正常"
    
    def test_memory_optimization(self):
        """测试内存优化"""
        from performance import MemoryOptimizer
        
        # 测试数据结构优化
        test_data = {
            "list": list(range(100)),
            "dict": {"a": 1, "b": 2},
            "string": "test" * 10
        }
        
        optimized_data = MemoryOptimizer.optimize_data_structure(test_data)
        assert optimized_data is not None
        
        # 测试内存使用情况获取
        memory_usage = MemoryOptimizer.get_memory_usage()
        assert memory_usage is not None
        
        return "内存优化功能正常"
    
    def test_integration(self):
        """集成测试"""
        # 测试完整占卜流程
        diviner = DaYanShiFaV2()
        
        # 执行完整占卜
        result = diviner.divination("测试问题")
        
        # 验证结果结构
        assert "question" in result
        assert "hexagram" in result
        assert "analysis" in result
        assert "duration" in result
        assert "timestamp" in result
        
        # 验证卦象
        hexagram = result["hexagram"]
        assert len(hexagram) == 6
        assert all(yao in [6, 7, 8, 9] for yao in hexagram)
        
        # 验证分析结果
        analysis = result["analysis"]
        assert "lower_trigram" in analysis
        assert "upper_trigram" in analysis
        assert "full_name" in analysis
        assert "changing_yaos" in analysis
        
        return "集成测试通过"
    
    def _print_summary(self):
        """打印测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 测试摘要")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        print(f"总耗时: {duration:.2f}秒")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for name, status, result in self.test_results:
                if status == "FAIL":
                    print(f"   - {name}: {result}")
        
        # 性能摘要
        perf_summary = get_performance_summary()
        print(f"\n📈 性能摘要:")
        print(f"缓存统计: {perf_summary.get('cache_stats', {})}")
        
        # 清理
        clear_all_caches()
        
        print("\n🎉 测试完成！")
        return passed_tests == total_tests


def main():
    """主函数"""
    print("🌟 大衍筮法程序综合测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 配置环境: {config.__class__.__name__}")
    print()
    
    # 运行测试
    tester = ComprehensiveTest()
    success = tester.run_all_tests()
    
    # 返回适当的退出码
    exit(0 if success else 1)


if __name__ == "__main__":
    main()