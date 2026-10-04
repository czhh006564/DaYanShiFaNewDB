/**
 * 大衍筮法 Web 应用主逻辑
 * 实现完整的用户交互和占卜流程
 */

// 全局变量
let currentHexagram = null;
let currentAnalysis = null;
let isInProgress = false;

/**
 * 页面加载完成后初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('大衍筮法 Web 应用已加载');
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    // 添加一些动画效果
    const title = document.querySelector('.title-main');
    if (title) {
        title.style.animation = 'fadeIn 2s ease-in';
    }
    
    // 为问题输入框添加字数统计
    const questionTextarea = document.getElementById('question');
    if (questionTextarea) {
        questionTextarea.addEventListener('input', function() {
            const maxLength = 200;
            const currentLength = this.value.length;
            
            // 创建或更新字数提示
            let counter = document.getElementById('char-counter');
            if (!counter) {
                counter = document.createElement('div');
                counter.id = 'char-counter';
                counter.style.cssText = 'text-align: right; font-size: 0.9rem; color: #daa520; margin-top: 5px;';
                this.parentNode.appendChild(counter);
            }
            
            counter.textContent = `${currentLength}/${maxLength}`;
            if (currentLength > maxLength) {
                counter.style.color = '#ff6b6b';
                this.value = this.value.substring(0, maxLength);
                counter.textContent = `${maxLength}/${maxLength}`;
            } else {
                counter.style.color = '#daa520';
            }
        });
    }
}

/**
 * 确保 GuaDatabase_V3.0.json 详注数据已加载（幂等）
 */
async function ensureJsonDatabase() {
    if (typeof GuaJson === 'undefined') return false;
    if (GuaJson.ready) return true;
    const ok = await GuaJson.load();
    if (!ok) {
        console.warn('[GuaJson] 详注数据未加载：' + GuaJson.error + '（将使用旧版精简数据）');
    }
    return ok;
}

/**
 * 取指定爻位的详注（未加载时返回 null）
 */
function getYaoDetailOf(position) {
    if (typeof GuaJson === 'undefined' || !GuaJson.ready) return null;
    return GuaJson.getYaoDetail(currentAnalysis.seq, position);
}

/**
 * 开始占卜
 */
async function startDivination() {
    if (isInProgress) return;
    
    isInProgress = true;
    
    // 获取用户输入的问题
    const questionInput = document.getElementById('question');
    const userQuestion = questionInput ? questionInput.value.trim() : '';
    
    // 隐藏准备区域，显示过程区域
    document.getElementById('divination-setup').style.display = 'none';
    document.getElementById('divination-process').style.display = 'block';
    
    // 滚动到过程区域
    document.getElementById('divination-process').scrollIntoView({ 
        behavior: 'smooth' 
    });
    
    try {
        // 确保 GuaDatabase_V3.0.json 详注数据已加载
        await ensureJsonDatabase();

        // 开始占卜过程
        await performDivination(userQuestion);
    } catch (error) {
        console.error('占卜过程出错:', error);
        showError('占卜过程中发生错误，请重试。');
        resetDivination();
    }
    
    isInProgress = false;
}

/**
 * 执行占卜过程
 */
async function performDivination(question) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const yaoList = document.getElementById('yao-list');
    const yarrowSticks = document.getElementById('yarrow-sticks');
    const yarrowInfo = document.getElementById('yarrow-info');
    
    // 清空之前的结果
    yaoList.innerHTML = '';
    
    // 显示开始信息
    updateProgress(0, '准备蓍草...');
    yarrowInfo.textContent = '正在准备49根蓍草...';
    yarrowSticks.textContent = daYanShiFa.generateYarrowDisplay(49);
    
    await daYanShiFa.sleep(1000);
    
    // 生成卦象
    const result = await daYanShiFa.generateHexagram((progress) => {
        const percentage = (progress.current / progress.total) * 100;
        updateProgress(percentage, progress.message);
        
        // 显示当前爻的生成过程
        showYaoGeneration(progress.current, progress.message);
    });
    
    currentHexagram = result.hexagram;
    
    // 完成占卜过程
    updateProgress(100, '占卜完成！');
    
    await daYanShiFa.sleep(1000);
    
    // 分析卦象
    currentAnalysis = daYanShiFa.analyzeHexagram(currentHexagram);

    // 数据保险：若拿到的是回落精简数据而 JSON 已就绪，则以 GuaDatabase_V3.0.json 重取卦层信息
    if (typeof GuaJson !== 'undefined' && GuaJson.ready &&
        currentAnalysis.guaInfo && !currentAnalysis.guaInfo.huGua) {
        const info = GuaJson.getGuaInfo(currentAnalysis.upperTrigram, currentAnalysis.lowerTrigram);
        if (info && info.number) {
            currentAnalysis.guaInfo = info;
            currentAnalysis.fullName = info.name;
            currentAnalysis.seq = info.seq;
            currentAnalysis.symbol = info.symbol || '';
        }
    }
    
    // 显示结果
    showResult(question);
}

/**
 * 更新进度条
 */
function updateProgress(percentage, message) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = message;
    }
}

/**
 * 显示爻的生成过程
 */
function showYaoGeneration(yaoNumber, message) {
    const yaoList = document.getElementById('yao-list');
    
    // 如果这个爻已经存在，就更新它；否则创建新的
    let yaoItem = document.getElementById(`yao-item-${yaoNumber}`);
    
    if (!yaoItem) {
        yaoItem = document.createElement('div');
        yaoItem.className = 'yao-item fade-in';
        yaoItem.id = `yao-item-${yaoNumber}`;
        yaoList.appendChild(yaoItem);
    }
    
    yaoItem.innerHTML = `
        <div class="yao-position">第${yaoNumber}爻</div>
        <div class="yao-process">${message}</div>
        <div class="yao-result">
            <span class="loading"></span>
        </div>
    `;
    
    // 如果占卜完成，显示实际结果
    if (currentHexagram && currentHexagram[yaoNumber - 1]) {
        const yaoValue = currentHexagram[yaoNumber - 1];
        const yaoSymbol = daYanShiFa.getYaoSymbol(yaoValue, yaoValue === 6 || yaoValue === 9);
        const isChanging = yaoValue === 6 || yaoValue === 9;
        
        yaoItem.innerHTML = `
            <div class="yao-position">第${yaoNumber}爻</div>
            <div class="yao-process">三次变化完成</div>
            <div class="yao-result ${isChanging ? 'changing' : ''}" title="${daYanShiFa.yaoMeanings[yaoValue]}">
                ${yaoSymbol}
            </div>
        `;
    }
}

/**
 * 显示占卜结果
 */
function showResult(question) {
    // 隐藏过程区域，显示结果区域
    document.getElementById('divination-process').style.display = 'none';
    document.getElementById('hexagram-result').style.display = 'block';
    
    // 滚动到结果区域
    document.getElementById('hexagram-result').scrollIntoView({ 
        behavior: 'smooth' 
    });
    
    // 构建本/互/变/综/错 五个视角，默认进入「本卦 = 现在」
    buildViews();
    switchView('ben');
}

/* ================= 五重卦象视角：本卦 / 互卦 / 变卦 / 综卦 / 错卦 ================= */

const VIEW_DEFS = [
    { key: 'ben',  name: '本卦', desc: '现在' },
    { key: 'hu',   name: '互卦', desc: '内情过程' },
    { key: 'bian', name: '变卦', desc: '结局走向' },
    { key: 'zong', name: '综卦', desc: '反过来，对立面视角' },
    { key: 'cuo',  name: '错卦', desc: '性质完全相反' }
];

let currentViews = {};
let currentViewKey = 'ben';

/** 由 JSON 的 "23 剝䷖" 提取卦序 */
function _seqFromText(text) {
    const m = /(\d+)/.exec(String(text || ''));
    return m ? parseInt(m[1], 10) : 0;
}

/** 由卦序生成六爻值（7 少阳 / 8 少阴，自下而上） */
function valuesFromSeq(seq) {
    const g = GuaJson.bySeq[seq];
    if (!g) return null;
    return g['爻'].slice(0, 6).map(y => (y['爻位'].indexOf('九') >= 0 ? 7 : 8));
}

/** 构造某视角的分析对象 */
function analysisForView(seq, values, changingYaos) {
    const g = GuaJson.bySeq[seq];
    if (!g) return null;
    const guaInfo = GuaJson.getGuaInfo(g['上卦'], g['下卦']);
    return {
        lowerTrigram: g['下卦'],
        upperTrigram: g['上卦'],
        fullName: guaInfo.name,
        changingYaos: changingYaos || [],
        hexagramValues: values,
        guaInfo: guaInfo,
        seq: seq,
        symbol: guaInfo.symbol || ''
    };
}

/** 起卦后构建五个视角 */
function buildViews() {
    currentViews = {};
    if (!currentAnalysis) return;

    const info = currentAnalysis.guaInfo;
    const benSeq = currentAnalysis.seq || info.number;
    const changes = currentAnalysis.changingYaos || [];
    const flip = v => (v === 9 ? 8 : v === 6 ? 7 : v);

    if (typeof GuaJson === 'undefined' || !GuaJson.ready) {
        currentViews.ben = Object.assign({}, VIEW_DEFS[0], {
            seq: benSeq, values: currentHexagram.slice(), analysis: currentAnalysis, note: ''
        });
        return;
    }

    // 变卦：所有变爻同时翻转（老阳 9→8，老阴 6→7）
    const bianValues = currentHexagram.slice();
    changes.forEach(p => {
        if (p >= 1 && p <= 6) bianValues[p - 1] = flip(bianValues[p - 1]);
    });
    const bianSeq = (changes.length ? GuaJson.hexagramValuesToSeq(bianValues) : benSeq) || benSeq;

    const make = (def, seq, changing, note) => {
        let values;
        if (def.key === 'ben') values = currentHexagram.slice();
        else if (def.key === 'bian') values = bianValues.slice();
        else values = valuesFromSeq(seq) || currentHexagram.slice();

        return Object.assign({}, def, {
            seq: seq,
            values: values,
            changing: changing,
            analysis: analysisForView(seq, values, changing),
            note: note
        });
    };

    currentViews.ben  = make(VIEW_DEFS[0], benSeq, changes, '');
    currentViews.hu   = make(VIEW_DEFS[1], _seqFromText(info.huGua)   || benSeq, [], '由本卦二三四爻为下卦、三四五爻为上卦相叠而成，主事情的脉络隐微。');
    currentViews.bian = make(VIEW_DEFS[2], bianSeq,                      [], changes.length ? `第${changes.join('、')}爻发动，由本卦变化而来，主结局走向。` : '静卦无变爻，变卦与本卦相同，事态稳定。');
    currentViews.zong = make(VIEW_DEFS[3], _seqFromText(info.zongGua) || benSeq, [], '将本卦上下颠倒（覆卦），是对立面、对方视角所见之象。');
    currentViews.cuo  = make(VIEW_DEFS[4], _seqFromText(info.cuoGua)  || benSeq, [], '六爻阴阳全反，性质完全相反，主事情的反面与失中之象。');
}

/** 切换卦象视角 */
function switchView(key) {
    if (!currentViews || !currentViews[key]) key = 'ben';
    currentViewKey = key;
    const view = currentViews[key];

    if (view.analysis) currentAnalysis = view.analysis;

    VIEW_DEFS.forEach(d => {
        const btn = document.getElementById('viewbtn-' + d.key);
        if (btn) btn.classList.toggle('active', d.key === key);
    });

    const title = document.getElementById('result-title');
    if (title) title.textContent = `🔮 ${view.name} · ${view.desc}`;

    const note = document.getElementById('view-note');
    if (note) note.textContent = view.note || '';

    // 每次切换视角默认回到「总览」标签
    setActiveTab('summary');
    displayHexagram();
    displayHexagramInfo();
    displayExplanation();
}

/* ================= 爻线悬停：展示当前爻辞 ================= */

function showYaoTooltip(event, detail, changed, pos, yao) {
    const tip = document.getElementById('yao-tooltip');
    if (!tip) return;

    let html = `<div class="tt-title">${YAO_POSITION_NAMES[pos - 1]}${detail ? ' · ' + detail['爻位'] : ''}</div>`;
    if (detail) {
        html += `<div class="tt-original">${detail['原文']}</div>`;
        html += `<div class="tt-row"><b>译文：</b>${detail['译文']}</div>`;
        html += `<div class="tt-row"><b>经义：</b>${detail['解说1_经义']}</div>`;
        html += `<div class="tt-row"><b>时位：</b>${detail['解说2_时位']}</div>`;
        if (detail['象传']) html += `<div class="tt-row"><b>象传：</b>${detail['象传']}</div>`;
    } else {
        html += `<div class="tt-original">${daYanShiFa.getYaoMeaning(pos, yao)}</div>`;
    }
    if (changed) html += `<div class="tt-row"><b>之卦：</b>${changed}</div>`;

    tip.innerHTML = html;
    tip.style.display = 'block';
    moveYaoTooltip(event);
}

function moveYaoTooltip(event) {
    const tip = document.getElementById('yao-tooltip');
    if (!tip) return;
    const pad = 16;
    const rect = tip.getBoundingClientRect();
    let left = event.clientX + pad;
    let top = event.clientY + pad;
    if (left + rect.width > window.innerWidth - 8) left = event.clientX - rect.width - pad;
    if (top + rect.height > window.innerHeight - 8) top = Math.max(8, event.clientY - rect.height - pad);
    tip.style.left = Math.max(8, left) + 'px';
    tip.style.top = top + 'px';
}

function hideYaoTooltip() {
    const tip = document.getElementById('yao-tooltip');
    if (tip) tip.style.display = 'none';
}

/**
 * 显示卦象图形
 */
function displayHexagram() {
    const hexagramVisual = document.getElementById('hexagram-visual');
    if (!hexagramVisual) return;

    // 使用当前视角的六爻值（本卦为实际筮得的 6/7/8/9，其余视角为静爻 7/8）
    const view = currentViews[currentViewKey];
    const values = (view && view.values) ? view.values : currentHexagram;
    if (!values) return;

    hexagramVisual.innerHTML = '';

    const ready = (typeof GuaJson !== 'undefined' && GuaJson.ready && currentAnalysis);

    // 从上到下显示（第6爻到第1爻）
    for (let i = 5; i >= 0; i--) {
        const yao = values[i];
        const pos = i + 1;
        const isChanging = yao === 6 || yao === 9;
        const isYang = yao % 2 === 1;

        const yaoLine = document.createElement('div');
        yaoLine.className = `yao-line ${isYang ? 'yang' : 'yin'} ${isChanging ? 'changing' : ''}`;

        // 悬停展示当前爻的完整爻辞（取自 GuaDatabase_V3.0.json）
        const detail = getYaoDetailOf(pos);
        const changed = ready ? GuaJson.getChangedGua(currentAnalysis.seq, pos) : null;

        yaoLine.addEventListener('mouseenter', e => showYaoTooltip(e, detail, changed, pos, yao));
        yaoLine.addEventListener('mousemove', moveYaoTooltip);
        yaoLine.addEventListener('mouseleave', hideYaoTooltip);

        if (isYang) {
            yaoLine.textContent = isChanging ? '━━━━━━ ○' : '━━━━━━';
        } else {
            yaoLine.textContent = isChanging ? '━━  ━━ ×' : '━━  ━━';
        }

        hexagramVisual.appendChild(yaoLine);
    }
}

/**
 * 显示卦象基本信息
 */
function displayHexagramInfo() {
    if (!currentAnalysis) return;
    
    // 卦名
    const hexagramName = document.getElementById('hexagram-name');
    if (hexagramName) {
        hexagramName.textContent = currentAnalysis.fullName;
    }

    // 卦符（六画卦 Unicode）
    const symbolEl = document.getElementById('hexagram-symbol');
    if (symbolEl) {
        symbolEl.textContent = currentAnalysis.symbol || '';
    }

    // 卦序
    const numberEl = document.getElementById('gua-number');
    if (numberEl) {
        numberEl.textContent = currentAnalysis.guaInfo.number
            ? `第${currentAnalysis.guaInfo.number}卦` : '-';
    }
    
    // 八卦符号优先取自 GuaDatabase_V3.0.json（含简繁归一化），旧库作兜底
    const baguaSymbol = (name) => (typeof GuaJson !== 'undefined' && GuaJson.ready)
        ? GuaJson.getBaguaSymbol(name) : getBaguaSymbol(name);

    // 上卦信息
    const upperTrigram = document.getElementById('upper-trigram');
    const upperSymbol = document.getElementById('upper-symbol');
    if (upperTrigram && upperSymbol) {
        upperTrigram.textContent = currentAnalysis.upperTrigram;
        upperSymbol.textContent = baguaSymbol(currentAnalysis.upperTrigram);
    }
    
    // 下卦信息
    const lowerTrigram = document.getElementById('lower-trigram');
    const lowerSymbol = document.getElementById('lower-symbol');
    if (lowerTrigram && lowerSymbol) {
        lowerTrigram.textContent = currentAnalysis.lowerTrigram;
        lowerSymbol.textContent = baguaSymbol(currentAnalysis.lowerTrigram);
    }
}

/**
 * 显示详细解释
 */
function displayExplanation() {
    if (!currentAnalysis) return;

    const guaInfo = currentAnalysis.guaInfo;

    // 卦辞
    const guaCi = document.getElementById('gua-ci');
    if (guaCi) {
        guaCi.textContent = guaInfo.guaCi || '卦辞待补充';
    }

    // 彖传
    const judgment = document.getElementById('judgment');
    if (judgment) {
        judgment.textContent = guaInfo.judgment || '彖传待补充';
    }

    // 象辞
    const image = document.getElementById('image');
    if (image) {
        image.textContent = guaInfo.image || '象辞待补充';
    }

    // 卦象关系：互卦 / 错卦 / 综卦
    const related = document.getElementById('related-gua');
    if (related) {
        related.textContent = guaInfo.huGua
            ? `互卦：${guaInfo.huGua}　错卦：${guaInfo.cuoGua}　综卦：${guaInfo.zongGua}`
            : '—（详注数据未加载）';
    }

    // 六爻爻辞：完整详注平铺展示
    const yaoCiList = document.getElementById('yao-ci-list');
    if (yaoCiList) {
        yaoCiList.innerHTML = renderYaoCards();
    }

    // 变爻信息
    const changingYaos = document.getElementById('changing-yaos');
    const changingDetail = document.getElementById('changing-detail');

    if (changingYaos) {
        changingYaos.textContent = currentAnalysis.changingYaos.length > 0
            ? `第${currentAnalysis.changingYaos.join('、')}爻为变爻。变爻代表事态发展的关键转折点，需特别关注。`
            : '无变爻（静卦）：六爻皆静，事态相对稳定。';
    }
    if (changingDetail) {
        changingDetail.innerHTML = currentAnalysis.changingYaos.length > 0
            ? renderChangingCards(currentAnalysis.changingYaos)
            : '<p style="color:#daa520;">本卦无变爻，无需特别关注转折点。</p>';
    }

    // 组成与建议
    renderExtra();
}

/**
 * 切换结果区标签页
 */
function setActiveTab(name) {
    const tabs = ['summary', 'yao', 'change', 'extra'];
    tabs.forEach(t => {
        const panel = document.getElementById('panel-' + t);
        const btn = document.getElementById('tabbtn-' + t);
        if (panel) panel.classList.toggle('active', t === name);
        if (btn) btn.classList.toggle('active', t === name);
    });
}

function switchTab(name) {
    setActiveTab(name);
    const target = document.getElementById('panel-' + name);
    if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/** 爻位通名 */
const YAO_POSITION_NAMES = ['初爻（地位）', '二爻（人位）', '三爻（天位）',
                            '四爻（地位）', '五爻（君位）', '上爻（天位）'];

/**
 * 六爻爻辞卡片：386 爻完整详注（原文/译文/注释/经义/时位/结构/象传×3/实占/之卦）
 */
function renderYaoCards() {
    let html = '';
    const ready = (typeof GuaJson !== 'undefined' && GuaJson.ready);

    for (let i = 1; i <= 6; i++) {
        const detail = getYaoDetailOf(i);
        if (!detail) continue;
        const isChanging = currentAnalysis.changingYaos.indexOf(i) >= 0;
        const changed = ready ? GuaJson.getChangedGua(currentAnalysis.seq, i) : null;
        const dayan = (detail['大衍实占'] || '').replace(/\*\*/g, '');

        html += `<div class="yao-card${isChanging ? ' changing' : ''}">
            <div class="yao-card-head">
                <span class="yao-name">${detail['爻位']}</span>
                <span class="yao-tag">${YAO_POSITION_NAMES[i - 1]}</span>
                ${isChanging ? '<span class="yao-tag changing">变爻</span>' : ''}
                ${changed ? `<span class="yao-tag">之卦 ${changed}</span>` : ''}
            </div>
            <div class="yao-original">${detail['原文']}</div>
            <div class="yao-row"><b>译文：</b>${detail['译文']}</div>
            <div class="yao-row"><b>注释：</b>${detail['注释']}</div>
            <div class="yao-row"><b>经义：</b>${detail['解说1_经义']}</div>
            <div class="yao-row"><b>时位：</b>${detail['解说2_时位']}</div>
            <div class="yao-row"><b>结构：</b>${detail['结构分析']}</div>
            <div class="yao-row"><b>象传：</b>${detail['象传']}</div>
            <div class="yao-row"><b>象传译：</b>${detail['象传译文']}</div>
            <div class="yao-row"><b>象传解：</b>${detail['象传解说']}</div>
            ${dayan ? `<div class="yao-row"><b>实占：</b>${dayan}</div>` : ''}
        </div>`;
    }

    // 六爻皆动时附加用九 / 用六
    const special = ready ? GuaJson.getSpecialYao(currentAnalysis.seq) : null;
    if (special && currentAnalysis.changingYaos.length === 6) {
        html += `<div class="yao-card changing">
            <div class="yao-card-head">
                <span class="yao-name">${special['爻位']}</span>
                <span class="yao-tag changing">六爻皆动</span>
            </div>
            <div class="yao-original">${special['原文']}</div>
            <div class="yao-row"><b>译文：</b>${special['译文']}</div>
            <div class="yao-row"><b>注释：</b>${special['注释']}</div>
            <div class="yao-row"><b>经义：</b>${special['解说1_经义']}</div>
        </div>`;
    }

    return html || '<p style="color:#daa520;">（详注数据未加载，仅能显示卦辞层面的精简信息）</p>';
}

/**
 * 变爻详解卡片
 */
function renderChangingCards(positions) {
    const ready = (typeof GuaJson !== 'undefined' && GuaJson.ready);
    let html = '';
    positions.forEach(pos => {
        const detail = getYaoDetailOf(pos);
        if (!detail) return;
        const changed = ready ? GuaJson.getChangedGua(currentAnalysis.seq, pos) : null;
        html += `<div class="yao-card changing">
            <div class="yao-card-head">
                <span class="yao-name">第${pos}爻 · ${detail['爻位']}</span>
                <span class="yao-tag">${YAO_POSITION_NAMES[pos - 1]}</span>
                ${changed ? `<span class="yao-tag">之卦 ${changed}</span>` : ''}
            </div>
            <div class="yao-original">${detail['原文']}</div>
            <div class="yao-row"><b>译文：</b>${detail['译文']}</div>
            <div class="yao-row"><b>经义：</b>${detail['解说1_经义']}</div>
            <div class="yao-row"><b>时位：</b>${detail['解说2_时位']}</div>
            <div class="yao-row"><b>象传：</b>${detail['象传']}</div>
            <div class="yao-row"><b>象传译：</b>${detail['象传译文']}</div>
        </div>`;
    });
    return html;
}

/**
 * 渲染「组成与建议」标签页
 */
function renderExtra() {
    if (!currentAnalysis) return;

    const compositionDetails = document.getElementById('composition-details');
    const adviceDetails = document.getElementById('advice-details');
    const guaInfo = currentAnalysis.guaInfo;

    // 卦象组成
    if (compositionDetails) {
        const baguaOf = (name) => (typeof GuaJson !== 'undefined' && GuaJson.ready)
            ? GuaJson.getBaguaInfo(name) : getBaguaInfo(name);
        const upperInfo = baguaOf(currentAnalysis.upperTrigram);
        const lowerInfo = baguaOf(currentAnalysis.lowerTrigram);

        compositionDetails.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">上卦：${currentAnalysis.upperTrigram} ${upperInfo.symbol}</h4>
                <p style="color: #daa520;">五行属性：${upperInfo.element}，特性：${upperInfo.attribute}${upperInfo.xiang ? '，取象：' + upperInfo.xiang : ''}</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">下卦：${currentAnalysis.lowerTrigram} ${lowerInfo.symbol}</h4>
                <p style="color: #daa520;">五行属性：${lowerInfo.element}，特性：${lowerInfo.attribute}${lowerInfo.xiang ? '，取象：' + lowerInfo.xiang : ''}</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">卦象序号</h4>
                <p style="color: #daa520;">《周易》第${guaInfo.number || '?'}卦${guaInfo.symbol ? '　' + guaInfo.symbol : ''}</p>
            </div>
            <div>
                <h4 style="color: #d4af37; margin-bottom: 10px;">卦象关系</h4>
                <p style="color: #daa520;">${guaInfo.huGua ? `互卦：${guaInfo.huGua}｜错卦：${guaInfo.cuoGua}｜综卦：${guaInfo.zongGua}` : '—'}</p>
            </div>
        `;
    }

    // 占卜建议
    if (adviceDetails) {
        const advice = daYanShiFa.generateAdvice(currentAnalysis);
        adviceDetails.innerHTML = `
            <div style="color: #daa520; line-height: 1.6;">
                ${advice.replace(/\n/g, '<br>')}
            </div>
            <div style="margin-top: 20px; padding: 15px; background: rgba(212,175,55,0.1); border-radius: 8px;">
                <h5 style="color: #d4af37; margin-bottom: 10px;">💡 使用提示</h5>
                <p style="color: #daa520; font-size: 0.9rem;">
                    占卜结果仅供参考，请结合实际情况理性判断。易经强调"自强不息"和"厚德载物"，
                    真正的智慧在于通过占卜启发思考，而非依赖占卜结果。
                </p>
            </div>
        `;
    }
}

/**
 * 显示详细解释弹窗
 */
function showDetails() {
    // 「查看详细解释」已改为标签页平铺展示，直接跳转到六爻爻辞
    switchTab('yao');
    return;

    if (!currentAnalysis) return;
    
    const modal = document.getElementById('detail-modal');
    const yaoDetails = document.getElementById('yao-details');
    const compositionDetails = document.getElementById('composition-details');
    const adviceDetails = document.getElementById('advice-details');
    
    if (!modal) return;
    
    // 爻象详解（优先使用 GuaDatabase_V3.0.json 的完整详注）
    if (yaoDetails) {
        let yaoHtml = '';
        currentHexagram.forEach((yao, index) => {
            const position = index + 1;
            const isChanging = yao === 6 || yao === 9;
            const detail = getYaoDetailOf(position);

            if (detail) {
                const changed = (typeof GuaJson !== 'undefined' && GuaJson.ready)
                    ? GuaJson.getChangedGua(currentAnalysis.seq, position) : null;
                const dayan = (detail['大衍实占'] || '').replace(/\*\*/g, '');
                yaoHtml += `
                    <div class="yao-detail-item" style="margin-bottom: 15px; padding: 10px; background: rgba(212,175,55,0.1); border-radius: 8px;">
                        <div style="font-weight: bold; color: #d4af37; margin-bottom: 5px;">
                            ${detail['爻位']}　${detail['原文']}${isChanging ? ' [变爻]' : ''}
                        </div>
                        <div style="color: #daa520; margin-bottom: 4px;">译：${detail['译文']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">注释：${detail['注释']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">经义：${detail['解说1_经义']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">时位：${detail['解说2_时位']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">结构：${detail['结构分析']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">${detail['象传']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">${detail['象传译文']}</div>
                        <div style="color: #daa520; margin-bottom: 4px;">${detail['象传解说']}</div>
                        ${changed ? `<div style="color:#d4af37; margin-bottom: 4px;">之卦：${changed}</div>` : ''}
                        <div style="color: #daa520;">实占：${dayan}</div>
                    </div>
                `;
            } else {
                const meaning = daYanShiFa.getYaoMeaning(position, yao);
                yaoHtml += `
                    <div class="yao-detail-item" style="margin-bottom: 15px; padding: 10px; background: rgba(212,175,55,0.1); border-radius: 8px;">
                        <div style="font-weight: bold; color: #d4af37; margin-bottom: 5px;">
                            ${meaning}
                        </div>
                        <div style="color: #daa520;">
                            ${isChanging ? '此爻为变爻，表示此方面将有重要变化。' : '此爻相对稳定，无明显变化。'}
                        </div>
                    </div>
                `;
            }
        });
        yaoDetails.innerHTML = yaoHtml;
    }
    
    // 卦象组成
    if (compositionDetails) {
        const baguaOf = (name) => (typeof GuaJson !== 'undefined' && GuaJson.ready)
            ? GuaJson.getBaguaInfo(name) : getBaguaInfo(name);
        const upperInfo = baguaOf(currentAnalysis.upperTrigram);
        const lowerInfo = baguaOf(currentAnalysis.lowerTrigram);
        
        compositionDetails.innerHTML = `
            <div style="margin-bottom: 20px;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">上卦：${currentAnalysis.upperTrigram} ${upperInfo.symbol}</h4>
                <p style="color: #daa520;">五行属性：${upperInfo.element}，特性：${upperInfo.attribute}${upperInfo.xiang ? '，取象：' + upperInfo.xiang : ''}</p>
            </div>
            <div style="margin-bottom: 20px;">
                <h4 style="color: #d4af37; margin-bottom: 10px;">下卦：${currentAnalysis.lowerTrigram} ${lowerInfo.symbol}</h4>
                <p style="color: #daa520;">五行属性：${lowerInfo.element}，特性：${lowerInfo.attribute}${lowerInfo.xiang ? '，取象：' + lowerInfo.xiang : ''}</p>
            </div>
            <div>
                <h4 style="color: #d4af37; margin-bottom: 10px;">卦象序号</h4>
                <p style="color: #daa520;">《周易》第${currentAnalysis.guaInfo.number || '?'}卦</p>
            </div>
        `;
    }
    
    // 占卜建议
    if (adviceDetails) {
        const advice = daYanShiFa.generateAdvice(currentAnalysis);
        adviceDetails.innerHTML = `
            <div style="color: #daa520; line-height: 1.6;">
                ${advice.replace(/\n/g, '<br>')}
            </div>
            <div style="margin-top: 20px; padding: 15px; background: rgba(212,175,55,0.1); border-radius: 8px;">
                <h5 style="color: #d4af37; margin-bottom: 10px;">💡 使用提示</h5>
                <p style="color: #daa520; font-size: 0.9rem;">
                    占卜结果仅供参考，请结合实际情况理性判断。易经强调"自强不息"和"厚德载物"，
                    真正的智慧在于通过占卜启发思考，而非依赖占卜结果。
                </p>
            </div>
        `;
    }
    
    modal.style.display = 'flex';
    modal.style.animation = 'fadeIn 0.3s ease-in';
}

/**
 * 关闭详细解释弹窗
 */
function closeDetails() {
    const modal = document.getElementById('detail-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * 重置占卜，返回初始状态
 */
function resetDivination() {
    isInProgress = false;
    currentHexagram = null;
    currentAnalysis = null;
    currentViews = {};
    currentViewKey = 'ben';
    hideYaoTooltip();

    const viewNote = document.getElementById('view-note');
    if (viewNote) viewNote.textContent = '';
    const resultTitle = document.getElementById('result-title');
    if (resultTitle) resultTitle.textContent = '🔮 卦象结果';
    
    // 隐藏所有区域
    document.getElementById('divination-process').style.display = 'none';
    document.getElementById('hexagram-result').style.display = 'none';
    
    // 显示准备区域
    document.getElementById('divination-setup').style.display = 'block';
    
    // 清空输入
    const questionInput = document.getElementById('question');
    if (questionInput) {
        questionInput.value = '';
        // 触发input事件更新字数统计
        questionInput.dispatchEvent(new Event('input'));
    }
    
    // 重置进度条
    updateProgress(0, '准备开始...');
    
    // 清空结果显示
    const yaoList = document.getElementById('yao-list');
    if (yaoList) {
        yaoList.innerHTML = '';
    }
    
    // 滚动回顶部
    document.querySelector('.header').scrollIntoView({ 
        behavior: 'smooth' 
    });
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 107, 107, 0.9);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1001;
        font-size: 1rem;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 3000);
}

/**
 * 显示成功信息
 */
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(76, 175, 80, 0.9);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        z-index: 1001;
        font-size: 1rem;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    successDiv.textContent = message;
    
    document.body.appendChild(successDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
}

// 键盘快捷键支持
document.addEventListener('keydown', function(event) {
    // ESC键关闭模态窗口
    if (event.key === 'Escape') {
        closeDetails();
    }
    
    // Enter键开始占卜（仅在准备阶段）
    if (event.key === 'Enter' && event.ctrlKey) {
        const setupSection = document.getElementById('divination-setup');
        if (setupSection && setupSection.style.display !== 'none') {
            startDivination();
        }
    }
});

// 点击模态窗口外部关闭
document.addEventListener('click', function(event) {
    const modal = document.getElementById('detail-modal');
    if (modal && event.target === modal) {
        closeDetails();
    }
});

// 防止页面刷新时丢失状态的提示
window.addEventListener('beforeunload', function(event) {
    if (isInProgress) {
        event.preventDefault();
        event.returnValue = '占卜正在进行中，确定要离开页面吗？';
        return event.returnValue;
    }
});

// 页面可见性变化时的处理
document.addEventListener('visibilitychange', function() {
    if (document.hidden && isInProgress) {
        console.log('页面被隐藏，占卜过程可能会受到影响');
    }
});

// 导出主要函数供HTML调用
window.startDivination = startDivination;
window.showDetails = showDetails;
window.closeDetails = closeDetails;
window.resetDivination = resetDivination;