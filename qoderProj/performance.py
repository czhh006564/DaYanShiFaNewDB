#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序性能监控和缓存模块
提供性能监控、缓存管理等功能
"""

import time
import functools
import hashlib
import pickle
from typing import Any, Dict, Optional, Callable, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta
from config import config
from logger import get_logger, PerformanceLogger


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化LRU缓存
        
        Args:
            max_size: 缓存最大大小
            ttl: 生存时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}
        self.logger = get_logger("cache")
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存项是否过期"""
        if key not in self.timestamps:
            return True
        return datetime.now() - self.timestamps[key] > timedelta(seconds=self.ttl)
    
    def _cleanup_expired(self):
        """清理过期的缓存项"""
        expired_keys = [
            key for key in self.cache.keys() 
            if self._is_expired(key)
        ]
        for key in expired_keys:
            self._remove(key)
    
    def _remove(self, key: str):
        """移除缓存项"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not config.ENABLE_CACHE:
            return None
        
        if key not in self.cache:
            return None
        
        if self._is_expired(key):
            self._remove(key)
            return None
        
        # 移动到末尾（最近使用）
        value = self.cache.pop(key)
        self.cache[key] = value
        
        self.logger.debug(f"缓存命中: {key}")
        return value
    
    def put(self, key: str, value: Any):
        """设置缓存值"""
        if not config.ENABLE_CACHE:
            return
        
        # 清理过期项
        self._cleanup_expired()
        
        # 如果已存在，更新位置
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # 移除最久未使用的项
            oldest_key = next(iter(self.cache))
            self._remove(oldest_key)
        
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
        
        self.logger.debug(f"缓存设置: {key}")
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
        self.logger.info("缓存已清空")
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        self._cleanup_expired()
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "usage_ratio": len(self.cache) / self.max_size
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = get_logger("performance")
        self.metrics: Dict[str, list] = {}
    
    def record_execution_time(self, operation: str, execution_time: float):
        """记录执行时间"""
        if operation not in self.metrics:
            self.metrics[operation] = []
        
        self.metrics[operation].append({
            "timestamp": datetime.now(),
            "execution_time": execution_time
        })
        
        # 只保留最近100条记录
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
        
        self.logger.debug(f"性能记录: {operation} - {execution_time:.3f}秒")
    
    def get_average_time(self, operation: str) -> Optional[float]:
        """获取操作的平均执行时间"""
        if operation not in self.metrics or not self.metrics[operation]:
            return None
        
        times = [metric["execution_time"] for metric in self.metrics[operation]]
        return sum(times) / len(times)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {}
        for operation, metrics in self.metrics.items():
            if not metrics:
                continue
            
            times = [metric["execution_time"] for metric in metrics]
            report[operation] = {
                "count": len(times),
                "average": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "recent": times[-10:] if len(times) >= 10 else times
            }
        
        return report


# 全局实例
global_cache = LRUCache(config.CACHE_SIZE, config.CACHE_TTL)
performance_monitor = PerformanceMonitor()


def cache_result(cache_key_func: Optional[Callable] = None, ttl: Optional[int] = None):
    """
    缓存函数结果的装饰器
    
    Args:
        cache_key_func: 生成缓存键的函数
        ttl: 缓存生存时间
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not config.ENABLE_CACHE:
                return func(*args, **kwargs)
            
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = global_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            global_cache.put(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def monitor_performance(operation_name: Optional[str] = None):
    """
    监控函数性能的装饰器
    
    Args:
        operation_name: 操作名称，默认使用函数名
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                performance_monitor.record_execution_time(op_name, execution_time)
        
        return wrapper
    return decorator


def time_it(func: Callable) -> Callable:
    """简单的执行时间测量装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with PerformanceLogger() as perf_logger:
            perf_logger.set_operation(func.__name__)
            return func(*args, **kwargs)
    return wrapper


class BatchProcessor:
    """批处理器，用于优化大量数据处理"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.logger = get_logger("batch_processor")
    
    def process_items(self, items: list, processor: Callable, progress_callback: Optional[Callable] = None) -> list:
        """
        批量处理项目
        
        Args:
            items: 要处理的项目列表
            processor: 处理函数
            progress_callback: 进度回调函数
        
        Returns:
            处理结果列表
        """
        results = []
        total_items = len(items)
        
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            
            batch_start = time.time()
            batch_results = [processor(item) for item in batch]
            batch_time = time.time() - batch_start
            
            results.extend(batch_results)
            
            if progress_callback:
                progress = min(i + self.batch_size, total_items) / total_items
                progress_callback(progress, f"已处理 {min(i + self.batch_size, total_items)}/{total_items} 项")
            
            self.logger.debug(f"批处理完成: {len(batch)} 项，耗时 {batch_time:.3f}秒")
        
        return results


class MemoryOptimizer:
    """内存优化器"""
    
    @staticmethod
    def optimize_data_structure(data: Any) -> Any:
        """优化数据结构以减少内存使用"""
        if isinstance(data, dict):
            # 使用__slots__优化字典
            return {k: MemoryOptimizer.optimize_data_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            # 对于大列表，考虑使用生成器
            if len(data) > 1000:
                return (MemoryOptimizer.optimize_data_structure(item) for item in data)
            return [MemoryOptimizer.optimize_data_structure(item) for item in data]
        elif isinstance(data, str):
            # 对于重复字符串，使用字符串池
            # 对于重复字符串，使用字符串池（Python 3.8+中intern已移除）
            return data
        else:
            return data
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """获取内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}


# 便捷函数
def clear_all_caches():
    """清空所有缓存"""
    global_cache.clear()
    get_logger("cache").info("所有缓存已清空")

def get_performance_summary() -> Dict[str, Any]:
    """获取性能摘要"""
    return {
        "cache_stats": global_cache.stats(),
        "performance_report": performance_monitor.get_performance_report(),
        "memory_usage": MemoryOptimizer.get_memory_usage()
    }