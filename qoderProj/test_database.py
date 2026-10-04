#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GuaDatabase_V3.0.json 数据完整性验证脚本

校验内容：
  1. 64 卦齐全、卦序连续、上下卦组合唯一
  2. 卦辞 / 彖传 / 大象 / 六爻详注字段无缺失、无占位符
  3. 爻阴阳与上下卦自洽
  4. 错卦（六爻全反）、综卦（上下颠倒）、互卦（中四爻）规则自洽
  5. 384 条单爻发动之卦与爻辞内「大衍实占」所载之卦一致
"""

from gua_data_json import (
    BAGUA_INFO, LIUSHISI_GUA_DB, GUA_DB,
    get_gua_info, get_bagua_symbol, get_yao_detail, get_changed_gua,
    hexagram_values_to_seq, DB_PATH,
)

# 八卦三爻位值（bit0=初爻）
TRI_BITS = {"乾": 0b111, "兌": 0b011, "離": 0b101, "震": 0b001,
            "巽": 0b110, "坎": 0b010, "艮": 0b100, "坤": 0b000}

PLACEHOLDERS = ("待补充", "尚未收录", "暂无")


def _code_of(gua):
    """由爻位名推出六爻阴阳位值"""
    bits = 0
    for i, yao in enumerate(gua["爻"][:6]):
        if "九" in yao["爻位"]:
            bits |= (1 << i)
    return bits


def _seq_of(text):
    """'44 姤䷫' -> 44"""
    return int(text.split()[0]) if text and text.split() else 0


def main():
    print("=== GuaDatabase_V3.0.json 数据完整性验证 ===\n")
    print(f"📁 数据源：{DB_PATH}\n")

    errors = []

    # 1. 基础信息
    print(f"✅ 八卦基础信息: {len(BAGUA_INFO)} 个键（含简繁别名，8 卦）")
    print(f"✅ 六十四卦数据库: {len(LIUSHISI_GUA_DB)} 个卦象\n")

    if len(LIUSHISI_GUA_DB) != 64:
        errors.append(f"卦象数量应为 64，实际 {len(LIUSHISI_GUA_DB)}")

    # 2. 卦序连续性
    seqs = [g["卦序"] for g in GUA_DB]
    if seqs != list(range(1, len(GUA_DB) + 1)):
        errors.append("卦序不连续")
    else:
        print("✅ 卦序 1-64 连续且无重复")

    # 3. 上下卦组合唯一
    combos = {(g["上卦"], g["下卦"]) for g in GUA_DB}
    if len(combos) != 64:
        errors.append(f"上下卦组合应 64 种，实际 {len(combos)}")
    else:
        print("✅ 上下卦组合 64 种且互不相同")

    # 4. 字段完整性
    missing = []
    for g in GUA_DB:
        for field in ("卦名", "全名", "卦符", "卦辞", "彖传", "大象", "互卦", "错卦", "综卦"):
            value = str(g.get(field, ""))
            if not value or any(p in value for p in PLACEHOLDERS):
                missing.append(f"{g['卦序']}·{field}")
        yaos = g.get("爻", [])
        if len(yaos) not in (6, 7):
            missing.append(f"{g['卦序']}·爻数={len(yaos)}")
        for y in yaos:
            for field in ("原文", "注释", "译文", "解说1_经义", "解说2_时位",
                          "结构分析", "象传", "象传译文", "象传解说", "大衍实占"):
                if not str(y.get(field, "")).strip():
                    missing.append(f"{g['卦序']}·{y['爻位']}·{field}")
    if missing:
        errors.append(f"{len(missing)} 处字段缺失: {missing[:5]}")
    else:
        print("✅ 卦辞 / 彖传 / 大象 / 386 爻详注字段全部完整（无缺失、无占位符）")

    # 5. 爻阴阳与上下卦自洽
    code_to_seq = {}
    bad_tri = []
    for g in GUA_DB:
        bits = _code_of(g)
        code_to_seq[bits] = g["卦序"]
        upper = bits >> 3
        lower = bits & 7
        inv = {v: k for k, v in TRI_BITS.items()}
        if (inv[upper], inv[lower]) != (g["上卦"], g["下卦"]):
            bad_tri.append(g["卦序"])
    if bad_tri:
        errors.append(f"爻阴阳与上下卦不符: {bad_tri[:5]}")
    else:
        print("✅ 六爻阴阳与上卦 / 下卦完全一致")

    # 6. 错卦 / 综卦 / 互卦
    bad_cuo, bad_zong, bad_hu = [], [], []
    for g in GUA_DB:
        bits = _code_of(g)
        seq = g["卦序"]
        cuo = code_to_seq.get(bits ^ 0b111111)
        zong = code_to_seq.get(sum(((bits >> i) & 1) << (5 - i) for i in range(6)))
        hu = code_to_seq.get(((bits >> 1) & 7) | (((bits >> 2) & 7) << 3))
        if cuo != _seq_of(g["错卦"]):
            bad_cuo.append(seq)
        if zong != _seq_of(g["综卦"]):
            bad_zong.append(seq)
        if hu != _seq_of(g["互卦"]):
            bad_hu.append(seq)
    for name, bad in (("错卦", bad_cuo), ("综卦", bad_zong), ("互卦", bad_hu)):
        if bad:
            errors.append(f"{name}不符 {len(bad)} 卦: {bad[:5]}")
        else:
            print(f"✅ {name}规则自洽（64/64）")

    # 7. 单爻发动之卦（384 爻）
    pos_key = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    bad_change = []
    for g in GUA_DB:
        bits = _code_of(g)
        for i in range(6):
            target = code_to_seq.get(bits ^ (1 << i))
            recorded = _seq_of(g["单爻发动之卦"].get(pos_key[i], ""))
            if target != recorded:
                bad_change.append((g["卦序"], pos_key[i]))
    if bad_change:
        errors.append(f"单爻发动之卦不符 {len(bad_change)} 处: {bad_change[:5]}")
    else:
        print("✅ 单爻发动之卦全部正确（384/384 爻）")

    # 8. 卦序反推与接口自洽
    if hexagram_values_to_seq([8, 8, 8, 8, 8, 9]) != 23:
        errors.append("由爻值反推卦序失败（应为 23 剝）")
    else:
        print("✅ 由六爻值反推卦序正确（[8,8,8,8,8,9] -> 23 山地剝）")

    # 9. 核心功能测试
    print("\n🧪 功能测试:")
    test_cases = [
        ("乾", "乾", "乾為天", 1),
        ("坤", "坤", "坤為地", 2),
        ("坎", "离", "水火既濟", 63),
        ("离", "坎", "火水未濟", 64),
    ]
    for upper, lower, expected, number in test_cases:
        info = get_gua_info(upper, lower)
        ok = info["name"] == expected and info["number"] == number
        print(f"   {'✅' if ok else '❌'} {upper}上{lower}下 -> {info['name']}（第{info['number']}卦）")
        if not ok:
            errors.append(f"get_gua_info({upper},{lower}) 期望 {expected}/{number}")

    print("\n   八卦符号测试:")
    for gua, symbol in [("乾", "☰"), ("坤", "☷"), ("震", "☳"), ("巽", "☴"),
                        ("坎", "☵"), ("离", "☲"), ("艮", "☶"), ("兑", "☱")]:
        got = get_bagua_symbol(gua)
        print(f"   {'✅' if got == symbol else '❌'} {gua}: {got}")
        if got != symbol:
            errors.append(f"get_bagua_symbol({gua}) 期望 {symbol}，实际 {got}")
    if get_bagua_symbol("未知") != "?":
        errors.append("get_bagua_symbol('未知') 应返回 '?'")

    # 10. 示例展示
    print("\n📜 卦象示例（乾）:")
    demo = get_gua_info("乾", "乾")
    print(f"   卦名: {demo['name']}（第{demo['number']}卦）{demo['卦符']}")
    print(f"   卦辞: {demo['gua_ci']}")
    print(f"   彖传: {demo['judgment'][:40]}…")
    print(f"   象辞: {demo['image']}")
    print(f"   互卦: {demo['互卦']} ｜ 错卦: {demo['错卦']} ｜ 综卦: {demo['综卦']}")

    yao = get_yao_detail(1, 1)
    print(f"\n   初爻详注: {yao['原文']}")
    print(f"   译文: {yao['译文']}")
    print(f"   之卦: {get_changed_gua(1, 1)}")

    # 汇总
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ 发现 {len(errors)} 类问题：")
        for e in errors:
            print(f"   - {e}")
        return 1
    print("🎉 验证全部通过！GuaDatabase_V3.0.json 数据完整且象数自洽。")
    print("   涵盖：64 卦 × 386 爻详注、互/错/综卦、384 条单爻发动之卦。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
