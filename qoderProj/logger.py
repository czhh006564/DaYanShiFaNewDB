#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序日志管理模块
提供统一的日志记录功能
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from config import config


class LogManager:
    """日志管理器"""
    
    _instance: Optional['LogManager'] = None
    _initialized = False
    
    def __new__(cls) -> 'LogManager':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志管理器"""
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """设置日志配置"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 创建格式器
        formatter = logging.Formatter(
            config.LOG_FORMAT,
            datefmt=config.LOG_DATE_FORMAT
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器（按日期轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / "dayansifa.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # 错误日志文件处理器
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        return logging.getLogger(name)
    
    def log_divination_start(self, question: str = ""):
        """记录占卜开始"""
        logger = self.get_logger("divination")
        logger.info(f"占卜开始 - 问题: {question[:50]}{'...' if len(question) > 50 else ''}")
    
    def log_divination_result(self, hexagram: list, analysis: dict):
        """记录占卜结果"""
        logger = self.get_logger("divination")
        logger.info(
            f"占卜完成 - 卦象: {hexagram}, "
            f"卦名: {analysis.get('full_name', '未知')}, "
            f"变爻: {analysis.get('changing_yaos', [])}"
        )
    
    def log_performance(self, operation: str, duration: float):
        """记录性能信息"""
        logger = self.get_logger("performance")
        logger.info(f"操作: {operation}, 耗时: {duration:.3f}秒")
    
    def log_error(self, error: Exception, context: str = ""):
        """记录错误信息"""
        logger = self.get_logger("error")
        logger.error(f"错误发生 - 上下文: {context}, 错误: {error}", exc_info=True)
    
    def log_web_request(self, method: str, path: str, status_code: int, duration: float):
        """记录Web请求"""
        logger = self.get_logger("web")
        logger.info(f"{method} {path} - {status_code} - {duration:.3f}秒")


class DivinationLogger:
    """占卜专用日志器"""
    
    def __init__(self):
        self.log_manager = LogManager()
        self.logger = self.log_manager.get_logger("divination")
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def start_session(self, question: str = ""):
        """开始占卜会话"""
        self.logger.info(f"会话开始 [{self.session_id}] - 问题: {question}")
    
    def log_yao_generation(self, yao_number: int, yao_value: int, process: list):
        """记录爻的生成过程"""
        self.logger.debug(
            f"会话 [{self.session_id}] - "
            f"第{yao_number}爻: 值={yao_value}, 过程={process}"
        )
    
    def log_hexagram_complete(self, hexagram: list):
        """记录卦象生成完成"""
        self.logger.info(f"会话 [{self.session_id}] - 卦象生成完成: {hexagram}")
    
    def log_analysis_result(self, analysis: dict):
        """记录分析结果"""
        self.logger.info(
            f"会话 [{self.session_id}] - "
            f"分析完成: {analysis.get('full_name', '未知卦')}, "
            f"变爻: {analysis.get('changing_yaos', [])}"
        )
    
    def end_session(self):
        """结束占卜会话"""
        self.logger.info(f"会话结束 [{self.session_id}]")


class PerformanceLogger:
    """性能监控日志器"""
    
    def __init__(self):
        self.log_manager = LogManager()
        self.logger = self.log_manager.get_logger("performance")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        duration = (datetime.now() - self.start_time).total_seconds()
        if hasattr(self, 'operation_name'):
            self.logger.info(f"操作 {self.operation_name} 完成，耗时: {duration:.3f}秒")
    
    def set_operation(self, name: str):
        """设置操作名称"""
        self.operation_name = name
        return self


# 全局日志管理器实例
log_manager = LogManager()

# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    return log_manager.get_logger(name)

def log_info(message: str, logger_name: str = "main"):
    """记录信息日志的便捷函数"""
    get_logger(logger_name).info(message)

def log_error(message: str, logger_name: str = "main", exc_info: bool = True):
    """记录错误日志的便捷函数"""
    get_logger(logger_name).error(message, exc_info=exc_info)

def log_debug(message: str, logger_name: str = "main"):
    """记录调试日志的便捷函数"""
    get_logger(logger_name).debug(message)