/**
 * GuaDatabase_V3.0.json 前端适配层
 *
 * 以 JSON（64 卦 386 爻完整详注）为唯一数据来源，为页面提供：
 *   - getGuaInfo(上卦, 下卦)        卦象全量信息（含爻数组、互/错/综卦、卦符）
 *   - hexagramValuesToSeq(六爻值)   由爻值反推卦序
 *   - getYaoDetail(卦序, 爻位)      指定爻的完整详注
 *   - getChangedGua(卦序, 爻位)     单爻发动之卦
 *   - getBaguaSymbol / getBaguaInfo 八卦符号与属性（简繁卦名均可）
 *
 * JSON 使用繁体字形（兌/離…），而页面内部使用简体（兑/离），
 * 故查询入口统一做 简 -> 繁 归一化。文本输出保留 JSON 原文。
 */

const GUA_JSON_URL = 'GuaDatabase_V3.0.json';

// 八卦三爻位值（bit0 = 初爻）
const GUA_TRI_BITS = {
    '乾': 0b111, '兌': 0b011, '離': 0b101, '震': 0b001,
    '巽': 0b110, '坎': 0b010, '艮': 0b100, '坤': 0b000
};

// 简 -> 繁（仅覆盖卦名中出现的差异字）
const GUA_S2T = {
    '兑': '兌', '离': '離', '剥': '剝', '复': '復', '无': '無', '恒': '恆',
    '晋': '晉', '归': '歸', '丰': '豐', '涣': '渙', '节': '節', '济': '濟',
    '讼': '訟', '师': '師', '谦': '謙', '随': '隨', '蛊': '蠱', '临': '臨',
    '观': '觀', '贲': '賁', '遁': '遯', '损': '損', '渐': '漸', '过': '過',
    '壮': '壯', '颐': '頤'
};

// 八卦基础属性（内联，避免依赖旧库；键为 JSON 用字，查询时做简繁归一化）
const GUA_BAGUA_BASE = {
    '乾': { symbol: '☰', element: '天', attribute: '刚健' },
    '坤': { symbol: '☷', element: '地', attribute: '柔顺' },
    '震': { symbol: '☳', element: '雷', attribute: '动' },
    '巽': { symbol: '☴', element: '风', attribute: '入' },
    '坎': { symbol: '☵', element: '水', attribute: '险' },
    '離': { symbol: '☲', element: '火', attribute: '丽' },
    '艮': { symbol: '☶', element: '山', attribute: '止' },
    '兌': { symbol: '☱', element: '泽', attribute: '悦' }
};

// 八卦取象（自 JSON 爻辞提取）
const GUA_BAGUA_XIANG = {
    '乾': '健、刚健、主动、天', '坤': '顺、承载、包容、地',
    '震': '动、发起、震动、雷', '巽': '入、顺入、渗透、风木',
    '坎': '险、陷、流行、水', '離': '明、附丽、文明、火',
    '艮': '止、界限、山', '兌': '说悦、交流、泽'
};

const GUA_POSITION_KEYS = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];

const GuaJson = {
    url: GUA_JSON_URL,
    raw: [],
    ready: false,
    error: null,
    source: null,          // 'inline' | 'fetch' —— 数据来源，便于排查
    bySeq: {},
    byTrigram: {},
    byName: {},
    codeToSeq: {},

    /**
     * 加载并构建索引（可重复调用，已加载则直接返回）
     *
     * 优先使用 window.GUA_DATABASE_V3（由 GuaDatabase_V3.0.data.js 以 <script>
     * 注入）。原因：file:// 协议下 fetch() 本地文件会被浏览器 CORS 拦截，而
     * <script> 标签不受该限制，这是纯 H5 离线版唯一可行的取数方式。
     * 未注入内联数据时（如 HTTP 静态托管且未引入数据脚本）仍回退到 fetch。
     */
    async load(url) {
        if (this.ready) return true;
        if (url) this.url = url;

        const inline = (typeof window !== 'undefined') ? window.GUA_DATABASE_V3 : null;
        if (Array.isArray(inline) && inline.length > 0) {
            try {
                this._build(inline);
                this.ready = true;
                this.source = 'inline';
                return true;
            } catch (e) {
                console.warn('[GuaJson] inline data invalid: ' + (e.message || e) + ', falling back to fetch');
            }
        }

        try {
            const resp = await fetch(this.url, { cache: 'no-cache' });
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            const data = await resp.json();
            if (!Array.isArray(data) || data.length === 0) throw new Error('数据为空');
            this._build(data);
            this.ready = true;
            this.source = 'fetch';
            return true;
        } catch (e) {
            this.error = e.message || String(e);
            console.warn('[GuaJson] 加载 GuaDatabase_V3.0.json 失败：' + this.error + '，回落旧数据');
            return false;
        }
    },

    _build(list) {
        this.raw = list;
        this.bySeq = {};
        this.byTrigram = {};
        this.byName = {};
        this.codeToSeq = {};
        list.forEach(gua => {
            this.bySeq[gua['卦序']] = gua;
            this.byTrigram[gua['上卦'] + '-' + gua['下卦']] = gua;
            this.byName[gua['卦名']] = gua;
            let bits = 0;
            gua['爻'].slice(0, 6).forEach((y, i) => {
                if (y['爻位'].indexOf('九') >= 0) bits |= (1 << i);
            });
            this.codeToSeq[bits] = gua['卦序'];
        });
    },

    /** 简体卦名 -> 繁体 */
    toTraditional(name) {
        return String(name).split('').map(ch => GUA_S2T[ch] || ch).join('');
    },

    /** 由爻位名推爻序(1-6)，用九/用六返回 0 */
    _yaoOrder(yao) {
        const n = yao['爻位'] || '';
        if (!n || n === '用九' || n === '用六') return 0;
        const ch = (n[0] === '初' || n[0] === '上') ? n[0] : (n[1] || '');
        const key = ch + '爻';
        const idx = GUA_POSITION_KEYS.indexOf(key);
        return idx >= 0 ? idx + 1 : 0;
    },

    /** 取卦象信息（兼容旧字段 + JSON 增强字段） */
    getGuaInfo(upperGua, lowerGua) {
        if (!this.ready) {
            // 未加载成功时回落到旧版 hexagram-database.js
            return getGuaInfo(upperGua, lowerGua);
        }
        const key = this.toTraditional(upperGua) + '-' + this.toTraditional(lowerGua);
        const g = this.byTrigram[key];
        if (!g) {
            return {
                name: `${upperGua}${lowerGua}`, number: 0,
                guaCi: '卦辞待补充', judgment: '此卦信息尚未收录', image: '象辞待补充',
                seq: 0, symbol: '', yaos: [], changedGua: {}
            };
        }
        return {
            // 旧版兼容字段
            name: g['全名'],
            number: g['卦序'],
            guaCi: g['卦辞'],
            judgment: g['彖传'],
            image: g['大象'],
            // JSON 增强字段
            seq: g['卦序'],
            symbol: g['卦符'],
            shortName: g['卦名'],
            upper: g['上卦'],
            lower: g['下卦'],
            huGua: g['互卦'],
            cuoGua: g['错卦'],
            zongGua: g['综卦'],
            yaos: g['爻'],
            changedGua: g['单爻发动之卦']
        };
    },

    /** 按卦序取卦象信息 */
    getGuaBySeq(seq) {
        const g = this.bySeq[seq];
        return g ? this.getGuaInfo(g['上卦'], g['下卦']) : null;
    },

    /** 六爻值(6/7/8/9，自下而上) -> 卦序 */
    hexagramValuesToSeq(values) {
        let bits = 0;
        values.slice(0, 6).forEach((v, i) => { if (v % 2 === 1) bits |= (1 << i); });
        return this.codeToSeq[bits] || 0;
    },

    /** 取指定爻的完整详注 */
    getYaoDetail(seq, position) {
        const info = this.getGuaBySeq(seq);
        if (!info || !info.yaos) return null;
        const found = info.yaos.find(y => this._yaoOrder(y) === position);
        return found || info.yaos[position - 1] || null;
    },

    /** 取单爻发动之卦，如 '44 姤䷫' */
    getChangedGua(seq, position) {
        const info = this.getGuaBySeq(seq);
        if (!info || !info.changedGua || position < 1 || position > 6) return null;
        return info.changedGua[GUA_POSITION_KEYS[position - 1]] || null;
    },

    /** 六爻皆动时的用九/用六辞 */
    getSpecialYao(seq) {
        const info = this.getGuaBySeq(seq);
        if (!info || !info.yaos) return null;
        return info.yaos.find(y => y['爻位'] === '用九' || y['爻位'] === '用六') || null;
    },

    /** 八卦符号（简繁均可） */
    getBaguaSymbol(guaName) {
        const t = this.toTraditional(guaName);
        const base = GUA_BAGUA_BASE[t] || GUA_BAGUA_BASE[guaName];
        return base ? base.symbol : '?';
    },

    /** 八卦属性（含 JSON 取象） */
    getBaguaInfo(guaName) {
        const t = this.toTraditional(guaName);
        const base = GUA_BAGUA_BASE[t] || GUA_BAGUA_BASE[guaName];
        if (!base) return { symbol: '?', element: '未知', attribute: '未知', xiang: '' };
        return {
            symbol: base.symbol,
            element: base.element,
            attribute: base.attribute,
            xiang: GUA_BAGUA_XIANG[t] || ''
        };
    }
};

// Node 环境下可直接 require 做自测
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GuaJson, GUA_TRI_BITS };
}
