#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单验证脚本 - 测试大衍筮法程序是否正常工作
"""

try:
    from dayansifa import DaYanShiFa
    # 数据源：GuaDatabase_V3.0.json
    from gua_data_json import get_gua_info, get_bagua_symbol
    
    print("🧪 开始验证大衍筮法程序...")
    print("=" * 50)
    
    # 创建占卜实例
    diviner = DaYanShiFa()
    print("✅ 成功创建DaYanShiFa实例")
    
    # 测试蓍草分堆
    left, right = diviner.divide_yarrow_sticks(49)
    print(f"✅ 蓍草分堆测试：左{left}根，右{right}根，总计{left+right}根")
    
    # 测试单次变化
    remaining, taken = diviner.single_change(49)
    print(f"✅ 单次变化测试：剩余{remaining}根，取出{taken}根")
    
    # 测试获取爻值
    yao_value, processes = diviner.get_yao_value()
    print(f"✅ 爻值生成测试：得到爻值{yao_value}，变化过程{processes}")
    
    # 测试卦象数据库
    info = get_gua_info("乾", "乾")
    print(f"✅ 卦象数据库测试：{info['name']} - {info['gua_ci'][:10]}...")
    
    # 测试八卦符号
    symbol = get_bagua_symbol("乾")
    print(f"✅ 八卦符号测试：乾 {symbol}")
    
    # 测试三爻卦名
    trigram_name = diviner.get_trigram_name((9, 7, 9))
    print(f"✅ 三爻卦名测试：(9,7,9) -> {trigram_name}")
    
    print("\n🎉 所有基础功能测试通过！")
    print("✨ 大衍筮法程序运行正常，可以开始使用。")
    
    # 演示一次简化的占卜过程
    print("\n" + "=" * 50)
    print("🔮 演示一次完整占卜过程...")
    
    # 生成一个完整卦象（不显示详细过程）
    import random
    random.seed(42)  # 使用固定种子以获得可预测的结果用于演示
    
    hexagram = []
    for i in range(6):
        yao_value, _ = diviner.get_yao_value()
        hexagram.append(yao_value)
    
    print(f"生成的卦象：{hexagram}")
    
    # 分析卦象
    analysis = diviner.analyze_hexagram(hexagram)
    print(f"下卦：{analysis['lower_trigram']}")
    print(f"上卦：{analysis['upper_trigram']}")
    print(f"卦名：{analysis['full_name']}")
    
    if analysis['changing_yaos']:
        print(f"变爻：第{', '.join(map(str, analysis['changing_yaos']))}爻")
    else:
        print("无变爻")
    
    print("\n✅ 演示完成！程序运行完全正常。")
    
except ImportError as e:
    print(f"❌ 导入错误：{e}")
    print("请确保所有文件都在同一目录下。")
except Exception as e:
    print(f"❌ 程序错误：{e}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 50)
print("验证完成！如果看到上面都是 ✅ 标记，说明程序工作正常。")
print("现在可以运行 'python dayansifa.py' 开始正式占卜。")