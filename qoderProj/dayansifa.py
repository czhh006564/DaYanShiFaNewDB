#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法 - 周易占卜程序
实现传统的大衍筮法算法，包括蓍草分筮、卦象生成和卦象解释
"""

import random
import time
from typing import List, Tuple, Dict
# 数据源：GuaDatabase_V3.0.json（64 卦 386 爻完整详注）
from gua_data_json import (get_gua_info, get_bagua_symbol, get_yao_meaning,
                           get_yao_detail, get_changed_gua,
                           hexagram_values_to_seq, BAGUA_INFO)


class DaYanShiFa:
    """大衍筮法类 - 实现完整的筮法过程"""
    
    def __init__(self):
        # 卦象名称对照表
        self.gua_names = {
            (1,1,1): "乾", (0,0,0): "坤", (1,0,0): "震", (0,1,1): "巽",
            (0,1,0): "坎", (1,0,1): "离", (0,0,1): "艮", (1,1,0): "兑"
        }
        
        # 爻象含义
        self.yao_meanings = {
            6: "老阴（--✕--）变爻",
            7: "少阳（━━━━━）",
            8: "少阴（━━ ━━）", 
            9: "老阳（--○--）变爻"
        }

    def divide_yarrow_sticks(self, total: int) -> Tuple[int, int]:
        """
        随机分蓍草为两堆
        Args:
            total: 蓍草总数
        Returns:
            左堆和右堆的数量
        """
        left = random.randint(1, total - 1)
        right = total - left
        return left, right

    def single_change(self, sticks: int) -> Tuple[int, int]:
        """
        执行一次变化过程
        Args:
            sticks: 当前蓍草数量
        Returns:
            (剩余蓍草数, 取出的蓍草数)
        """
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
        return remaining, taken

    def get_yao_value(self) -> Tuple[int, List[int]]:
        """
        通过三次变化得到一个爻的值
        Returns:
            (爻值, 每次变化取出的蓍草数列表)
        """
        sticks = 49  # 初始蓍草数（50-1）
        taken_list = []
        
        # 进行三次变化
        for i in range(3):
            sticks, taken = self.single_change(sticks)
            taken_list.append(taken)
        
        # 根据最终剩余蓍草数确定爻值
        if sticks == 36:
            yao_value = 9  # 老阳
        elif sticks == 32:
            yao_value = 8  # 少阴
        elif sticks == 28:
            yao_value = 7  # 少阳
        elif sticks == 24:
            yao_value = 6  # 老阴
        else:
            # 理论上不应该出现其他情况，但为了安全起见
            yao_value = 7
            
        return yao_value, taken_list

    def generate_hexagram(self) -> Tuple[List[int], List[List[int]]]:
        """
        生成完整的六爻卦象
        Returns:
            (六个爻值的列表, 每个爻的变化过程记录)
        """
        hexagram = []
        processes = []
        
        print("开始大衍筮法占卜过程...")
        print("=" * 50)
        
        for i in range(6):
            print(f"\n第{i+1}爻：")
            yao_value, taken_list = self.get_yao_value()
            hexagram.append(yao_value)
            processes.append(taken_list)
            
            print(f"三次变化取出蓍草：{taken_list}")
            print(f"得到爻值：{yao_value} ({self.yao_meanings[yao_value]})")
            
            # 添加一点延迟，增加仪式感
            time.sleep(0.5)
        
        return hexagram, processes

    def get_trigram_name(self, trigram: Tuple[int, int, int]) -> str:
        """
        获取三爻卦名
        Args:
            trigram: 三个爻值（转换为阴阳）
        Returns:
            卦名
        """
        # 将爻值转换为阴阳（奇数为阳1，偶数为阴0）
        binary_list = [1 if yao % 2 == 1 else 0 for yao in trigram]
        binary_trigram: Tuple[int, int, int] = (binary_list[0], binary_list[1], binary_list[2])
        return self.gua_names.get(binary_trigram, "未知卦")

    def analyze_hexagram(self, hexagram: List[int]) -> Dict:
        """
        分析卦象
        Args:
            hexagram: 六个爻值的列表（从下到上）
        Returns:
            分析结果字典
        """
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
        
        return {
            "lower_trigram": lower_name,
            "upper_trigram": upper_name, 
            "full_name": full_gua_name,
            "changing_yaos": changing_yaos,
            "hexagram_values": hexagram,
            "gua_info": gua_info,
            "seq": gua_seq,
            "gua_symbol": gua_info.get('卦符', '')
        }

    def display_hexagram(self, hexagram: List[int]):
        """
        显示卦象图形
        Args:
            hexagram: 六个爻值的列表（从下到上）
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
            print(f"      {get_yao_meaning(i+1, yao, hexagram)}")
            print()

    def divination(self):
        """执行完整的占卜过程"""
        print("🌟 欢迎使用大衍筮法占卜程序 🌟")
        print("请心中默念您要占卜的问题...")
        
        input("\n按回车键开始占卜...")
        
        # 生成卦象
        hexagram, processes = self.generate_hexagram()
        
        # 显示卦象
        self.display_hexagram(hexagram)
        
        # 分析卦象
        analysis = self.analyze_hexagram(hexagram)
        
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


def main():
    """主程序"""
    diviner = DaYanShiFa()
    
    while True:
        diviner.divination()
        
        again = input("\n是否再次占卜？(y/n): ").lower()
        if again not in ['y', 'yes', '是']:
            break
        print("\n" + "=" * 60 + "\n")
    
    print("感谢使用大衍筮法占卜程序！")


if __name__ == "__main__":
    main()