/**
 * 纯 H5 增强模块：本地历史记录 + 结果导出
 *
 * 无任何后端依赖，数据全部存放在浏览器 localStorage。
 * 依赖 app.js 中的全局状态：currentHexagram / currentAnalysis / currentViews /
 * currentQuestion，以及 gua-data-json.js 的 GuaJson。
 * 本文件必须在 app.js 之后引入。
 */

const H5_HISTORY_KEY = 'dayansifa_history_v1';
const H5_HISTORY_MAX = 100;

const H5_YAO_TEXT = { 6: '老阴(变)', 7: '少阳', 8: '少阴', 9: '老阳(变)' };
const H5_POSITION_NAMES = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻'];

/* ============================ 本地历史记录 ============================ */

const H5History = {
    /** 读取全部记录（新的在前）；localStorage 不可用时返回空数组 */
    all() {
        try {
            const raw = localStorage.getItem(H5_HISTORY_KEY);
            const list = raw ? JSON.parse(raw) : [];
            return Array.isArray(list) ? list : [];
        } catch (e) {
            console.warn('[H5History] 读取失败: ' + (e.message || e));
            return [];
        }
    },

    _write(list) {
        try {
            localStorage.setItem(H5_HISTORY_KEY, JSON.stringify(list));
            return true;
        } catch (e) {
            console.warn('[H5History] 写入失败: ' + (e.message || e));
            showError && showError('本地存储不可用，历史记录未能保存。');
            return false;
        }
    },

    add(record) {
        const list = this.all();
        list.unshift(record);
        return this._write(list.slice(0, H5_HISTORY_MAX));
    },

    remove(id) {
        return this._write(this.all().filter(r => r.id !== id));
    },

    clear() {
        return this._write([]);
    }
};

/** 用当前占卜结果构建一条可序列化的记录 */
function buildCurrentRecord(question) {
    if (!currentAnalysis || !currentHexagram) return null;

    const ben = (typeof currentViews !== 'undefined' && currentViews && currentViews.ben) ? currentViews.ben : null;
    const values = ((ben && ben.values) ? ben.values : currentHexagram).slice();
    const info = currentAnalysis.guaInfo || {};
    const seq = currentAnalysis.seq || info.seq || info.number || 0;
    const changing = (currentAnalysis.changingYaos || []).slice();
    const jsonReady = (typeof GuaJson !== 'undefined' && GuaJson.ready);

    const yaos = [];
    for (let pos = 1; pos <= 6; pos++) {
        const d = jsonReady ? GuaJson.getYaoDetail(seq, pos) : null;
        const changed = jsonReady ? GuaJson.getChangedGua(seq, pos) : null;
        const value = values[pos - 1];
        yaos.push({
            position: pos,
            name: (d && d['爻位']) || H5_POSITION_NAMES[pos - 1],
            value: value,
            valueText: H5_YAO_TEXT[value] || String(value),
            original: (d && d['原文']) || (typeof daYanShiFa !== 'undefined' ? daYanShiFa.getYaoMeaning(pos, value) : ''),
            translation: (d && d['译文']) || '',
            jingyi: (d && d['解说1_经义']) || '',
            shiwei: (d && d['解说2_时位']) || '',
            xiang: (d && d['象传']) || '',
            changed: changed || ''
        });
    }

    const relation = {};
    ['hu', 'bian', 'zong', 'cuo'].forEach(key => {
        const v = (typeof currentViews !== 'undefined' && currentViews) ? currentViews[key] : null;
        if (!v) return;
        relation[key] = {
            name: (v.analysis && v.analysis.fullName) || '',
            seq: v.seq || 0,
            symbol: (v.analysis && v.analysis.symbol) || '',
            note: v.note || ''
        };
    });

    return {
        id: 'h' + Date.now() + Math.random().toString(36).slice(2, 7),
        time: new Date().toISOString(),
        question: question || '',
        seq: seq,
        fullName: currentAnalysis.fullName || info.name || '',
        shortName: info.shortName || '',
        symbol: currentAnalysis.symbol || info.symbol || '',
        upper: currentAnalysis.upperTrigram || info.upper || '',
        lower: currentAnalysis.lowerTrigram || info.lower || '',
        guaCi: info.guaCi || '',
        judgment: info.judgment || '',
        image: info.image || '',
        values: values,
        changing: changing,
        yaos: yaos,
        relation: relation
    };
}

/** 占卜完成后调用：保存当前结果到历史 */
function saveCurrentToHistory(question) {
    const rec = buildCurrentRecord(question);
    if (rec) H5History.add(rec);
}

/* ================================ 导出 ================================ */

function h5Escape(text) {
    return String(text == null ? '' : text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function h5Timestamp(rec) {
    const d = new Date(rec.time);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
}

function h5ReadableTime(rec) {
    const d = new Date(rec.time);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** 生成自包含的 HTML（内嵌样式，无外部资源） */
function buildRecordHtml(rec) {
    const yaoRows = rec.yaos.map(y => `
        <tr>
            <th>${h5Escape(y.name)}</th>
            <td>${h5Escape(y.valueText)}</td>
            <td class="orig">${h5Escape(y.original)}</td>
            <td>${h5Escape(y.translation)}</td>
            <td>${h5Escape(y.jingyi)}</td>
            <td>${h5Escape(y.shiwei)}</td>
            <td>${h5Escape(y.changed)}</td>
        </tr>`).join('');

    const relationRows = Object.keys(rec.relation).map(k => {
        const r = rec.relation[k];
        const label = { hu: '互卦', bian: '变卦', zong: '综卦', cuo: '错卦' }[k] || k;
        return `<tr><th>${label}</th><td>${h5Escape(r.name)} ${h5Escape(r.symbol)}</td><td>${h5Escape(r.note)}</td></tr>`;
    }).join('');

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>${h5Escape(rec.fullName)} - 大衍筮法占卜记录</title>
<style>
  body{font-family:"Songti SC","SimSun",serif;max-width:900px;margin:0 auto;padding:32px 24px;color:#2c2416;line-height:1.8;background:#fdfaf3}
  h1{text-align:center;border-bottom:2px solid #b8860b;padding-bottom:12px}
  .symbol{text-align:center;font-size:64px;margin:8px 0}
  .meta{background:#f5efe0;border-left:4px solid #b8860b;padding:12px 16px;margin:16px 0}
  h2{color:#8b6914;border-bottom:1px solid #e0d5bd;padding-bottom:6px;margin-top:28px}
  table{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}
  th,td{border:1px solid #ddd3bd;padding:8px 10px;text-align:left;vertical-align:top}
  thead th{background:#efe6d2}
  tbody th{width:72px;white-space:nowrap;background:#faf6ec}
  .orig{font-weight:bold}
  footer{margin-top:32px;text-align:center;color:#8a7d63;font-size:13px}
</style>
</head>
<body>
  <h1>大衍筮法占卜记录</h1>
  <div class="symbol">${h5Escape(rec.symbol)}</div>
  <div class="meta">
    <div><b>卦名：</b>${h5Escape(rec.fullName)}（第 ${rec.seq} 卦）</div>
    <div><b>上下卦：</b>上${h5Escape(rec.upper)} 下${h5Escape(rec.lower)}</div>
    <div><b>变爻：</b>${rec.changing.length ? '第 ' + rec.changing.join('、') + ' 爻发动' : '静卦无变爻'}</div>
    <div><b>时间：</b>${h5ReadableTime(rec)}</div>
    <div><b>问题：</b>${h5Escape(rec.question || '（未填写）')}</div>
  </div>
  <h2>卦辞 / 彖传 / 象辞</h2>
  <table>
    <tr><th>卦辞</th><td>${h5Escape(rec.guaCi)}</td></tr>
    <tr><th>彖传</th><td>${h5Escape(rec.judgment)}</td></tr>
    <tr><th>象辞</th><td>${h5Escape(rec.image)}</td></tr>
  </table>
  ${relationRows ? `<h2>五重卦象</h2><table>${relationRows}</table>` : ''}
  <h2>六爻详注</h2>
  <table>
    <thead><tr><th>爻位</th><th>爻性</th><th>爻辞原文</th><th>译文</th><th>经义</th><th>时位</th><th>之卦</th></tr></thead>
    <tbody>${yaoRows}</tbody>
  </table>
  <footer>大衍筮法 · 数字化周易占卜 —— 仅供学习参考</footer>
</body>
</html>`;
}

function buildRecordCsv(rec) {
    const cell = v => {
        const s = String(v == null ? '' : v);
        return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    };
    const header = ['时间', '问题', '卦名', '卦序', '上卦', '下卦',
        '初爻', '二爻', '三爻', '四爻', '五爻', '上爻', '变爻', '卦辞'];
    const row = [
        h5ReadableTime(rec), rec.question || '', rec.fullName, rec.seq,
        rec.upper, rec.lower,
        ...rec.yaos.map(y => y.valueText),
        rec.changing.length ? rec.changing.join('、') : '无',
        rec.guaCi
    ];
    // BOM 保证 Excel 正确识别 UTF-8
    return '\uFEFF' + [header, row].map(r => r.map(cell).join(',')).join('\r\n');
}

function h5Download(filename, content, mime) {
    const blob = new Blob([content], { type: mime + ';charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/** 导出单条记录：format = html | json | csv */
function exportRecord(rec, format) {
    if (!rec) { showError && showError('暂无可导出的占卜结果。'); return; }
    const stamp = h5Timestamp(rec);
    const base = `大衍筮法_${(rec.fullName || '卦象').replace(/[\/\\s]+/g, '')}_${stamp}`;

    if (format === 'html') {
        h5Download(base + '.html', buildRecordHtml(rec), 'text/html');
    } else if (format === 'json') {
        h5Download(base + '.json', JSON.stringify(rec, null, 2), 'application/json');
    } else if (format === 'csv') {
        h5Download(base + '.csv', buildRecordCsv(rec), 'text/csv');
    } else {
        showError && showError('不支持的导出格式：' + format);
        return;
    }
    showSuccess && showSuccess('已导出 ' + format.toUpperCase() + ' 文件。');
}

/** 导出当前占卜结果 */
function exportCurrent(format) {
    exportRecord(buildCurrentRecord(currentQuestion), format);
}

/** 导出全部历史记录为 JSON */
function exportHistoryJson() {
    const list = H5History.all();
    if (!list.length) { showError && showError('历史记录为空。'); return; }
    h5Download(`大衍筮法_历史记录_${list.length}条.json`, JSON.stringify(list, null, 2), 'application/json');
    showSuccess && showSuccess('已导出历史记录。');
}

/* ============================ 打印 / 另存 PDF ============================ */

function printRecord(rec) {
    if (!rec) { showError && showError('暂无可打印的占卜结果。'); return; }
    const frame = document.createElement('iframe');
    frame.setAttribute('aria-hidden', 'true');
    frame.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0;';
    frame.onload = function () {
        try {
            frame.contentWindow.focus();
            frame.contentWindow.print();
        } catch (e) {
            showError && showError('打印失败：' + (e.message || e));
        } finally {
            setTimeout(() => frame.parentNode && frame.parentNode.removeChild(frame), 500);
        }
    };
    document.body.appendChild(frame);
    frame.srcdoc = buildRecordHtml(rec);
}

function printCurrent() {
    printRecord(buildCurrentRecord(currentQuestion));
}

/* ============================ 历史记录面板 ============================ */

let h5ExpandedId = null;

function toggleHistory() {
    const modal = document.getElementById('history-modal');
    if (!modal) return;
    const visible = modal.style.display === 'flex';
    if (visible) { closeHistory(); return; }
    h5ExpandedId = null;
    renderHistory();
    modal.style.display = 'flex';
}

function closeHistory() {
    const modal = document.getElementById('history-modal');
    if (modal) modal.style.display = 'none';
}

function toggleHistoryItem(id) {
    h5ExpandedId = (h5ExpandedId === id) ? null : id;
    renderHistory();
}

function renderHistory() {
    const box = document.getElementById('history-list');
    if (!box) return;
    const list = H5History.all();

    if (!list.length) {
        box.innerHTML = '<p class="h5-empty">暂无历史记录。完成一次占卜后会自动保存在本机浏览器中。</p>';
        return;
    }

    box.innerHTML = list.map(function (rec) {
        const open = rec.id === h5ExpandedId;
        const head = `
            <div class="h5-item-head" onclick="toggleHistoryItem('${rec.id}')">
                <span class="h5-item-symbol">${h5Escape(rec.symbol || '')}</span>
                <span class="h5-item-name">${h5Escape(rec.fullName || '')}</span>
                <span class="h5-item-seq">第${rec.seq}卦</span>
                <span class="h5-item-time">${h5ReadableTime(rec)}</span>
                <span class="h5-item-toggle">${open ? '收起 ▲' : '详情 ▼'}</span>
            </div>`;

        if (!open) return `<div class="h5-item">${head}</div>`;

        const yaoRows = rec.yaos.map(y => `
            <tr>
                <th>${h5Escape(y.name)}</th>
                <td>${h5Escape(y.valueText)}</td>
                <td>${h5Escape(y.original)}</td>
                <td>${h5Escape(y.translation)}</td>
            </tr>`).join('');

        const detail = `
            <div class="h5-item-body">
                <p><b>问题：</b>${h5Escape(rec.question || '（未填写）')}</p>
                <p><b>上下卦：</b>上${h5Escape(rec.upper)} 下${h5Escape(rec.lower)}</p>
                <p><b>变爻：</b>${rec.changing.length ? '第 ' + rec.changing.join('、') + ' 爻发动' : '静卦无变爻'}</p>
                <p><b>卦辞：</b>${h5Escape(rec.guaCi)}</p>
                <table class="h5-mini-table">
                    <thead><tr><th>爻位</th><th>爻性</th><th>爻辞</th><th>译文</th></tr></thead>
                    <tbody>${yaoRows}</tbody>
                </table>
                <div class="h5-item-actions">
                    <button class="ghost-btn" onclick="h5ExportFromHistory('${rec.id}','html')">HTML</button>
                    <button class="ghost-btn" onclick="h5ExportFromHistory('${rec.id}','json')">JSON</button>
                    <button class="ghost-btn" onclick="h5ExportFromHistory('${rec.id}','csv')">CSV</button>
                    <button class="ghost-btn" onclick="printRecord(h5FindRecord('${rec.id}'))">打印</button>
                    <button class="ghost-btn danger" onclick="h5RemoveRecord('${rec.id}')">删除</button>
                </div>
            </div>`;

        return `<div class="h5-item expanded">${head}${detail}</div>`;
    }).join('');
}

function h5FindRecord(id) {
    return H5History.all().find(r => r.id === id) || null;
}

function h5ExportFromHistory(id, format) {
    exportRecord(h5FindRecord(id), format);
}

function h5RemoveRecord(id) {
    H5History.remove(id);
    h5ExpandedId = null;
    renderHistory();
}

function clearHistory() {
    if (!H5History.all().length) { showError && showError('历史记录已为空。'); return; }
    if (!confirm('确定清空全部本地历史记录？此操作不可恢复。')) return;
    H5History.clear();
    renderHistory();
    showSuccess && showSuccess('已清空历史记录。');
}

/* 导出供 HTML 内联 onclick 调用 */
window.toggleHistory = toggleHistory;
window.closeHistory = closeHistory;
window.toggleHistoryItem = toggleHistoryItem;
window.clearHistory = clearHistory;
window.exportHistoryJson = exportHistoryJson;
window.exportCurrent = exportCurrent;
window.printCurrent = printCurrent;
window.printRecord = printRecord;
window.h5ExportFromHistory = h5ExportFromHistory;
window.h5RemoveRecord = h5RemoveRecord;
window.h5FindRecord = h5FindRecord;
