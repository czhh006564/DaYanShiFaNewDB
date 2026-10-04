#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法 - 周易占卜程序 (优化版)
实现传统的大衍筮法算法，包括蓍草分筮、卦象生成和卦象解释
集成了配置管理、日志记录、性能监控等现代化功能
"""

import random
import time
from typing import List, Tuple, Dict, Optional, Callable, Any
from datetime import datetime

# 导入新的模块
from config import config
from logger import DivinationLogger, get_logger
from performance import monitor_performance, cache_result, time_it
from history import save_divination_history, history_manager
from i18n import i18n_manager, localized_divination, _
from export_tools import export_divination_report
# 数据源：GuaDatabase_V3.0.json（64 卦 386 爻完整详注）
from gua_data_json import (get_gua_info, get_bagua_symbol, get_yao_meaning,
                           get_yao_detail, get_changed_gua,
                           hexagram_values_to_seq, BAGUA_INFO)


class DaYanShiFaV2:
    """大衍筮法类 - 实现完整的筮法过程 (优化版)"""
    
    def __init__(self, use_logging: bool = True, use_caching: bool = True, 
                 save_history: bool = True, language: str = None):
        """
        初始化大衍筮法实例
        
        Args:
            use_logging: 是否启用日志记录
            use_caching: 是否启用缓存
            save_history: 是否保存历史记录
            language: 界面语言
        """
        self.logger = get_logger("dayansifa")
        self.divination_logger = DivinationLogger() if use_logging else None
        self.use_caching = use_caching
        self.save_history = save_history
        
        # 设置语言
        if language:
            i18n_manager.set_language(language)
        
        # 八卦名称对照表
        # 必须使用中文卦名：get_gua_info() 与 get_bagua_symbol() 以中文名为键查询数据库。
        # 若需英文显示，请使用 i18n.LocalizedDivination.get_trigram_name_localized() 转换。
        self.gua_names = {
            (1,1,1): "乾", (0,0,0): "坤", (1,0,0): "震", (0,1,1): "巽",
            (0,1,0): "坎", (1,0,1): "离", (0,0,1): "艮", (1,1,0): "兑"
        }
        
        # 从配置中获取爻象含义
        self.yao_meanings = config.YAO_MEANINGS.copy()
        
        # 统计信息
        self.stats = {
            "total_divinations": 0,
            "total_yaos_generated": 0,
            "start_time": datetime.now()
        }
        
        self.logger.info("大衍筮法实例初始化完成")

    @monitor_performance("divide_yarrow_sticks")
    def divide_yarrow_sticks(self, total: int) -> Tuple[int, int]:
        """
        随机分蓍草为两堆
        
        Args:
            total: 蓍草总数
            
        Returns:
            Tuple[int, int]: (左堆数量, 右堆数量)
            
        Raises:
            ValueError: 当total小于2时
        """
        if total < 2:
            raise ValueError("蓍草总数必须大于等于2")
            
        left = random.randint(1, total - 1)
        right = total - left
        
        self.logger.debug(f"蓍草分堆: 总数{total} -> 左{left} 右{right}")
        return left, right

    @monitor_performance("single_change")
    def single_change(self, sticks: int) -> Tuple[int, int]:
        """
        执行一次变化过程
        
        Args:
            sticks: 当前蓍草数量
            
        Returns:
            Tuple[int, int]: (剩余蓍草数, 取出的蓍草数)
            
        Raises:
            ValueError: 当sticks小于4时
        """
        if sticks < 4:
            raise ValueError("蓍草数量不足以进行变化")
            
        # 分为两堆
        left, right = self.divide_yarrow_sticks(sticks)
        
        # 从右堆取一根放在手指间
        right -= 1
        taken = 1
        
        # 用4除左堆，取余数
        left_remainder = left % 4
        if left_remainder == 0:
            left_remainder = 4
        taken += left_remainder
        left -= left_remainder
        
        # 用4除右堆，取余数
        right_remainder = right % 4
        if right_remainder == 0:
            right_remainder = 4
        taken += right_remainder
        right -= right_remainder
        
        remaining = left + right
        
        self.logger.debug(f"单次变化: {sticks} -> 剩余{remaining}, 取出{taken}")
        return remaining, taken

    @monitor_performance("get_yao_value")
    def get_yao_value(self) -> Tuple[int, List[int]]:
        """
        通过三次变化得到一个爻的值
        
        Returns:
            Tuple[int, List[int]]: (爻值, 每次变化取出的蓍草数列表)
        """
        sticks = config.WORKING_YARROW_STICKS  # 从配置获取初始蓍草数
        taken_list = []
        
        # 进行三次变化
        for i in range(config.CHANGE_CYCLES):
            sticks, taken = self.single_change(sticks)
            taken_list.append(taken)
        
        # 根据最终剩余蓍草数确定爻值
        yao_value = config.YAO_STICK_MAPPING.get(sticks, 7)  # 默认为少阳
        
        if sticks not in config.YAO_STICK_MAPPING:
            self.logger.warning(f"异常的蓍草数量: {sticks}, 默认为少阳")
        
        self.stats["total_yaos_generated"] += 1
        
        if self.divination_logger:
            self.divination_logger.log_yao_generation(
                self.stats["total_yaos_generated"] % 6 or 6, 
                yao_value, 
                taken_list
            )
        
        return yao_value, taken_list

    @monitor_performance("generate_hexagram")
    @time_it
    def generate_hexagram(self, 
                         progress_callback: Optional[Callable[[int, int, str], None]] = None,
                         show_process: Optional[bool] = None) -> Tuple[List[int], List[List[int]]]:
        """
        生成完整的六爻卦象
        
        Args:
            progress_callback: 进度回调函数 (current, total, message)
            show_process: 是否显示过程，默认从配置获取
            
        Returns:
            Tuple[List[int], List[List[int]]]: (六个爻值的列表, 每个爻的变化过程记录)
        """
        if show_process is None:
            show_process = config.SHOW_PROCESS_DETAILS
            
        hexagram = []
        processes = []
        
        if self.divination_logger:
            self.divination_logger.start_session()
        
        if show_process:
            print("开始大衍筮法占卜过程...")
            print("=" * 50)
        
        for i in range(config.HEXAGRAM_LINES):
            if progress_callback:
                progress_callback(i + 1, config.HEXAGRAM_LINES, f"正在生成第{i+1}爻")
            
            if show_process:
                print(f"\n第{i+1}爻：")
            
            yao_value, taken_list = self.get_yao_value()
            hexagram.append(yao_value)
            processes.append(taken_list)
            
            if show_process:
                print(f"三次变化取出蓍草：{taken_list}")
                print(f"得到爻值：{yao_value} ({self.yao_meanings[yao_value]})")
                # 添加延迟增加仪式感
                time.sleep(config.UI_ANIMATION_SPEED * 0.5)
        
        if self.divination_logger:
            self.divination_logger.log_hexagram_complete(hexagram)
        
        self.stats["total_divinations"] += 1
        return hexagram, processes

    @cache_result()
    @monitor_performance("get_trigram_name")
    def get_trigram_name(self, trigram: Tuple[int, int, int]) -> str:
        """
        获取三爻卦名
        
        Args:
            trigram: 三个爻值（转换为阴阳）
            
        Returns:
            str: 卦名
        """
        # 将爻值转换为阴阳（奇数为阳1，偶数为阴0）
        binary_list = [1 if yao % 2 == 1 else 0 for yao in trigram]
        binary_trigram: Tuple[int, int, int] = (binary_list[0], binary_list[1], binary_list[2])
        
        trigram_name = self.gua_names.get(binary_trigram, "未知卦")
        self.logger.debug(f"三爻卦识别: {trigram} -> {binary_trigram} -> {trigram_name}")
        
        return trigram_name

    @cache_result()
    @monitor_performance("analyze_hexagram")
    def analyze_hexagram(self, hexagram: List[int]) -> Dict:
        """
        分析卦象
        
        Args:
            hexagram: 六个爻值的列表（从下到上）
            
        Returns:
            Dict: 分析结果字典
            
        Raises:
            ValueError: 当hexagram长度不为6时
        """
        if len(hexagram) != config.HEXAGRAM_LINES:
            raise ValueError(f"卦象必须包含{config.HEXAGRAM_LINES}个爻")
        
        # 分析上下卦
        lower_list = hexagram[0:3]  # 下三爻
        upper_list = hexagram[3:6]  # 上三爻
        
        lower_trigram: Tuple[int, int, int] = (lower_list[0], lower_list[1], lower_list[2])
        upper_trigram: Tuple[int, int, int] = (upper_list[0], upper_list[1], upper_list[2])
        
        lower_name = self.get_trigram_name(lower_trigram)
        upper_name = self.get_trigram_name(upper_trigram)
        
        # 查找完整卦名和详细信息（数据源：GuaDatabase_V3.0.json）
        gua_info = get_gua_info(upper_name, lower_name)
        full_gua_name = gua_info.get('name', f"{upper_name}上{lower_name}下")
        gua_seq = hexagram_values_to_seq(hexagram)
        
        # 找出变爻
        changing_yaos = []
        for i, yao in enumerate(hexagram):
            if yao in [6, 9]:  # 老阴或老阳为变爻
                changing_yaos.append(i + 1)
        
        analysis_result = {
            "lower_trigram": lower_name,
            "upper_trigram": upper_name,
            "full_name": full_gua_name,
            "changing_yaos": changing_yaos,
            "hexagram_values": hexagram,
            "gua_info": gua_info,
            "seq": gua_seq,
            "gua_symbol": gua_info.get('卦符', ''),
            "analysis_time": datetime.now(),
            "session_id": getattr(self.divination_logger, 'session_id', None)
        }
        
        if self.divination_logger:
            self.divination_logger.log_analysis_result(analysis_result)
        
        return analysis_result

    def display_hexagram(self, hexagram: List[int], detailed: bool = True):
        """
        显示卦象图形
        
        Args:
            hexagram: 六个爻值的列表（从下到上）
            detailed: 是否显示详细信息
        """
        print("\n" + "=" * 60)
        print("📊 卦象图形")
        print("=" * 60)
        
        # 从上到下显示（第6爻到第1爻）
        for i in range(5, -1, -1):
            yao = hexagram[i]
            if yao % 2 == 1:  # 阳爻
                if yao == 9:  # 老阳，变爻
                    line = "━━━━━━━ ○"
                    color = "🔴"  # 红色圆点表示变爻
                else:  # 少阳
                    line = "━━━━━━━  "
                    color = "🟡"  # 黄色表示阳爻
            else:  # 阴爻
                if yao == 6:  # 老阴，变爻
                    line = "━━━  ━━━ ✕"
                    color = "🔴"  # 红色叉表示变爻
                else:  # 少阴
                    line = "━━━  ━━━  "
                    color = "🔵"  # 蓝色表示阴爻
            
            print(f"第{i+1}爻: {line} {color}")
            
            if detailed:
                yao_meaning = get_yao_meaning(i+1, yao, hexagram)
                position_meaning = config.YAO_POSITIONS.get(i+1, f"第{i+1}爻")
                print(f"      {position_meaning}：{yao_meaning}")
            print()

    @time_it
    def divination(self, question: str = "") -> Dict:
        """
        执行完整的占卜过程
        
        Args:
            question: 占卜问题
            
        Returns:
            Dict: 完整的占卜结果
        """
        print("🌟 欢迎使用大衍筮法占卜程序 🌟")
        
        if question:
            print(f"占卜问题：{question}")
        else:
            print("请心中默念您要占卜的问题...")
        
        if not question:
            input("\n按回车键开始占卜...")
        
        start_time = datetime.now()
        
        try:
            # 生成卦象
            hexagram, processes = self.generate_hexagram()
            
            # 显示卦象
            self.display_hexagram(hexagram)
            
            # 分析卦象
            analysis = self.analyze_hexagram(hexagram)
            
            # 显示分析结果
            self._display_analysis(analysis)
            
            # 计算耗时
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "question": question,
                "hexagram": hexagram,
                "processes": processes,
                "analysis": analysis,
                "duration": duration,
                "timestamp": start_time
            }
            
            # 保存历史记录
            if self.save_history:
                try:
                    session_id = save_divination_history(
                        question=question,
                        hexagram=hexagram,
                        analysis=analysis,
                        duration=duration
                    )
                    result["session_id"] = session_id
                    print(f"\n✅ {_('history_saved')}")
                except Exception as e:
                    self.logger.warning(f"保存历史记录失败: {e}")
            
            # 提供导出选项
            if not question:  # 只在交互模式下提供导出选项
                export_choice = input(f"\n是否导出此次占卜报告？(y/n): ").lower().strip()
                if export_choice in ['y', 'yes', '是']:
                    try:
                        report_path = export_divination_report(
                            question=question,
                            hexagram=hexagram,
                            analysis=analysis,
                            processes=processes,
                            duration=duration,
                            format_type="html"
                        )
                        print(f"✅ 报告已导出：{report_path}")
                    except Exception as e:
                        self.logger.error(f"导出报告失败: {e}")
                        print(f"❌ 导出失败：{e}")
            
            if self.divination_logger:
                self.divination_logger.end_session()
            
            self.logger.info(f"占卜完成: {analysis['full_name']}, 耗时: {duration:.3f}秒")
            
            return result
            
        except Exception as e:
            self.logger.error(f"占卜过程出错: {e}", exc_info=True)
            raise

    def _display_analysis(self, analysis: Dict):
        """显示卦象分析结果"""
        print("\n" + "=" * 60)
        print("🔮 卦象分析")
        print("=" * 60)
        
        # 基本信息
        lower_symbol = get_bagua_symbol(analysis['lower_trigram'])
        upper_symbol = get_bagua_symbol(analysis['upper_trigram'])
        
        print(f"📍 卦象结构：")
        print(f"   上卦（外卦）：{analysis['upper_trigram']} {upper_symbol}")
        print(f"   下卦（内卦）：{analysis['lower_trigram']} {lower_symbol}")
        print(f"\n🏷️  完整卦名：{analysis['full_name']}")
        
        # 卦象详细信息
        gua_info = analysis['gua_info']
        if gua_info.get('number'):
            print(f"📊 卦序：第{gua_info['number']}卦")
        if analysis.get('gua_symbol'):
            print(f"🪷 卦符：{analysis['gua_symbol']}")
        
        print(f"\n📜 卦辞：{gua_info.get('gua_ci', '暂无')}")
        print(f"\n🎯 彖传：{gua_info.get('judgment', '暂无')}")
        print(f"\n🖼️  象辞：{gua_info.get('image', '暂无')}")
        
        # 卦象之间的关系（互卦 / 错卦 / 综卦）
        if gua_info.get('互卦'):
            print(f"\n🔗 互卦：{gua_info['互卦']} ｜ 错卦：{gua_info['错卦']} ｜ 综卦：{gua_info['综卦']}")
        
        # 变爻信息（取自 GuaDatabase_V3.0.json 的详细爻辞）
        if analysis['changing_yaos']:
            print(f"\n⚡ 变爻：第{', '.join(map(str, analysis['changing_yaos']))}爻")
            print("💡 变爻提示：变爻代表事态发展的关键转折点，需特别关注。")
            seq = analysis.get('seq', gua_info.get('number', 0))
            for pos in analysis['changing_yaos']:
                detail = get_yao_detail(seq, pos)
                if not detail:
                    continue
                print(f"\n   【第{pos}爻 · {detail['爻位']}】{detail['原文']}")
                print(f"      译文：{detail['译文']}")
                print(f"      解说：{detail['解说1_经义']}")
                print(f"      象传：{detail['象传']}")
                changed = get_changed_gua(seq, pos)
                if changed:
                    print(f"      之卦：{changed}")
        else:
            print("\n🔒 静卦：无变爻，事态相对稳定。")
        
        print("\n" + "=" * 60)
        print("💫 占卜完成！")
        print("📚 注：此程序仅供学习和娱乐使用，具体卦象解释请参考《易经》相关典籍。")
        print("🙏 建议结合个人实际情况，理性对待占卜结果。")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        runtime = (datetime.now() - self.stats["start_time"]).total_seconds()
        return {
            **self.stats,
            "runtime_seconds": runtime,
            "average_time_per_divination": runtime / max(self.stats["total_divinations"], 1)
        }
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取历史记录
        
        Args:
            limit: 限制数量
        
        Returns:
            历史记录列表
        """
        if not self.save_history:
            return []
        
        try:
            return history_manager.get_history(limit=limit)
        except Exception as e:
            self.logger.error(f"获取历史记录失败: {e}")
            return []
    
    def export_history(self, format_type: str = "json") -> Optional[str]:
        """
        导出历史记录
        
        Args:
            format_type: 导出格式
        
        Returns:
            导出文件路径
        """
        if not self.save_history:
            self.logger.warning("未启用历史记录功能")
            return None
        
        try:
            return history_manager.export_history(format_type=format_type)
        except Exception as e:
            self.logger.error(f"导出历史记录失败: {e}")
            return None
    
    def clear_history(self, days_to_keep: Optional[int] = None) -> int:
        """
        清理历史记录
        
        Args:
            days_to_keep: 保留天数，None表示清空所有
        
        Returns:
            删除的记录数
        """
        if not self.save_history:
            self.logger.warning("未启用历史记录功能")
            return 0
        
        try:
            return history_manager.clear_history(days_to_keep=days_to_keep)
        except Exception as e:
            self.logger.error(f"清理历史记录失败: {e}")
            return 0


# 保持向后兼容性
class DaYanShiFa(DaYanShiFaV2):
    """兼容性别名"""
    pass


def main():
    """主程序"""
    try:
        diviner = DaYanShiFaV2()
        
        while True:
            diviner.divination()
            
            again = input("\n是否再次占卜？(y/n): ").lower()
            if again not in ['y', 'yes', '是']:
                break
            print("\n" + "=" * 60 + "\n")
        
        # 显示统计信息
        stats = diviner.get_statistics()
        print(f"\n📊 本次运行统计:")
        print(f"   总占卜次数: {stats['total_divinations']}")
        print(f"   生成爻数: {stats['total_yaos_generated']}")
        print(f"   运行时长: {stats['runtime_seconds']:.1f}秒")
        
        print("\n感谢使用大衍筮法占卜程序！")
        
    except KeyboardInterrupt:
        print("\n\n程序已退出。")
    except Exception as e:
        logger = get_logger("main")
        logger.error(f"程序运行出错: {e}", exc_info=True)
        print(f"程序运行出错: {e}")


if __name__ == "__main__":
    main()