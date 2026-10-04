#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法数据导出工具
支持多种格式的数据导出和报告生成
"""

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import base64
import io

from config import config
from logger import get_logger
from i18n import i18n_manager, _


class DataExporter:
    """数据导出器"""
    
    def __init__(self):
        self.logger = get_logger("data_exporter")
        self.export_dir = Path(__file__).parent / "exports"
        self.export_dir.mkdir(exist_ok=True)
    
    def export_divination_report(self,
                               question: str,
                               hexagram: List[int],
                               analysis: Dict[str, Any],
                               processes: List[List[int]],
                               duration: float,
                               format_type: str = "html",
                               include_process: bool = True) -> str:
        """
        导出单次占卜的详细报告
        
        Args:
            question: 占卜问题
            hexagram: 卦象
            analysis: 分析结果
            processes: 占卜过程
            duration: 耗时
            format_type: 导出格式 (html, pdf, json, xml)
            include_process: 是否包含详细过程
        
        Returns:
            导出文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"divination_report_{timestamp}.{format_type}"
        output_path = self.export_dir / filename
        
        report_data = {
            "metadata": {
                "title": _("divination_complete"),
                "question": question,
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "format": format_type
            },
            "hexagram": hexagram,
            "analysis": analysis,
            "processes": processes if include_process else None
        }
        
        try:
            if format_type.lower() == "html":
                self._export_html_report(report_data, output_path)
            elif format_type.lower() == "json":
                self._export_json_report(report_data, output_path)
            elif format_type.lower() == "xml":
                self._export_xml_report(report_data, output_path)
            elif format_type.lower() == "pdf":
                self._export_pdf_report(report_data, output_path)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            self.logger.info(f"占卜报告导出完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"导出占卜报告失败: {e}", exc_info=True)
            raise
    
    def _export_html_report(self, data: Dict[str, Any], output_path: Path):
        """导出HTML格式报告"""
        metadata = data["metadata"]
        hexagram = data["hexagram"]
        analysis = data["analysis"]
        processes = data.get("processes")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="{i18n_manager.current_language[:2]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata['title']}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'Arial', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #daa520;
        }}
        .title {{
            color: #daa520;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
        .metadata {{
            background: rgba(218, 165, 32, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}
        .hexagram-display {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
        }}
        .yao-line {{
            font-size: 1.5em;
            margin: 8px 0;
            font-family: monospace;
        }}
        .analysis-section {{
            margin: 25px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }}
        .section-title {{
            color: #daa520;
            font-size: 1.3em;
            margin-bottom: 15px;
            border-bottom: 1px solid #daa520;
            padding-bottom: 5px;
        }}
        .process-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .process-table th, .process-table td {{
            border: 1px solid #daa520;
            padding: 8px;
            text-align: center;
        }}
        .process-table th {{
            background: rgba(218, 165, 32, 0.3);
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #daa520;
            color: #ccc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{metadata['title']}</h1>
        </div>
        
        <div class="metadata">
            <p><strong>{_('question_prompt')}</strong> {metadata['question'] or _('no_question')}</p>
            <p><strong>{_('timestamp')}:</strong> {datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>{_('duration')}:</strong> {metadata['duration']:.3f} {_('seconds')}</p>
        </div>
        
        <div class="analysis-section">
            <div class="section-title">{_('hexagram_display')}</div>
            <div class="hexagram-display">
                {self._generate_hexagram_html(hexagram)}
            </div>
        </div>
        
        <div class="analysis-section">
            <div class="section-title">{_('hexagram_analysis')}</div>
            <p><strong>{_('hexagram_structure')}</strong></p>
            <p>{_('upper_trigram', analysis.get('upper_trigram', ''), '')}</p>
            <p>{_('lower_trigram', analysis.get('lower_trigram', ''), '')}</p>
            <p><strong>{_('full_hexagram_name', analysis.get('full_name', ''))}</strong></p>
            
            {self._generate_gua_info_html(analysis.get('gua_info', {}))}
            
            {self._generate_changing_yaos_html(analysis.get('changing_yaos', []))}
        </div>
        
        {self._generate_process_html(processes) if processes else ''}
        
        <div class="footer">
            <p>{_('disclaimer')}</p>
            <p>{_('suggestion')}</p>
            <p><em>{_('generated_at')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_hexagram_html(self, hexagram: List[int]) -> str:
        """生成卦象的HTML显示"""
        yao_symbols = {
            6: "━━━  ━━━ ✕",  # 老阴
            7: "━━━━━━━",      # 少阳
            8: "━━━  ━━━",      # 少阴
            9: "━━━━━━━ ○"      # 老阳
        }
        
        html = ""
        for i in range(5, -1, -1):  # 从上到下显示
            yao = hexagram[i]
            symbol = yao_symbols.get(yao, "━━━━━━━")
            color = "🔴" if yao in [6, 9] else ("🟡" if yao % 2 == 1 else "🔵")
            html += f'<div class="yao-line">{_("position_" + str(i+1))}: {symbol} {color}</div>\n'
        
        return html
    
    def _generate_gua_info_html(self, gua_info: Dict[str, Any]) -> str:
        """生成卦象信息的HTML"""
        html = ""
        if gua_info.get('number'):
            html += f"<p><strong>{_('hexagram_number', gua_info['number'])}</strong></p>\n"
        if gua_info.get('gua_ci'):
            html += f"<p><strong>{_('hexagram_text', gua_info['gua_ci'])}</strong></p>\n"
        if gua_info.get('judgment'):
            html += f"<p><strong>{_('judgment', gua_info['judgment'])}</strong></p>\n"
        if gua_info.get('image'):
            html += f"<p><strong>{_('image', gua_info['image'])}</strong></p>\n"
        return html
    
    def _generate_changing_yaos_html(self, changing_yaos: List[int]) -> str:
        """生成变爻信息的HTML"""
        if changing_yaos:
            yaos_str = "、".join(map(str, changing_yaos))
            return f"""
            <p><strong>{_('changing_yaos', yaos_str)}</strong></p>
            <p>{_('changing_hint')}</p>
            """
        else:
            return f"<p><strong>{_('static_hexagram')}</strong></p>"
    
    def _generate_process_html(self, processes: List[List[int]]) -> str:
        """生成占卜过程的HTML"""
        if not processes:
            return ""
        
        html = f"""
        <div class="analysis-section">
            <div class="section-title">{_('divination_process')}</div>
            <table class="process-table">
                <thead>
                    <tr>
                        <th>{_('yao_number')}</th>
                        <th>{_('first_change')}</th>
                        <th>{_('second_change')}</th>
                        <th>{_('third_change')}</th>
                        <th>{_('total_taken')}</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, process in enumerate(processes):
            total_taken = sum(process)
            html += f"""
                    <tr>
                        <td>{i + 1}</td>
                        <td>{process[0]}</td>
                        <td>{process[1]}</td>
                        <td>{process[2]}</td>
                        <td>{total_taken}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def _export_json_report(self, data: Dict[str, Any], output_path: Path):
        """导出JSON格式报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_xml_report(self, data: Dict[str, Any], output_path: Path):
        """导出XML格式报告"""
        root = ET.Element("divination_report")
        
        # 元数据
        metadata_elem = ET.SubElement(root, "metadata")
        for key, value in data["metadata"].items():
            elem = ET.SubElement(metadata_elem, key)
            elem.text = str(value)
        
        # 卦象
        hexagram_elem = ET.SubElement(root, "hexagram")
        for i, yao in enumerate(data["hexagram"]):
            yao_elem = ET.SubElement(hexagram_elem, "yao")
            yao_elem.set("position", str(i + 1))
            yao_elem.text = str(yao)
        
        # 分析结果
        analysis_elem = ET.SubElement(root, "analysis")
        for key, value in data["analysis"].items():
            elem = ET.SubElement(analysis_elem, key)
            if isinstance(value, dict):
                elem.text = json.dumps(value, ensure_ascii=False)
            else:
                elem.text = str(value)
        
        # 过程（如果包含）
        if data.get("processes"):
            processes_elem = ET.SubElement(root, "processes")
            for i, process in enumerate(data["processes"]):
                process_elem = ET.SubElement(processes_elem, "yao_process")
                process_elem.set("yao_number", str(i + 1))
                for j, change in enumerate(process):
                    change_elem = ET.SubElement(process_elem, "change")
                    change_elem.set("number", str(j + 1))
                    change_elem.text = str(change)
        
        # 写入文件
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def _export_pdf_report(self, data: Dict[str, Any], output_path: Path):
        """导出PDF格式报告（需要额外依赖）"""
        try:
            # 这里可以集成reportlab或weasyprint等PDF生成库
            # 暂时生成一个简单的文本版本
            self._export_text_report(data, output_path.with_suffix('.txt'))
            self.logger.warning("PDF导出功能需要额外依赖，已生成文本版本")
        except Exception as e:
            self.logger.error(f"PDF导出失败: {e}")
            raise
    
    def _export_text_report(self, data: Dict[str, Any], output_path: Path):
        """导出纯文本格式报告"""
        metadata = data["metadata"]
        hexagram = data["hexagram"]
        analysis = data["analysis"]
        processes = data.get("processes")
        
        content = []
        content.append(f"{metadata['title']}")
        content.append("=" * 50)
        content.append("")
        
        # 基本信息
        content.append(f"{_('question_prompt')} {metadata['question'] or _('no_question')}")
        content.append(f"{_('timestamp')}: {datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"{_('duration')}: {metadata['duration']:.3f}秒")
        content.append("")
        
        # 卦象显示
        content.append(_('hexagram_display'))
        content.append("-" * 30)
        yao_symbols = {6: "━━━  ━━━ ✕", 7: "━━━━━━━", 8: "━━━  ━━━", 9: "━━━━━━━ ○"}
        for i in range(5, -1, -1):
            yao = hexagram[i]
            symbol = yao_symbols.get(yao, "━━━━━━━")
            content.append(f"{_('position_' + str(i+1))}: {symbol}")
        content.append("")
        
        # 分析结果
        content.append(_('hexagram_analysis'))
        content.append("-" * 30)
        content.append(f"{_('upper_trigram', analysis.get('upper_trigram', ''), '')}")
        content.append(f"{_('lower_trigram', analysis.get('lower_trigram', ''), '')}")
        content.append(f"{_('full_hexagram_name', analysis.get('full_name', ''))}")
        
        gua_info = analysis.get('gua_info', {})
        if gua_info.get('gua_ci'):
            content.append(f"{_('hexagram_text', gua_info['gua_ci'])}")
        
        # 变爻信息
        changing_yaos = analysis.get('changing_yaos', [])
        if changing_yaos:
            yaos_str = "、".join(map(str, changing_yaos))
            content.append(f"{_('changing_yaos', yaos_str)}")
            content.append(_('changing_hint'))
        else:
            content.append(_('static_hexagram'))
        
        content.append("")
        content.append(_('disclaimer'))
        content.append(_('suggestion'))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
    
    def export_statistics_report(self,
                               statistics: Dict[str, Any],
                               format_type: str = "html") -> str:
        """
        导出统计报告
        
        Args:
            statistics: 统计数据
            format_type: 导出格式
        
        Returns:
            导出文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"statistics_report_{timestamp}.{format_type}"
        output_path = self.export_dir / filename
        
        try:
            if format_type.lower() == "html":
                self._export_statistics_html(statistics, output_path)
            elif format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(statistics, f, ensure_ascii=False, indent=2, default=str)
            else:
                raise ValueError(f"不支持的统计报告格式: {format_type}")
            
            self.logger.info(f"统计报告导出完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"导出统计报告失败: {e}", exc_info=True)
            raise
    
    def _export_statistics_html(self, statistics: Dict[str, Any], output_path: Path):
        """导出HTML格式统计报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="{i18n_manager.current_language[:2]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_('statistics')}</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'Arial', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: #daa520;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(218, 165, 32, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #daa520;
        }}
        .chart-container {{
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{_('statistics')}</h1>
            <p>{_('generated_at')} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{statistics.get('total_divinations', 0)}</div>
                <div>{_('total_divinations_label')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{statistics.get('average_duration', 0):.3f}s</div>
                <div>{_('average_duration_label')}</div>
            </div>
        </div>
        
        {self._generate_popular_hexagrams_html(statistics.get('popular_hexagrams', []))}
        
        {self._generate_daily_stats_html(statistics.get('daily_statistics', []))}
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_popular_hexagrams_html(self, popular_hexagrams: List[Dict[str, Any]]) -> str:
        """生成热门卦象HTML"""
        if not popular_hexagrams:
            return ""
        
        html = f"""
        <div class="chart-container">
            <h3>{_('popular_hexagrams')}</h3>
            <ul>
        """
        
        for hexagram in popular_hexagrams:
            html += f"<li>{hexagram['name']}: {hexagram['count']} 次</li>\n"
        
        html += """
            </ul>
        </div>
        """
        
        return html
    
    def _generate_daily_stats_html(self, daily_stats: List[Dict[str, Any]]) -> str:
        """生成每日统计HTML"""
        if not daily_stats:
            return ""
        
        html = f"""
        <div class="chart-container">
            <h3>{_('recent_activity')}</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid #daa520;">
                        <th style="padding: 10px; text-align: left;">{_('date')}</th>
                        <th style="padding: 10px; text-align: right;">{_('count')}</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for stat in daily_stats[:10]:  # 只显示最近10天
            html += f"""
                    <tr>
                        <td style="padding: 8px;">{stat['date']}</td>
                        <td style="padding: 8px; text-align: right;">{stat['count']}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html


# 全局导出工具实例
data_exporter = DataExporter()

# 便捷函数
def export_divination_report(**kwargs) -> str:
    """导出占卜报告的便捷函数"""
    return data_exporter.export_divination_report(**kwargs)

def export_statistics_report(**kwargs) -> str:
    """导出统计报告的便捷函数"""
    return data_exporter.export_statistics_report(**kwargs)