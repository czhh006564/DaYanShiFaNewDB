#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法程序配置管理
统一管理项目的各种配置参数
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """项目配置类"""
    
    # 项目基本信息
    PROJECT_NAME = "大衍筮法"
    PROJECT_VERSION = "2.0.0"
    PROJECT_DESCRIPTION = "数字化周易大衍筮法占卜程序"
    
    # 蓍草相关配置
    TOTAL_YARROW_STICKS = 50
    WORKING_YARROW_STICKS = 49  # 总数减去太极的一根
    CHANGE_CYCLES = 3  # 每个爻需要三次变化
    HEXAGRAM_LINES = 6  # 一个卦有六个爻
    
    # 爻值对应的蓍草数量
    YAO_STICK_MAPPING = {
        36: 9,  # 老阳
        32: 8,  # 少阴
        28: 7,  # 少阳
        24: 6   # 老阴
    }
    
    # 爻的含义
    YAO_MEANINGS = {
        6: "老阴（━━ ━━）变爻",
        7: "少阳（━━━━━━━）",
        8: "少阴（━━ ━━）",
        9: "老阳（━━━━━━━）变爻"
    }
    
    # 爻位含义
    YAO_POSITIONS = {
        1: "初爻（地位）",
        2: "二爻（人位）",
        3: "三爻（天位）",
        4: "四爻（地位）",
        5: "五爻（君位）",
        6: "六爻（天位）"
    }
    
    # Web服务器配置
    WEB_SERVER_HOST = "localhost"
    WEB_SERVER_PORT = 8080
    WEB_AUTO_OPEN_BROWSER = True
    
    # 文件路径配置
    BASE_DIR = Path(__file__).parent
    STATIC_DIR = BASE_DIR / "static"
    TEMPLATES_DIR = BASE_DIR / "templates"
    LOGS_DIR = BASE_DIR / "logs"
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 缓存配置
    ENABLE_CACHE = True
    CACHE_SIZE = 1000  # 缓存最多1000个结果
    CACHE_TTL = 3600   # 缓存1小时
    
    # 用户界面配置
    UI_LANGUAGE = "zh_CN"
    UI_THEME = "traditional"
    UI_ANIMATION_SPEED = 1.0
    
    # 占卜配置
    MAX_QUESTION_LENGTH = 200
    SHOW_PROCESS_DETAILS = True
    ENABLE_SOUND_EFFECTS = False
    
    @classmethod
    def get_env_config(cls, key: str, default: Any = None) -> Any:
        """从环境变量获取配置"""
        env_key = f"DAYANSIFA_{key.upper()}"
        return os.getenv(env_key, default)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取所有配置的字典形式"""
        config_dict = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and not callable(getattr(cls, attr_name)):
                config_dict[attr_name] = getattr(cls, attr_name)
        return config_dict
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置的有效性"""
        try:
            # 验证基本数值
            assert cls.TOTAL_YARROW_STICKS == 50
            assert cls.WORKING_YARROW_STICKS == 49
            assert cls.CHANGE_CYCLES == 3
            assert cls.HEXAGRAM_LINES == 6
            
            # 验证爻值映射
            assert len(cls.YAO_STICK_MAPPING) == 4
            assert all(k in [24, 28, 32, 36] for k in cls.YAO_STICK_MAPPING.keys())
            assert all(v in [6, 7, 8, 9] for v in cls.YAO_STICK_MAPPING.values())
            
            # 验证端口范围
            assert 1024 <= cls.WEB_SERVER_PORT <= 65535
            
            return True
        except AssertionError:
            return False


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False
    SHOW_PROCESS_DETAILS = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_CACHE = True
    SHOW_PROCESS_DETAILS = False


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False
    WEB_AUTO_OPEN_BROWSER = False


# 根据环境变量选择配置
def get_config() -> Config:
    """根据环境变量获取相应的配置类"""
    env = os.getenv('DAYANSIFA_ENV', 'development').lower()
    
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_mapping.get(env, DevelopmentConfig)


# 全局配置实例
config = get_config()

# 验证配置
if not config.validate_config():
    raise ValueError("配置验证失败，请检查配置参数")