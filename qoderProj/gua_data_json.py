#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六十四卦数据适配层 —— 以 GuaDatabase_V3.0.json 为唯一数据来源

本模块替代 gua_database.py 中的内嵌精简字典，对外保持同名同签名的兼容接口：
    get_gua_info(上卦, 下卦)      -> dict
    get_bagua_symbol(卦名)        -> str
    get_yao_meaning(爻位, 爻值)   -> str
    BAGUA_INFO / LIUSHISI_GUA_DB / YAO_POSITIONS

并在此之上提供 JSON 全量数据（卦辞、彖传、大象、互/错/综卦、386 爻详注、
单爻发动之卦）的增强访问接口。

数据说明：
  * JSON 使用繁体字形（兌/離/剝/恆…），而调用方（dayansifa.py 等）内部使用
    简体卦名，故本模块在「查询入口」统一做简 -> 繁归一化，保证不漏查。
  * 输出文本保留 JSON 原文（繁体），以确保「以 JSON 数据为准」。
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "DB_PATH", "GUA_DB", "BAGUA_INFO", "LIUSHISI_GUA_DB", "YAO_POSITIONS",
    "get_gua_info", "get_bagua_symbol", "get_yao_meaning",
    "get_gua_by_seq", "get_gua_by_name", "get_yao_detail", "get_changed_gua",
    "hexagram_values_to_seq", "normalize_gua_name", "to_simplified",
]

DB_FILENAME = "GuaDatabase_V3.0.json"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILENAME)

# ---------------------------------------------------------------------------
# 简 -> 繁 字形映射（仅覆盖 64 卦名 / 八卦名中出现的差异字，避免引入外部依赖）
# ---------------------------------------------------------------------------
S2T_MAP = {
    "兑": "兌", "离": "離", "剥": "剝", "复": "復", "无": "無", "恒": "恆",
    "晋": "晉", "归": "歸", "丰": "豐", "涣": "渙", "节": "節", "济": "濟",
    "讼": "訟", "师": "師", "谦": "謙", "随": "隨", "蛊": "蠱", "临": "臨",
    "观": "觀", "贲": "賁", "遁": "遯", "损": "損", "渐": "漸", "过": "過",
    "壮": "壯", "颐": "頤", "众": "眾",
}
T2S_MAP = {v: k for k, v in S2T_MAP.items()}


def to_traditional(name: str) -> str:
    """简体卦名 -> 繁体（JSON 用字）"""
    return "".join(S2T_MAP.get(ch, ch) for ch in name)


def to_simplified(name: str) -> str:
    """繁体卦名 -> 简体（用于与既有简体界面文案对齐）"""
    return "".join(T2S_MAP.get(ch, ch) for ch in name)


def normalize_gua_name(name: str) -> str:
    """归一化卦名：已可在库中命中则原样返回，否则尝试简 -> 繁转换"""
    if name in _NAME_INDEX:
        return name
    traditional = to_traditional(name)
    if traditional in _NAME_INDEX:
        return traditional
    return name


# ---------------------------------------------------------------------------
# 八卦基础信息（JSON 无独立八卦表，符号沿用传统三画符号，取象自爻辞提取）
# ---------------------------------------------------------------------------
BAGUA_BASE = {
    "乾": {"symbol": "☰", "element": "天", "attribute": "刚健", "xiang": "健、刚健、主动、天"},
    "坤": {"symbol": "☷", "element": "地", "attribute": "柔顺", "xiang": "顺、承载、包容、地"},
    "震": {"symbol": "☳", "element": "雷", "attribute": "动", "xiang": "动、发起、震动、雷"},
    "巽": {"symbol": "☴", "element": "风", "attribute": "入", "xiang": "入、顺入、渗透、风木"},
    "坎": {"symbol": "☵", "element": "水", "attribute": "险", "xiang": "险、陷、流行、水"},
    "離": {"symbol": "☲", "element": "火", "attribute": "丽", "xiang": "明、附丽、文明、火"},
    "艮": {"symbol": "☶", "element": "山", "attribute": "止", "xiang": "止、界限、山"},
    "兌": {"symbol": "☱", "element": "泽", "attribute": "悦", "xiang": "说悦、交流、泽"},
}

# 爻位含义（与旧版一致）
YAO_POSITIONS = {
    1: "初爻（地位）",
    2: "二爻（人位）",
    3: "三爻（天位）",
    4: "四爻（地位）",
    5: "五爻（君位）",
    6: "上爻（天位）",
}

# 爻值含义
YAO_VALUE_NAMES = {6: "老阴", 7: "少阳", 8: "少阴", 9: "老阳"}

_POSITION_KEYS = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# 八卦三爻组合（bit0=初爻）用于由爻值反推卦序
_TRI_BITS = {"乾": 0b111, "兌": 0b011, "離": 0b101, "震": 0b001,
             "巽": 0b110, "坎": 0b010, "艮": 0b100, "坤": 0b000}
_TRI_BY_BITS = {v: k for k, v in _TRI_BITS.items()}

# ---------------------------------------------------------------------------
# 惰性加载与索引
# ---------------------------------------------------------------------------
GUA_DB: List[Dict[str, Any]] = []
_NAME_INDEX: Dict[str, Dict[str, Any]] = {}
_SEQ_INDEX: Dict[int, Dict[str, Any]] = {}
_TRIGRAM_INDEX: Dict[Tuple[str, str], Dict[str, Any]] = {}
_CODE_TO_SEQ: Dict[int, int] = {}
BAGUA_INFO: Dict[str, Dict[str, str]] = {}
LIUSHISI_GUA_DB: Dict[Tuple[str, str], Dict[str, Any]] = {}
_loaded = False


def _ensure_loaded() -> None:
    """首次访问时加载 JSON 并建立索引"""
    global _loaded
    if _loaded:
        return
    _load()
    _loaded = True


def _load() -> None:
    global GUA_DB
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"卦象数据库不存在: {DB_PATH}")

    with open(DB_PATH, "r", encoding="utf-8") as f:
        GUA_DB = json.load(f)

    for gua in GUA_DB:
        seq = gua["卦序"]
        _SEQ_INDEX[seq] = gua
        _NAME_INDEX[gua["卦名"]] = gua
        _TRIGRAM_INDEX[(gua["上卦"], gua["下卦"])] = gua

        # 由爻位名反推六爻阴阳，建立 爻值组合 -> 卦序 索引
        bits = 0
        for i, yao in enumerate(gua["爻"][:6]):
            if "九" in yao["爻位"]:
                bits |= (1 << i)
        _CODE_TO_SEQ[bits] = seq

        # 兼容旧结构：{(上卦, 下卦): {...}}
        LIUSHISI_GUA_DB[(gua["上卦"], gua["下卦"])] = _build_legacy_entry(gua)

    # 八卦信息：繁体主键 + 简体别名
    for name, info in BAGUA_BASE.items():
        BAGUA_INFO[name] = dict(info)
        simplified = to_simplified(name)
        if simplified != name:
            BAGUA_INFO[simplified] = dict(info)


def _build_legacy_entry(gua: Dict[str, Any]) -> Dict[str, Any]:
    """把 JSON 单卦结构映射为旧版字段，并保留全部增强字段"""
    entry = {
        # ---- 旧版兼容字段 ----
        "name": gua["全名"],
        "number": gua["卦序"],
        "gua_ci": gua["卦辞"],
        "judgment": gua["彖传"],
        "image": gua["大象"],
        # ---- JSON 原生字段 ----
        "卦序": gua["卦序"],
        "卦名": gua["卦名"],
        "卦符": gua["卦符"],
        "全名": gua["全名"],
        "上卦": gua["上卦"],
        "下卦": gua["下卦"],
        "卦辞": gua["卦辞"],
        "彖传": gua["彖传"],
        "大象": gua["大象"],
        "互卦": gua["互卦"],
        "错卦": gua["错卦"],
        "综卦": gua["综卦"],
        "爻": gua["爻"],
        "单爻发动之卦": gua["单爻发动之卦"],
    }
    return entry


# ---------------------------------------------------------------------------
# 兼容接口
# ---------------------------------------------------------------------------
def get_gua_info(upper_gua: str, lower_gua: str) -> Dict[str, Any]:
    """获取卦象信息（键约定为 (上卦, 下卦)）

    传入简体或繁体卦名均可，内部统一归一化后查询。
    """
    _ensure_loaded()
    upper = to_traditional(upper_gua)
    lower = to_traditional(lower_gua)
    entry = LIUSHISI_GUA_DB.get((upper, lower))
    if entry is not None:
        return entry
    return {
        "name": f"{upper_gua}{lower_gua}",
        "number": 0,
        "gua_ci": "卦辞待补充",
        "judgment": "此卦信息尚未收录",
        "image": "象辞待补充",
        "上卦": upper,
        "下卦": lower,
        "爻": [],
        "单爻发动之卦": {},
    }


def get_bagua_symbol(gua_name: str) -> str:
    """获取八卦三画符号（☰☷☳☴☵☲☶☱），简繁卦名均可"""
    _ensure_loaded()
    info = BAGUA_INFO.get(gua_name)
    if info is None:
        info = BAGUA_INFO.get(to_traditional(gua_name))
    if info is None:
        return "?"
    return info.get("symbol", "?")


def get_yao_meaning(position: int, value: int,
                    hexagram_values: Optional[List[int]] = None,
                    upper_gua: Optional[str] = None,
                    lower_gua: Optional[str] = None) -> str:
    """获取爻的含义说明

    兼容旧签名 get_yao_meaning(position, value)；
    额外传入 hexagram_values（六爻值，自下而上）或上下卦名时，
    返回 GuaDatabase_V3.0.json 中该爻的真实爻辞、译文与变卦之卦。
    """
    _ensure_loaded()
    pos_name = YAO_POSITIONS.get(position, f"第{position}爻")
    value_name = YAO_VALUE_NAMES.get(value, "未知爻象")

    gua = None
    if hexagram_values is not None and len(hexagram_values) == 6:
        gua = get_gua_by_seq(hexagram_values_to_seq(hexagram_values))
    elif upper_gua and lower_gua:
        upper = to_traditional(upper_gua)
        lower = to_traditional(lower_gua)
        gua = LIUSHISI_GUA_DB.get((upper, lower))

    if gua is None:
        # 旧版兜底文案
        if value == 9:
            return f"{pos_name}：老阳，变爻。刚强过度，宜谦逊。"
        if value == 8:
            return f"{pos_name}：少阴，静爻。柔顺得中，吉。"
        if value == 7:
            return f"{pos_name}：少阳，静爻。刚正得位，利。"
        if value == 6:
            return f"{pos_name}：老阴，变爻。柔弱过度，当变刚。"
        return f"{pos_name}：未知爻象"

    is_changing = value in (6, 9)

    # 六爻全动：乾之用九 / 坤之用六
    yao_list = gua.get("爻", [])
    if (hexagram_values is not None and len(hexagram_values) == 6
            and all(v in (6, 9) for v in hexagram_values)):
        special = next((y for y in yao_list if y["爻位"] in ("用九", "用六")), None)
        if special is not None:
            changed = "坤（六阳皆变）" if special["爻位"] == "用九" else "乾（六阴皆变）"
            return (f"{pos_name}·{value_name}（变爻）：{special['原文']}"
                    f"｜{special['译文']}｜【{special['爻位']}】之卦：{changed}")

    yao = _yao_at(yao_list, position)
    if yao is None:
        return f"{pos_name}：{value_name}"

    tag = "变爻" if is_changing else "静爻"
    parts = [f"{pos_name}·{value_name}（{tag}）：{yao['原文']}"]
    if yao.get("译文"):
        parts.append(f"译：{yao['译文']}")
    if is_changing:
        changed = get_changed_gua(gua["卦序"], position)
        if changed:
            parts.append(f"之卦：{changed}")
    return "｜".join(parts)


def _yao_order(yao: Dict[str, Any]) -> int:
    """由爻位名推爻序(1-6)，如 初九->1、九二->2、上六->6；用九/用六返回 0"""
    name = yao.get("爻位", "")
    if not name or name in ("用九", "用六"):
        return 0
    # 「初」「上」位于首字，其余（九二、六三…）位序在次字
    char = name[0] if name[0] in ("初", "上") else (name[1] if len(name) > 1 else "")
    key = char + "爻"
    return _POSITION_KEYS.index(key) + 1 if key in _POSITION_KEYS else 0


def _yao_at(yao_list: List[Dict[str, Any]], position: int) -> Optional[Dict[str, Any]]:
    """按爻位(1-6)取爻，优先按爻位名精确匹配"""
    if not yao_list:
        return None
    for yao in yao_list:
        if _yao_order(yao) == position:
            return yao
    if 1 <= position <= 6 and len(yao_list) >= position:
        return yao_list[position - 1]
    return None


# ---------------------------------------------------------------------------
# 增强接口
# ---------------------------------------------------------------------------
def get_gua_by_seq(seq: int) -> Optional[Dict[str, Any]]:
    """按卦序(1-64)取卦"""
    _ensure_loaded()
    gua = _SEQ_INDEX.get(seq)
    return LIUSHISI_GUA_DB.get((gua["上卦"], gua["下卦"])) if gua else None


def get_gua_by_name(name: str) -> Optional[Dict[str, Any]]:
    """按卦名取卦（简繁均可）"""
    _ensure_loaded()
    gua = _NAME_INDEX.get(name) or _NAME_INDEX.get(to_traditional(name))
    if gua is None:
        return None
    return LIUSHISI_GUA_DB.get((gua["上卦"], gua["下卦"]))


def get_yao_detail(seq: int, position: int) -> Optional[Dict[str, Any]]:
    """取指定卦序、爻位(1-6)的完整爻辞条目"""
    gua = get_gua_by_seq(seq)
    if gua is None:
        return None
    return _yao_at(gua.get("爻", []), position)


def get_changed_gua(seq: int, position: int) -> Optional[str]:
    """取单爻发动之卦，如 '44 姤䷫'"""
    gua = get_gua_by_seq(seq)
    if gua is None or not (1 <= position <= 6):
        return None
    mapping = gua.get("单爻发动之卦", {})
    return mapping.get(_POSITION_KEYS[position - 1])


def hexagram_values_to_seq(values: List[int]) -> int:
    """六爻值(6/7/8/9，自下而上) -> 卦序(1-64)"""
    _ensure_loaded()
    bits = 0
    for i, v in enumerate(values[:6]):
        if v % 2 == 1:  # 奇数为阳
            bits |= (1 << i)
    return _CODE_TO_SEQ.get(bits, 0)


def get_related_gua(seq: int) -> Dict[str, str]:
    """取互卦 / 错卦 / 综卦"""
    """取互卦 / 错卦 / 综卦"""
    gua = get_gua_by_seq(seq)
    if gua is None:
        return {}
    return {"互卦": gua["互卦"], "错卦": gua["错卦"], "综卦": gua["综卦"]}


def _parse_related(text: str) -> Tuple[int, str]:
    """解析 '44 姤䷫' -> (44, '姤')"""
    m = re.match(r"\s*(\d+)\s+(\S+)", text or "")
    if not m:
        return 0, ""
    return int(m.group(1)), m.group(2)


# ---------------------------------------------------------------------------
# 导入即加载：保证 `from gua_data_json import LIUSHISI_GUA_DB` 后立即可用
# （文件缺失时静默跳过，延迟到首次接口调用时抛出明确错误）
# ---------------------------------------------------------------------------
try:
    _ensure_loaded()
except FileNotFoundError:
    pass
