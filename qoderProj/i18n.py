#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法多语言支持模块
提供中文、英文等多种语言的界面和内容
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from config import config
from logger import get_logger


class I18nManager:
    """国际化管理器"""
    
    def __init__(self):
        self.logger = get_logger("i18n")
        self.current_language = config.UI_LANGUAGE
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_translations()
    
    def load_translations(self):
        """加载翻译文件"""
        translations_dir = Path(__file__).parent / "translations"
        
        # 内置翻译数据
        self.translations = {
            "zh_CN": {
                # 基本界面
                "app_title": "大衍筮法 - 数字化周易占卜程序",
                "welcome_message": "🌟 欢迎使用大衍筮法占卜程序 🌟",
                "question_prompt": "请心中默念您要占卜的问题...",
                "start_divination": "开始占卜",
                "press_enter": "按回车键开始占卜...",
                
                # 占卜过程
                "divination_start": "开始大衍筮法占卜过程...",
                "yao_generating": "第{0}爻：",
                "yarrow_changes": "三次变化取出蓍草：{0}",
                "yao_value": "得到爻值：{0} ({1})",
                "hexagram_display": "📊 卦象图形",
                "hexagram_analysis": "🔮 卦象分析",
                
                # 爻值含义
                "old_yin": "老阴（━━ ━━）变爻",
                "young_yang": "少阳（━━━━━━━）",
                "young_yin": "少阴（━━ ━━）",
                "old_yang": "老阳（━━━━━━━）变爻",
                
                # 爻位含义
                "position_1": "初爻（地位）",
                "position_2": "二爻（人位）", 
                "position_3": "三爻（天位）",
                "position_4": "四爻（地位）",
                "position_5": "五爻（君位）",
                "position_6": "六爻（天位）",
                
                # 分析结果
                "hexagram_structure": "📍 卦象结构：",
                "upper_trigram": "上卦（外卦）：{0} {1}",
                "lower_trigram": "下卦（内卦）：{0} {1}",
                "full_hexagram_name": "🏷️ 完整卦名：{0}",
                "hexagram_number": "📊 卦序：第{0}卦",
                "hexagram_text": "📜 卦辞：{0}",
                "judgment": "🎯 断语：{0}",
                "image": "🖼️ 象辞：{0}",
                "changing_yaos": "⚡ 变爻：第{0}爻",
                "static_hexagram": "🔒 静卦：无变爻，事态相对稳定。",
                "changing_hint": "💡 变爻提示：变爻代表事态发展的关键转折点，需特别关注。",
                
                # 完成信息
                "divination_complete": "💫 占卜完成！",
                "disclaimer": "📚 注：此程序仅供学习和娱乐使用，具体卦象解释请参考《易经》相关典籍。",
                "suggestion": "🙏 建议结合个人实际情况，理性对待占卜结果。",
                
                # 功能按钮
                "continue_divination": "是否再次占卜？(y/n): ",
                "thank_you": "感谢使用大衍筮法占卜程序！",
                
                # 历史记录
                "history_title": "📚 占卜历史",
                "export_history": "导出历史",
                "clear_history": "清空历史",
                "search_history": "搜索历史",
                "no_history": "暂无历史记录",
                "history_saved": "✅ 占卜记录已保存",
                "history_exported": "✅ 历史记录导出成功",
                
                # 统计信息
                "statistics": "📊 统计信息",
                "total_divinations": "总占卜次数：{0}",
                "average_duration": "平均耗时：{0}秒",
                "popular_hexagrams": "常见卦象：",
                "recent_activity": "最近活动：",
                
                # 错误信息
                "error_occurred": "❌ 发生错误：{0}",
                "file_not_found": "文件未找到：{0}",
                "invalid_input": "无效输入：{0}",
                "network_error": "网络错误：{0}",
                
                # Web界面
                "start_button": "开始大衍筮法",
                "question_placeholder": "请输入您的问题（可选）",
                "progress_text": "正在进行占卜...",
                "result_title": "占卜结果",
                "details_button": "查看详情",
                "new_divination": "重新占卜",
                
                # API相关
                "api_success": "操作成功",
                "api_error": "操作失败",
                "invalid_request": "无效请求",
                "server_error": "服务器错误"
            },
            
            "en_US": {
                # Basic interface
                "app_title": "Da Yan Shi Fa - Digital I Ching Divination",
                "welcome_message": "🌟 Welcome to Da Yan Shi Fa Divination Program 🌟",
                "question_prompt": "Please meditate on your question...",
                "start_divination": "Start Divination",
                "press_enter": "Press Enter to start divination...",
                
                # Divination process
                "divination_start": "Starting Da Yan Shi Fa divination process...",
                "yao_generating": "Line {0}:",
                "yarrow_changes": "Three changes extracted yarrow: {0}",
                "yao_value": "Line value: {0} ({1})",
                "hexagram_display": "📊 Hexagram Display",
                "hexagram_analysis": "🔮 Hexagram Analysis",
                
                # Line meanings
                "old_yin": "Old Yin (--×--) Changing",
                "young_yang": "Young Yang (━━━━━━━)",
                "young_yin": "Young Yin (━━ ━━)",
                "old_yang": "Old Yang (--○--) Changing",
                
                # Position meanings
                "position_1": "1st Line (Earth)",
                "position_2": "2nd Line (Human)",
                "position_3": "3rd Line (Heaven)",
                "position_4": "4th Line (Earth)",
                "position_5": "5th Line (Ruler)",
                "position_6": "6th Line (Heaven)",
                
                # Analysis results
                "hexagram_structure": "📍 Hexagram Structure:",
                "upper_trigram": "Upper Trigram: {0} {1}",
                "lower_trigram": "Lower Trigram: {0} {1}",
                "full_hexagram_name": "🏷️ Hexagram Name: {0}",
                "hexagram_number": "📊 Hexagram No.: {0}",
                "hexagram_text": "📜 Hexagram Text: {0}",
                "judgment": "🎯 Judgment: {0}",
                "image": "🖼️ Image: {0}",
                "changing_yaos": "⚡ Changing Lines: {0}",
                "static_hexagram": "🔒 Static hexagram: No changing lines, situation is stable.",
                "changing_hint": "💡 Changing lines represent key turning points in development.",
                
                # Completion info
                "divination_complete": "💫 Divination Complete!",
                "disclaimer": "📚 Note: This program is for learning and entertainment only.",
                "suggestion": "🙏 Please consider personal circumstances and use results wisely.",
                
                # Function buttons
                "continue_divination": "Divinate again? (y/n): ",
                "thank_you": "Thank you for using Da Yan Shi Fa!",
                
                # History
                "history_title": "📚 Divination History",
                "export_history": "Export History",
                "clear_history": "Clear History", 
                "search_history": "Search History",
                "no_history": "No history records",
                "history_saved": "✅ Divination record saved",
                "history_exported": "✅ History exported successfully",
                
                # Statistics
                "statistics": "📊 Statistics",
                "total_divinations": "Total Divinations: {0}",
                "average_duration": "Average Duration: {0}s",
                "popular_hexagrams": "Popular Hexagrams:",
                "recent_activity": "Recent Activity:",
                
                # Errors
                "error_occurred": "❌ Error: {0}",
                "file_not_found": "File not found: {0}",
                "invalid_input": "Invalid input: {0}",
                "network_error": "Network error: {0}",
                
                # Web interface
                "start_button": "Start Da Yan Shi Fa",
                "question_placeholder": "Enter your question (optional)",
                "progress_text": "Divination in progress...",
                "result_title": "Divination Result",
                "details_button": "View Details",
                "new_divination": "New Divination",
                
                # API related
                "api_success": "Success",
                "api_error": "Failed",
                "invalid_request": "Invalid request",
                "server_error": "Server error"
            }
        }
        
        # 尝试从文件加载额外翻译
        try:
            if translations_dir.exists():
                for lang_file in translations_dir.glob("*.json"):
                    lang_code = lang_file.stem
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        file_translations = json.load(f)
                        if lang_code in self.translations:
                            self.translations[lang_code].update(file_translations)
                        else:
                            self.translations[lang_code] = file_translations
                        self.logger.debug(f"加载翻译文件: {lang_file}")
        except Exception as e:
            self.logger.warning(f"加载翻译文件失败: {e}")
    
    def set_language(self, language_code: str):
        """设置当前语言"""
        if language_code in self.translations:
            self.current_language = language_code
            self.logger.info(f"语言设置为: {language_code}")
        else:
            self.logger.warning(f"不支持的语言: {language_code}")
    
    def get_text(self, key: str, *args, language: Optional[str] = None) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            *args: 格式化参数
            language: 指定语言，默认使用当前语言
        
        Returns:
            翻译后的文本
        """
        lang = language or self.current_language
        
        # 获取翻译文本
        if lang in self.translations and key in self.translations[lang]:
            text = self.translations[lang][key]
        elif "zh_CN" in self.translations and key in self.translations["zh_CN"]:
            # 回退到中文
            text = self.translations["zh_CN"][key]
            self.logger.debug(f"翻译键 '{key}' 在语言 '{lang}' 中未找到，使用中文")
        else:
            # 最后回退到键本身
            text = key
            self.logger.warning(f"翻译键 '{key}' 未找到")
        
        # 格式化参数
        if args:
            try:
                text = text.format(*args)
            except Exception as e:
                self.logger.error(f"格式化翻译文本失败: {e}")
        
        return text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return {
            "zh_CN": "简体中文",
            "en_US": "English"
        }
    
    def export_translations(self, language: str, output_path: str):
        """导出翻译文件"""
        if language not in self.translations:
            raise ValueError(f"语言 '{language}' 不存在")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.translations[language], f, 
                     ensure_ascii=False, indent=2)
        
        self.logger.info(f"翻译文件导出完成: {output_path}")


class LocalizedDivination:
    """本地化的占卜类"""
    
    def __init__(self, i18n_manager: I18nManager):
        self.i18n = i18n_manager
        self.logger = get_logger("localized_divination")
    
    def get_yao_meaning(self, yao_value: int) -> str:
        """获取爻含义的本地化文本"""
        meanings = {
            6: "old_yin",
            7: "young_yang", 
            8: "young_yin",
            9: "old_yang"
        }
        key = meanings.get(yao_value, "young_yang")
        return self.i18n.get_text(key)
    
    def get_position_meaning(self, position: int) -> str:
        """获取爻位含义的本地化文本"""
        key = f"position_{position}"
        return self.i18n.get_text(key)
    
    def get_trigram_name_localized(self, trigram_name: str, language: Optional[str] = None) -> str:
        """获取三爻卦名的本地化版本"""
        # 三爻卦名的英文对照
        trigram_translations = {
            "zh_CN": {
                "乾": "乾", "坤": "坤", "震": "震", "巽": "巽",
                "坎": "坎", "离": "离", "艮": "艮", "兑": "兑"
            },
            "en_US": {
                "乾": "Qian (Heaven)", "坤": "Kun (Earth)", 
                "震": "Zhen (Thunder)", "巽": "Xun (Wind)",
                "坎": "Kan (Water)", "离": "Li (Fire)", 
                "艮": "Gen (Mountain)", "兑": "Dui (Lake)"
            }
        }
        
        lang = language or self.i18n.current_language
        if lang in trigram_translations and trigram_name in trigram_translations[lang]:
            return trigram_translations[lang][trigram_name]
        return trigram_name
    
    def format_hexagram_analysis(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """格式化卦象分析的本地化文本"""
        formatted = {}
        
        # 基本结构信息
        formatted["structure"] = self.i18n.get_text("hexagram_structure")
        formatted["upper_trigram"] = self.i18n.get_text(
            "upper_trigram", 
            self.get_trigram_name_localized(analysis.get("upper_trigram", "")),
            analysis.get("upper_symbol", "")
        )
        formatted["lower_trigram"] = self.i18n.get_text(
            "lower_trigram",
            self.get_trigram_name_localized(analysis.get("lower_trigram", "")),
            analysis.get("lower_symbol", "")
        )
        
        # 卦名和信息
        formatted["full_name"] = self.i18n.get_text(
            "full_hexagram_name", 
            analysis.get("full_name", "")
        )
        
        gua_info = analysis.get("gua_info", {})
        if gua_info.get("number"):
            formatted["number"] = self.i18n.get_text(
                "hexagram_number", 
                gua_info["number"]
            )
        
        formatted["gua_ci"] = self.i18n.get_text(
            "hexagram_text", 
            gua_info.get("gua_ci", "暂无")
        )
        formatted["judgment"] = self.i18n.get_text(
            "judgment", 
            gua_info.get("judgment", "暂无")
        )
        formatted["image"] = self.i18n.get_text(
            "image", 
            gua_info.get("image", "暂无")
        )
        
        # 变爻信息
        changing_yaos = analysis.get("changing_yaos", [])
        if changing_yaos:
            formatted["changing_yaos"] = self.i18n.get_text(
                "changing_yaos", 
                "、".join(map(str, changing_yaos))
            )
            formatted["changing_hint"] = self.i18n.get_text("changing_hint")
        else:
            formatted["static_hexagram"] = self.i18n.get_text("static_hexagram")
        
        return formatted


# 全局国际化管理器
i18n_manager = I18nManager()
localized_divination = LocalizedDivination(i18n_manager)

# 便捷函数
def _(key: str, *args, **kwargs) -> str:
    """获取翻译文本的便捷函数"""
    return i18n_manager.get_text(key, *args, **kwargs)

def set_language(language_code: str):
    """设置语言的便捷函数"""
    i18n_manager.set_language(language_code)

def get_supported_languages() -> Dict[str, str]:
    """获取支持语言的便捷函数"""
    return i18n_manager.get_supported_languages()