/**
 * 大衍筮法核心算法 - JavaScript版本
 * 完整实现传统的大衍筮法占卜流程
 */

class DaYanShiFa {
    constructor() {
        // 三爻卦名对照表
        this.guaNames = {
            '111': '乾', '000': '坤', '100': '震', '011': '巽',
            '010': '坎', '101': '离', '001': '艮', '110': '兑'
        };
        
        // 爻象含义
        this.yaoMeanings = {
            6: "老阴（━━  ━━）变爻",
            7: "少阳（━━━━━━）静爻", 
            8: "少阴（━━  ━━）静爻",
            9: "老阳（━━━━━━）变爻"
        };
    }

    /**
     * 随机分蓍草为两堆
     * @param {number} total - 蓍草总数
     * @returns {Array} [左堆数量, 右堆数量]
     */
    divideYarrowSticks(total) {
        const left = Math.floor(Math.random() * (total - 1)) + 1;
        const right = total - left;
        return [left, right];
    }

    /**
     * 执行一次变化过程
     * @param {number} sticks - 当前蓍草数量
     * @returns {Object} {remaining: 剩余蓍草数, taken: 取出的蓍草数}
     */
    singleChange(sticks) {
        // 分为两堆
        let [left, right] = this.divideYarrowSticks(sticks);
        
        // 从右堆取一根放在手指间
        right -= 1;
        let taken = 1;
        
        // 用4除左堆，取余数
        let leftRemainder = left % 4;
        if (leftRemainder === 0) {
            leftRemainder = 4;
        }
        taken += leftRemainder;
        left -= leftRemainder;
        
        // 用4除右堆，取余数
        let rightRemainder = right % 4;
        if (rightRemainder === 0) {
            rightRemainder = 4;
        }
        taken += rightRemainder;
        right -= rightRemainder;
        
        const remaining = left + right;
        return { remaining, taken };
    }

    /**
     * 通过三次变化得到一个爻的值
     * @returns {Object} {yaoValue: 爻值, takenList: 每次变化取出的蓍草数列表}
     */
    getYaoValue() {
        let sticks = 49; // 初始蓍草数（50-1）
        const takenList = [];
        
        // 进行三次变化
        for (let i = 0; i < 3; i++) {
            const result = this.singleChange(sticks);
            sticks = result.remaining;
            takenList.push(result.taken);
        }
        
        // 根据最终剩余蓍草数确定爻值
        let yaoValue;
        switch (sticks) {
            case 36:
                yaoValue = 9; // 老阳
                break;
            case 32:
                yaoValue = 8; // 少阴
                break;
            case 28:
                yaoValue = 7; // 少阳
                break;
            case 24:
                yaoValue = 6; // 老阴
                break;
            default:
                // 理论上不应该出现其他情况，但为了安全起见
                yaoValue = 7;
                break;
        }
        
        return { yaoValue, takenList };
    }

    /**
     * 生成完整的六爻卦象
     * @param {Function} progressCallback - 进度回调函数
     * @returns {Promise} 返回卦象数据
     */
    async generateHexagram(progressCallback = null) {
        const hexagram = [];
        const processes = [];
        
        for (let i = 0; i < 6; i++) {
            // 更新进度
            if (progressCallback) {
                progressCallback({
                    current: i + 1,
                    total: 6,
                    message: `正在生成第${i + 1}爻...`
                });
            }
            
            // 添加延迟以显示动画效果
            await this.sleep(800);
            
            const result = this.getYaoValue();
            hexagram.push(result.yaoValue);
            processes.push(result.takenList);
        }
        
        return { hexagram, processes };
    }

    /**
     * 获取三爻卦名
     * @param {Array} trigram - 三个爻值数组
     * @returns {string} 卦名
     */
    getTrigramName(trigram) {
        // 将爻值转换为阴阳（奇数为阳1，偶数为阴0）
        const binaryTrigram = trigram.map(yao => yao % 2 === 1 ? '1' : '0').join('');
        return this.guaNames[binaryTrigram] || '未知卦';
    }

    /**
     * 分析卦象
     * @param {Array} hexagram - 六个爻值的数组（从下到上）
     * @returns {Object} 分析结果
     */
    analyzeHexagram(hexagram) {
        // 分析上下卦
        const lowerTrigram = hexagram.slice(0, 3); // 下三爻
        const upperTrigram = hexagram.slice(3, 6); // 上三爻
        
        const lowerName = this.getTrigramName(lowerTrigram);
        const upperName = this.getTrigramName(upperTrigram);
        
        // 查找完整卦名和信息（数据源：GuaDatabase_V3.0.json，未就绪时回落旧库）
        const hasJson = (typeof GuaJson !== 'undefined' && GuaJson.ready);
        const guaInfo = hasJson ? GuaJson.getGuaInfo(upperName, lowerName)
                                : getGuaInfo(upperName, lowerName);
        const fullGuaName = guaInfo.name || `${upperName}上${lowerName}下`;
        const guaSeq = hasJson ? GuaJson.hexagramValuesToSeq(hexagram) : 0;
        
        // 找出变爻
        const changingYaos = [];
        hexagram.forEach((yao, index) => {
            if (yao === 6 || yao === 9) { // 老阴或老阳为变爻
                changingYaos.push(index + 1);
            }
        });
        
        return {
            lowerTrigram: lowerName,
            upperTrigram: upperName,
            fullName: fullGuaName,
            changingYaos: changingYaos,
            hexagramValues: hexagram,
            guaInfo: guaInfo,
            seq: guaSeq,
            symbol: guaInfo.symbol || ''
        };
    }

    /**
     * 获取爻的Unicode符号
     * @param {number} yaoValue - 爻值
     * @param {boolean} isChanging - 是否为变爻
     * @returns {string} Unicode符号
     */
    getYaoSymbol(yaoValue, isChanging = false) {
        if (yaoValue % 2 === 1) { // 阳爻
            return isChanging ? '━━━━━━ ○' : '━━━━━━';
        } else { // 阴爻
            return isChanging ? '━━  ━━ ×' : '━━  ━━';
        }
    }

    /**
     * 获取爻的详细含义
     * @param {number} position - 爻位（1-6）
     * @param {number} value - 爻值（6,7,8,9）
     * @returns {string} 爻的含义说明
     */
    getYaoMeaning(position, value) {
        const positions = {
            1: "初爻（地位）",
            2: "二爻（人位）", 
            3: "三爻（天位）",
            4: "四爻（地位）",
            5: "五爻（君位）",
            6: "上爻（天位）"
        };
        
        const posName = positions[position] || `第${position}爻`;
        
        switch (value) {
            case 9:
                return `${posName}：老阳，变爻。刚强过度，宜谦逊。`;
            case 8:
                return `${posName}：少阴，静爻。柔顺得中，吉。`;
            case 7:
                return `${posName}：少阳，静爻。刚正得位，利。`;
            case 6:
                return `${posName}：老阴，变爻。柔弱过度，当变刚。`;
            default:
                return `${posName}：未知爻象`;
        }
    }

    /**
     * 生成占卜建议
     * @param {Object} analysis - 卦象分析结果
     * @returns {string} 占卜建议
     */
    generateAdvice(analysis) {
        const { changingYaos, guaInfo } = analysis;
        let advice = "";
        
        if (changingYaos.length === 0) {
            advice = "此卦无变爻，表示当前状态相对稳定，可按既定方向发展。建议保持现状，稳中求进。";
        } else if (changingYaos.length === 1) {
            advice = `此卦有一个变爻在第${changingYaos[0]}位，表示事态发展有关键转折。建议特别关注这个方面的变化。`;
        } else if (changingYaos.length <= 3) {
            advice = `此卦有${changingYaos.length}个变爻，表示事态变化较为复杂。建议谨慎行事，多方考虑。`;
        } else {
            advice = "此卦变爻较多，表示形势变化很大。建议暂缓行动，等待时机。";
        }
        
        // 添加基于卦象的通用建议
        if (guaInfo.judgment) {
            advice += `\n\n根据卦象特点：${guaInfo.judgment}`;
        }
        
        return advice;
    }

    /**
     * 休眠函数，用于添加延迟
     * @param {number} ms - 毫秒数
     * @returns {Promise}
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 模拟蓍草分筮动画数据
     * @param {number} sticks - 蓍草数量
     * @returns {string} 蓍草显示字符串
     */
    generateYarrowDisplay(sticks) {
        const sticksPerLine = 10;
        const lines = Math.ceil(sticks / sticksPerLine);
        let display = '';
        
        for (let i = 0; i < lines; i++) {
            const sticksInLine = Math.min(sticksPerLine, sticks - i * sticksPerLine);
            display += '|'.repeat(sticksInLine);
            if (i < lines - 1) display += '\n';
        }
        
        return display;
    }
}

// 导出类以供其他文件使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DaYanShiFa;
}

// 全局实例
const daYanShiFa = new DaYanShiFa();