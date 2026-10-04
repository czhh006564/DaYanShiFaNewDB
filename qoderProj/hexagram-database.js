/**
 * 六十四卦数据库 - JavaScript版本
 * 包含完整的64卦信息和八卦基本数据
 */

// 八卦基本信息
const BAGUA_INFO = {
    "乾": { symbol: "☰", element: "天", attribute: "刚健" },
    "坤": { symbol: "☷", element: "地", attribute: "柔顺" },
    "震": { symbol: "☳", element: "雷", attribute: "动" },
    "巽": { symbol: "☴", element: "风", attribute: "入" },
    "坎": { symbol: "☵", element: "水", attribute: "险" },
    "离": { symbol: "☲", element: "火", attribute: "丽" },
    "艮": { symbol: "☶", element: "山", attribute: "止" },
    "兑": { symbol: "☱", element: "泽", attribute: "悦" }
};

// 完整的六十四卦数据库
const LIUSHISI_GUA_DB = {
    // 乾宫八卦
    "乾-乾": {
        name: "乾为天", number: 1,
        guaCi: "元，亨，利，贞。",
        judgment: "刚健中正，大吉大利。君子以自强不息。",
        image: "天行健，君子以自强不息。"
    },
    "乾-巽": {
        name: "天风姤", number: 44,
        guaCi: "女壮，勿用取女。",
        judgment: "阴长阳消，需要谨慎。",
        image: "天下有风，姤；后以施命诰四方。"
    },
    "乾-离": {
        name: "天火同人", number: 13,
        guaCi: "同人于野，亨。利涉大川，利君子贞。",
        judgment: "同心协力，和谐共处。",
        image: "天与火，同人；君子以类族辨物。"
    },
    "乾-兑": {
        name: "天泽履", number: 10,
        guaCi: "履虎尾，不咥人，亨。",
        judgment: "慎行谨言，可获成功。",
        image: "上天下泽，履；君子以辨上下，定民志。"
    },
    "乾-坤": {
        name: "天地否", number: 12,
        guaCi: "否之匪人，不利君子贞，大往小来。",
        judgment: "天地不交，万物不通。",
        image: "天地不交，否；君子以俭德辟难，不可荣以禄。"
    },
    "乾-艮": {
        name: "天山遁", number: 33,
        guaCi: "亨，小利贞。",
        judgment: "退而求进，明哲保身。",
        image: "天下有山，遁；君子以远小人，不恶而严。"
    },
    "乾-坎": {
        name: "天水讼", number: 6,
        guaCi: "有孚，窒惕，中吉，终凶。利见大人，不利涉大川。",
        judgment: "争讼之象，宜和解。",
        image: "天与水违行，讼；君子以作事谋始。"
    },
    "乾-震": {
        name: "天雷无妄", number: 25,
        guaCi: "元亨，利贞。其匪正有眚，不利有攸往。",
        judgment: "顺应天意，无妄而行。",
        image: "天下雷行，物与无妄；先王以茂对时，育万物。"
    },
    
    // 坤宫八卦
    "坤-坤": {
        name: "坤为地", number: 2,
        guaCi: "元亨，利牝马之贞。君子有攸往，先迷后得主，利。西南得朋，东北丧朋。安贞吉。",
        judgment: "柔顺承载，厚德载物。",
        image: "地势坤，君子以厚德载物。"
    },
    "坤-震": {
        name: "地雷复", number: 24,
        guaCi: "亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。",
        judgment: "一阳来复，生机萌动。",
        image: "雷在地中，复；先王以至日闭关，商旅不行，后不省方。"
    },
    "坤-坎": {
        name: "地水师", number: 7,
        guaCi: "贞，丈人吉，无咎。",
        judgment: "用兵之道，以正制胜。",
        image: "地中有水，师；君子以容民畜众。"
    },
    "坤-艮": {
        name: "地山谦", number: 15,
        guaCi: "亨，君子有终。",
        judgment: "谦逊有礼，必得善终。",
        image: "地中有山，谦；君子以裒多益寡，称物平施。"
    },
    "坤-巽": {
        name: "地风升", number: 46,
        guaCi: "元亨，用见大人，勿恤，南征吉。",
        judgment: "顺势上升，前程远大。",
        image: "地中生木，升；君子以顺德，积小以高大。"
    },
    "坤-离": {
        name: "地火明夷", number: 36,
        guaCi: "利艰贞。",
        judgment: "明珠蒙尘，韬光养晦。",
        image: "明入地中，明夷；君子以莅众，用晦而明。"
    },
    "坤-兑": {
        name: "地泽临", number: 19,
        guaCi: "元亨利贞。至于八月有凶。",
        judgment: "居高临下，恩威并施。",
        image: "泽上有地，临；君子以教思无穷，容保民无疆。"
    },
    "坤-乾": {
        name: "地天泰", number: 11,
        guaCi: "小往大来，吉亨。",
        judgment: "天地交泰，万物通达。",
        image: "天地交，泰；后以财成天地之道，辅相天地之宜，以左右民。"
    },

    // 震宫八卦  
    "震-震": {
        name: "震为雷", number: 51,
        guaCi: "亨。震来虩虩，笑言哑哑。震惊百里，不丧匕鬯。",
        judgment: "雷声震震，警醒众生。",
        image: "洊雷，震；君子以恐惧修省。"
    },
    "震-艮": {
        name: "雷山小过", number: 62,
        guaCi: "亨，利贞，可小事，不可大事。飞鸟遗之音，不宜上宜下，大吉。",
        judgment: "小有过越，宜守不宜进。",
        image: "山上有雷，小过；君子以行过乎恭，丧过乎哀，用过乎俭。"
    },
    "震-坎": {
        name: "雷水解", number: 40,
        guaCi: "利西南，无所往，其来复吉。有攸往，夙吉。",
        judgment: "解除困难，重获新生。",
        image: "雷雨作，解；君子以赦过宥罪。"
    },
    "震-巽": {
        name: "雷风恒", number: 32,
        guaCi: "亨，无咎，利贞，利有攸往。",
        judgment: "恒久不变，持之以恒。",
        image: "雷风，恒；君子以立不易方。"
    },
    "震-坤": {
        name: "雷地豫", number: 16,
        guaCi: "利建侯行师。",
        judgment: "顺应民心，建功立业。",
        image: "雷出地奋，豫；先王以作乐崇德，殷荐之上帝，以配祖考。"
    },
    "震-离": {
        name: "雷火丰", number: 55,
        guaCi: "亨，王假之，勿忧，宜日中。",
        judgment: "丰盛之象，正当盛时。",
        image: "雷电皆至，丰；君子以折狱致刑。"
    },
    "震-兑": {
        name: "雷泽归妹", number: 54,
        guaCi: "征凶，无攸利。",
        judgment: "归妹之象，当慎行事。",
        image: "泽上有雷，归妹；君子以永终知敝。"
    },
    "震-乾": {
        name: "雷天大壮", number: 34,
        guaCi: "利贞。",
        judgment: "阳气盛大，势不可挡。",
        image: "雷在天上，大壮；君子以非礼勿履。"
    },

    // 巽宫八卦
    "巽-巽": {
        name: "巽为风", number: 57,
        guaCi: "小亨，利有攸往，利见大人。",
        judgment: "顺风而行，渐进有功。",
        image: "随风，巽；君子以申命行事。"
    },
    "巽-艮": {
        name: "风山渐", number: 53,
        guaCi: "女归吉，利贞。",
        judgment: "循序渐进，稳步发展。",
        image: "山上有木，渐；君子以居贤德善俗。"
    },
    "巽-坎": {
        name: "风水涣", number: 59,
        guaCi: "亨。王假有庙，利涉大川，利贞。",
        judgment: "离散之象，当聚人心。",
        image: "风行水上，涣；先王以享于帝立庙。"
    },
    "巽-震": {
        name: "风雷益", number: 42,
        guaCi: "利有攸往，利涉大川。",
        judgment: "损上益下，利益众生。",
        image: "风雷，益；君子以见善则迁，有过则改。"
    },
    "巽-坤": {
        name: "风地观", number: 20,
        guaCi: "盥而不荐，有孚颙若。",
        judgment: "观察时势，以德感化。",
        image: "风行地上，观；先王以省方，观民设教。"
    },
    "巽-离": {
        name: "风火家人", number: 37,
        guaCi: "利女贞。",
        judgment: "家庭和睦，内外有别。",
        image: "风自火出，家人；君子以言有物，而行有恒。"
    },
    "巽-兑": {
        name: "风泽中孚", number: 61,
        guaCi: "豚鱼吉，利涉大川，利贞。",
        judgment: "诚信待人，感化万物。",
        image: "泽上有风，中孚；君子以议狱缓死。"
    },
    "巽-乾": {
        name: "风天小畜", number: 9,
        guaCi: "亨。密云不雨，自我西郊。",
        judgment: "小有积蓄，尚待时机。",
        image: "风行天上，小畜；君子以懿文德。"
    },

    // 坎宫八卦
    "坎-坎": {
        name: "坎为水", number: 29,
        guaCi: "习坎，有孚，维心亨，行有尚。",
        judgment: "险中求进，诚信为本。",
        image: "水洊至，习坎；君子以常德行，习教事。"
    },
    "坎-艮": {
        name: "水山蹇", number: 39,
        guaCi: "利西南，不利东北；利见大人，贞吉。",
        judgment: "险阻在前，当择良径。",
        image: "山上有水，蹇；君子以反身修德。"
    },
    "坎-震": {
        name: "水雷屯", number: 3,
        guaCi: "元亨利贞。勿用，有攸往，利建侯。",
        judgment: "草创之初，宜建基业。",
        image: "云雷屯，君子以经纶。"
    },
    "坎-巽": {
        name: "水风井", number: 48,
        guaCi: "改邑不改井，无丧无得，往来井井。汔至，亦未繘井，羸其瓶，凶。",
        judgment: "德泽深远，惠及众生。",
        image: "木上有水，井；君子以劳民劝相。"
    },
    "坎-坤": {
        name: "水地比", number: 8,
        guaCi: "吉。原筮元永贞，无咎。不宁方来，后夫凶。",
        judgment: "亲密团结，互相扶助。",
        image: "地上有水，比；先王以建万国，亲诸侯。"
    },
    "坎-离": {
        name: "水火既济", number: 63,
        guaCi: "亨，小利贞，初吉终乱。",
        judgment: "事已成功，当防盛极而衰。",
        image: "水在火上，既济；君子以思患而豫防之。"
    },
    "坎-兑": {
        name: "水泽节", number: 60,
        guaCi: "亨。苦节不可贞。",
        judgment: "有节制度，适可而止。",
        image: "泽上有水，节；君子以制数度，议德行。"
    },
    "坎-乾": {
        name: "水天需", number: 5,
        guaCi: "有孚，光亨，贞吉。利涉大川。",
        judgment: "需要等待，时机未到。",
        image: "云上于天，需；君子以饮食宴乐。"
    },

    // 离宫八卦
    "离-离": {
        name: "离为火", number: 30,
        guaCi: "利贞，亨。畜牝牛，吉。",
        judgment: "光明正大，文明之象。",
        image: "明两作，离；大人以继明照于四方。"
    },
    "离-艮": {
        name: "火山旅", number: 56,
        guaCi: "小亨，旅贞吉。",
        judgment: "旅行在外，当谨慎行事。",
        image: "山上有火，旅；君子以明慎用刑，而不留狱。"
    },
    "离-震": {
        name: "火雷噬嗑", number: 21,
        guaCi: "亨。利用狱。",
        judgment: "刚柔相济，破除阻碍。",
        image: "雷电噬嗑，君子以明罚敕法。"
    },
    "离-巽": {
        name: "火风鼎", number: 50,
        guaCi: "元吉，亨。",
        judgment: "鼎新革故，建立秩序。",
        image: "木上有火，鼎；君子以正位凝命。"
    },
    "离-坎": {
        name: "火水未济", number: 64,
        guaCi: "亨。小狐汔济，濡其尾，无攸利。",
        judgment: "功业未成，当继续努力。",
        image: "火在水上，未济；君子以慎辨物居方。"
    },
    "离-坤": {
        name: "火地晋", number: 35,
        guaCi: "康侯用锡马蕃庶，昼日三接。",
        judgment: "光明上进，前程似锦。",
        image: "明出地上，晋；君子以自昭明德。"
    },
    "离-兑": {
        name: "火泽睽", number: 38,
        guaCi: "小事吉。",
        judgment: "意见分歧，当求同存异。",
        image: "上火下泽，睽；君子以同而异。"
    },
    "离-乾": {
        name: "火天大有", number: 14,
        guaCi: "元亨。",
        judgment: "大有所获，盛世之象。",
        image: "火在天上，大有；君子以遏恶扬善，顺天休命。"
    },

    // 艮宫八卦
    "艮-艮": {
        name: "艮为山", number: 52,
        guaCi: "艮其背，不获其身，行其庭，不见其人，无咎。",
        judgment: "止于所当止，静以修身。",
        image: "兼山，艮；君子以思不出其位。"
    },
    "艮-震": {
        name: "山雷颐", number: 27,
        guaCi: "贞吉。观颐，自求口实。",
        judgment: "颐养之道，自食其力。",
        image: "山下有雷，颐；君子以慎言语，节饮食。"
    },
    "艮-坎": {
        name: "山水蒙", number: 4,
        guaCi: "亨。匪我求童蒙，童蒙求我。初噬告，再三渎，渎则不告。利贞。",
        judgment: "启发教育，循循善诱。",
        image: "山下出泉，蒙；君子以果行育德。"
    },
    "艮-巽": {
        name: "山风蛊", number: 18,
        guaCi: "元亨，利涉大川。先甲三日，后甲三日。",
        judgment: "拨乱反正，重建秩序。",
        image: "山下有风，蛊；君子以振民育德。"
    },
    "艮-坤": {
        name: "山地剥", number: 23,
        guaCi: "不利有攸往。",
        judgment: "阳气剥落，当守不当攻。",
        image: "山附于地，剥；上以厚下，安宅。"
    },
    "艮-离": {
        name: "山火贲", number: 22,
        guaCi: "亨。小利有攸往。",
        judgment: "文质彬彬，内外兼修。",
        image: "山下有火，贲；君子以明庶政，无敢折狱。"
    },
    "艮-兑": {
        name: "山泽损", number: 41,
        guaCi: "有孚，元吉，无咎，可贞，利有攸往。曷之用，二簋可用享。",
        judgment: "损己利人，诚信为本。",
        image: "山下有泽，损；君子以征忿窒欲。"
    },
    "艮-乾": {
        name: "山天大畜", number: 26,
        guaCi: "利贞，不家食吉，利涉大川。",
        judgment: "大有积蓄，德容载物。",
        image: "天在山中，大畜；君子以多识前言往行，以畜其德。"
    },

    // 兑宫八卦
    "兑-兑": {
        name: "兑为泽", number: 58,
        guaCi: "亨，利贞。",
        judgment: "喜悦和谐，朋友相聚。",
        image: "丽泽，兑；君子以朋友讲习。"
    },
    "兑-震": {
        name: "泽雷随", number: 17,
        guaCi: "元亨利贞，无咎。",
        judgment: "随时变通，顺应大势。",
        image: "泽中有雷，随；君子以向晦入宴息。"
    },
    "兑-坎": {
        name: "泽水困", number: 47,
        guaCi: "亨，贞，大人吉，无咎，有言不信。",
        judgment: "身处困境，当坚守正道。",
        image: "泽无水，困；君子以致命遂志。"
    },
    "兑-巽": {
        name: "泽风大过", number: 28,
        guaCi: "栋桡，利有攸往，亨。",
        judgment: "大过之象，当谨慎行事。",
        image: "泽灭木，大过；君子以独立不惧，遁世无闷。"
    },
    "兑-坤": {
        name: "泽地萃", number: 45,
        guaCi: "亨。王假有庙，利见大人，亨，利贞。用大牲吉，利有攸往。",
        judgment: "聚集众人，共襄盛举。",
        image: "泽上于地，萃；君子以除戎器，戒不虞。"
    },
    "兑-离": {
        name: "泽火革", number: 49,
        guaCi: "巳日乃孚，元亨利贞，悔亡。",
        judgment: "革故鼎新，除旧布新。",
        image: "泽中有火，革；君子以治历明时。"
    },
    "兑-艮": {
        name: "泽山咸", number: 31,
        guaCi: "亨，利贞，取女吉。",
        judgment: "感应相通，心心相印。",
        image: "山上有泽，咸；君子以虚受人。"
    },
    "兑-乾": {
        name: "泽天夬", number: 43,
        guaCi: "扬于王庭，孚号，有厉，告自邑，不利即戎，利有攸往。",
        judgment: "决断之象，当机立断。",
        image: "泽上于天，夬；君子以施禄及下，居德则忌。"
    }
};

// 爻位含义
const YAO_POSITIONS = {
    1: "初爻（地位）",
    2: "二爻（人位）", 
    3: "三爻（天位）",
    4: "四爻（地位）",
    5: "五爻（君位）",
    6: "上爻（天位）"
};

/**
 * 获取卦象信息
 * @param {string} upperGua - 上卦名称
 * @param {string} lowerGua - 下卦名称
 * @returns {Object} 卦象信息
 */
function getGuaInfo(upperGua, lowerGua) {
    const key = `${upperGua}-${lowerGua}`; // 注意顺序：上卦在前，下卦在后
    return LIUSHISI_GUA_DB[key] || {
        name: `${upperGua}${lowerGua}`,
        number: 0,
        guaCi: "卦辞待补充",
        judgment: "此卦信息尚未收录",
        image: "象辞待补充"
    };
}

/**
 * 获取八卦符号
 * @param {string} guaName - 卦名
 * @returns {string} 八卦符号
 */
function getBaguaSymbol(guaName) {
    return BAGUA_INFO[guaName] ? BAGUA_INFO[guaName].symbol : "?";
}

/**
 * 获取八卦属性
 * @param {string} guaName - 卦名
 * @returns {Object} 八卦信息
 */
function getBaguaInfo(guaName) {
    return BAGUA_INFO[guaName] || { symbol: "?", element: "未知", attribute: "未知" };
}

/**
 * 获取爻位名称
 * @param {number} position - 爻位（1-6）
 * @returns {string} 爻位名称
 */
function getYaoPositionName(position) {
    return YAO_POSITIONS[position] || `第${position}爻`;
}

/**
 * 根据卦名搜索相关卦象
 * @param {string} keyword - 搜索关键词
 * @returns {Array} 匹配的卦象列表
 */
function searchGua(keyword) {
    const results = [];
    for (const [key, gua] of Object.entries(LIUSHISI_GUA_DB)) {
        if (gua.name.includes(keyword) || 
            gua.guaCi.includes(keyword) || 
            gua.judgment.includes(keyword)) {
            results.push({ key, ...gua });
        }
    }
    return results;
}

/**
 * 获取所有卦象列表
 * @returns {Array} 全部卦象信息
 */
function getAllGua() {
    return Object.entries(LIUSHISI_GUA_DB).map(([key, gua]) => ({
        key,
        ...gua
    }));
}

// 导出函数供其他文件使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        BAGUA_INFO,
        LIUSHISI_GUA_DB,
        YAO_POSITIONS,
        getGuaInfo,
        getBaguaSymbol,
        getBaguaInfo,
        getYaoPositionName,
        searchGua,
        getAllGua
    };
}