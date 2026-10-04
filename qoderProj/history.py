#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大衍筮法历史记录管理模块
提供占卜历史的存储、查询、导出等功能
"""

import json
import csv
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET

from config import config
from logger import get_logger


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化历史记录管理器
        
        Args:
            db_path: 数据库文件路径，默认为项目目录下的history.db
        """
        self.logger = get_logger("history")
        
        # 确定数据库路径
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "history.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # 初始化数据库
        self._init_database()
        
        self.logger.info(f"历史记录管理器初始化完成，数据库路径: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建占卜历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS divination_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    question TEXT,
                    hexagram TEXT NOT NULL,
                    analysis TEXT NOT NULL,
                    duration REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    tags TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_date DATE NOT NULL,
                    total_divinations INTEGER DEFAULT 0,
                    most_frequent_hexagram TEXT,
                    average_duration REAL,
                    unique_users INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建用户配置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    language TEXT DEFAULT 'zh_CN',
                    theme TEXT DEFAULT 'traditional',
                    show_process BOOLEAN DEFAULT 1,
                    auto_save BOOLEAN DEFAULT 1,
                    export_format TEXT DEFAULT 'json',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self.logger.debug("数据库表创建/检查完成")
    
    def save_divination(self, 
                       question: str,
                       hexagram: List[int],
                       analysis: Dict[str, Any],
                       duration: float,
                       user_id: str = "default",
                       tags: List[str] = None,
                       notes: str = "") -> str:
        """
        保存占卜记录
        
        Args:
            question: 占卜问题
            hexagram: 卦象数组
            analysis: 分析结果
            duration: 占卜耗时
            user_id: 用户ID
            tags: 标签列表
            notes: 备注
        
        Returns:
            session_id: 会话ID
        """
        # 生成唯一会话ID
        session_id = self._generate_session_id(question, hexagram, datetime.now())
        
        # 序列化数据
        hexagram_json = json.dumps(hexagram)
        analysis_json = json.dumps(analysis, ensure_ascii=False, default=str)
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO divination_history 
                    (session_id, question, hexagram, analysis, duration, user_id, tags, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, question, hexagram_json, analysis_json, 
                     duration, user_id, tags_json, notes))
                
                conn.commit()
                
                self.logger.info(f"占卜记录已保存: {session_id}")
                return session_id
                
        except Exception as e:
            self.logger.error(f"保存占卜记录失败: {e}", exc_info=True)
            raise
    
    def get_history(self,
                   user_id: str = "default",
                   limit: int = 50,
                   offset: int = 0,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取历史记录
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            offset: 偏移量
            start_date: 开始日期
            end_date: 结束日期
            search_query: 搜索关键词
        
        Returns:
            历史记录列表
        """
        query = '''
            SELECT id, session_id, question, hexagram, analysis, duration,
                   timestamp, user_id, tags, notes, created_at, updated_at
            FROM divination_history
            WHERE user_id = ?
        '''
        params = [user_id]
        
        # 添加日期范围过滤
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date.isoformat())
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date.isoformat())
        
        # 添加搜索过滤
        if search_query:
            query += ' AND (question LIKE ? OR notes LIKE ?)'
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern, search_pattern])
        
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                records = []
                for row in cursor.fetchall():
                    record = dict(row)
                    # 反序列化JSON数据
                    record['hexagram'] = json.loads(record['hexagram'])
                    record['analysis'] = json.loads(record['analysis'])
                    record['tags'] = json.loads(record['tags'])
                    records.append(record)
                
                self.logger.debug(f"获取历史记录: {len(records)} 条")
                return records
                
        except Exception as e:
            self.logger.error(f"获取历史记录失败: {e}", exc_info=True)
            return []
    
    def get_statistics(self, 
                      user_id: str = "default",
                      days: int = 30) -> Dict[str, Any]:
        """
        获取统计信息
        
        Args:
            user_id: 用户ID
            days: 统计天数
        
        Returns:
            统计信息字典
        """
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总占卜次数
                cursor.execute('''
                    SELECT COUNT(*) FROM divination_history
                    WHERE user_id = ? AND timestamp >= ?
                ''', (user_id, start_date.isoformat()))
                total_count = cursor.fetchone()[0]
                
                # 平均耗时
                cursor.execute('''
                    SELECT AVG(duration) FROM divination_history
                    WHERE user_id = ? AND timestamp >= ? AND duration IS NOT NULL
                ''', (user_id, start_date.isoformat()))
                avg_duration = cursor.fetchone()[0] or 0
                
                # 最常见的卦象
                cursor.execute('''
                    SELECT analysis, COUNT(*) as count FROM divination_history
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY analysis ORDER BY count DESC LIMIT 5
                ''', (user_id, start_date.isoformat()))
                
                popular_hexagrams = []
                for row in cursor.fetchall():
                    try:
                        analysis = json.loads(row[0])
                        popular_hexagrams.append({
                            'name': analysis.get('full_name', '未知'),
                            'count': row[1]
                        })
                    except:
                        continue
                
                # 按日期统计
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM divination_history
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                ''', (user_id, start_date.isoformat()))
                
                daily_stats = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
                
                return {
                    'total_divinations': total_count,
                    'average_duration': round(avg_duration, 3),
                    'popular_hexagrams': popular_hexagrams,
                    'daily_statistics': daily_stats,
                    'period_days': days,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}", exc_info=True)
            return {}
    
    def export_history(self,
                      format_type: str = "json",
                      user_id: str = "default",
                      output_path: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> str:
        """
        导出历史记录
        
        Args:
            format_type: 导出格式 (json, csv, xml)
            user_id: 用户ID
            output_path: 输出文件路径
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            输出文件路径
        """
        # 获取历史记录
        records = self.get_history(
            user_id=user_id,
            limit=10000,  # 导出时不限制数量
            start_date=start_date,
            end_date=end_date
        )
        
        # 确定输出路径
        if output_path is None:
            export_dir = Path(__file__).parent / "exports"
            export_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = export_dir / f"divination_history_{timestamp}.{format_type}"
        
        output_path = Path(output_path)
        
        try:
            if format_type.lower() == "json":
                self._export_json(records, output_path)
            elif format_type.lower() == "csv":
                self._export_csv(records, output_path)
            elif format_type.lower() == "xml":
                self._export_xml(records, output_path)
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
            
            self.logger.info(f"历史记录导出完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"导出历史记录失败: {e}", exc_info=True)
            raise
    
    def _export_json(self, records: List[Dict[str, Any]], output_path: Path):
        """导出为JSON格式"""
        export_data = {
            'export_info': {
                'format': 'json',
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'total_records': len(records)
            },
            'records': records
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_csv(self, records: List[Dict[str, Any]], output_path: Path):
        """导出为CSV格式"""
        if not records:
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'session_id', 'question', 'hexagram_name', 'changing_yaos',
                'duration', 'timestamp', 'tags', 'notes'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                writer.writerow({
                    'session_id': record['session_id'],
                    'question': record['question'],
                    'hexagram_name': record['analysis'].get('full_name', ''),
                    'changing_yaos': ','.join(map(str, record['analysis'].get('changing_yaos', []))),
                    'duration': record['duration'],
                    'timestamp': record['timestamp'],
                    'tags': ','.join(record['tags']),
                    'notes': record['notes']
                })
    
    def _export_xml(self, records: List[Dict[str, Any]], output_path: Path):
        """导出为XML格式"""
        root = ET.Element("divination_history")
        
        # 添加导出信息
        export_info = ET.SubElement(root, "export_info")
        ET.SubElement(export_info, "format").text = "xml"
        ET.SubElement(export_info, "version").text = "1.0"
        ET.SubElement(export_info, "exported_at").text = datetime.now().isoformat()
        ET.SubElement(export_info, "total_records").text = str(len(records))
        
        # 添加记录
        records_elem = ET.SubElement(root, "records")
        for record in records:
            record_elem = ET.SubElement(records_elem, "record")
            
            for key, value in record.items():
                if key in ['hexagram', 'analysis', 'tags']:
                    # 复杂对象转为JSON字符串
                    elem = ET.SubElement(record_elem, key)
                    elem.text = json.dumps(value, ensure_ascii=False)
                else:
                    elem = ET.SubElement(record_elem, key)
                    elem.text = str(value) if value is not None else ""
        
        # 写入文件
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def delete_record(self, session_id: str, user_id: str = "default") -> bool:
        """
        删除指定记录
        
        Args:
            session_id: 会话ID
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM divination_history
                    WHERE session_id = ? AND user_id = ?
                ''', (session_id, user_id))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    self.logger.info(f"删除记录成功: {session_id}")
                    return True
                else:
                    self.logger.warning(f"未找到要删除的记录: {session_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"删除记录失败: {e}", exc_info=True)
            return False
    
    def clear_history(self, 
                     user_id: str = "default",
                     days_to_keep: Optional[int] = None) -> int:
        """
        清理历史记录
        
        Args:
            user_id: 用户ID
            days_to_keep: 保留天数，None表示清空所有
        
        Returns:
            删除的记录数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if days_to_keep is None:
                    # 清空所有记录
                    cursor.execute('DELETE FROM divination_history WHERE user_id = ?', (user_id,))
                else:
                    # 保留指定天数内的记录
                    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
                    cursor.execute('''
                        DELETE FROM divination_history
                        WHERE user_id = ? AND timestamp < ?
                    ''', (user_id, cutoff_date.isoformat()))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                self.logger.info(f"清理历史记录完成: 删除 {deleted_count} 条记录")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"清理历史记录失败: {e}", exc_info=True)
            return 0
    
    def _generate_session_id(self, question: str, hexagram: List[int], timestamp: datetime) -> str:
        """生成唯一会话ID"""
        content = f"{question}:{hexagram}:{timestamp.isoformat()}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]


# 全局历史管理器实例
history_manager = HistoryManager()

# 便捷函数
def save_divination_history(question: str, hexagram: List[int], analysis: Dict[str, Any], 
                           duration: float, **kwargs) -> str:
    """保存占卜历史的便捷函数"""
    return history_manager.save_divination(question, hexagram, analysis, duration, **kwargs)

def get_divination_history(**kwargs) -> List[Dict[str, Any]]:
    """获取占卜历史的便捷函数"""
    return history_manager.get_history(**kwargs)

def export_divination_history(**kwargs) -> str:
    """导出占卜历史的便捷函数"""
    return history_manager.export_history(**kwargs)