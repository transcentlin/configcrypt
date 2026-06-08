"""
KeyVault 操作历史记录模块

管理加密/解密操作的历史记录
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    """操作历史记录管理器"""
    
    # 最大历史记录数
    MAX_RECORDS = 100
    
    def __init__(self, history_file: Optional[Path] = None):
        """
        初始化历史管理器
        
        Args:
            history_file: 历史文件路径，默认为 ~/.keyvault/history.json
        """
        if history_file is None:
            # 默认路径：用户主目录/.keyvault/history.json
            home = Path.home()
            keyvault_dir = home / '.keyvault'
            keyvault_dir.mkdir(exist_ok=True)
            self.history_file = keyvault_dir / 'history.json'
        else:
            self.history_file = Path(history_file)
        
        self._records: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """从文件加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._records = json.load(f)
                # 限制记录数量
                if len(self._records) > self.MAX_RECORDS:
                    self._records = self._records[-self.MAX_RECORDS:]
            except Exception:
                # 如果加载失败，使用空列表
                self._records = []
        else:
            self._records = []
    
    def _save_history(self):
        """保存历史记录到文件"""
        try:
            # 确保目录存在
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 保存失败不应中断程序
            print(f"Warning: Failed to save history: {e}")
    
    def add_record(
        self,
        operation: str,
        source_file: str,
        output_file: str,
        status: str = 'success',
        error_message: Optional[str] = None
    ):
        """
        添加操作记录
        
        Args:
            operation: 操作类型 ('encrypt' 或 'decrypt')
            source_file: 源文件路径
            output_file: 输出文件路径
            status: 状态 ('success' 或 'failed')
            error_message: 错误消息（如果失败）
        """
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'source_file': str(source_file),
            'output_file': str(output_file),
            'status': status,
        }
        
        if error_message:
            record['error_message'] = error_message
        
        self._records.append(record)
        
        # 限制记录数量
        if len(self._records) > self.MAX_RECORDS:
            self._records = self._records[-self.MAX_RECORDS:]
        
        self._save_history()
    
    def get_records(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取历史记录
        
        Args:
            limit: 限制返回记录数，None表示返回所有
            
        Returns:
            历史记录列表（按时间倒序）
        """
        records = list(reversed(self._records))  # 最新的在前
        if limit:
            return records[:limit]
        return records
    
    def clear_history(self):
        """清除所有历史记录"""
        self._records = []
        self._save_history()
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        total = len(self._records)
        encrypt_count = sum(1 for r in self._records if r['operation'] == 'encrypt')
        decrypt_count = sum(1 for r in self._records if r['operation'] == 'decrypt')
        success_count = sum(1 for r in self._records if r['status'] == 'success')
        failed_count = sum(1 for r in self._records if r['status'] == 'failed')
        
        return {
            'total': total,
            'encrypt': encrypt_count,
            'decrypt': decrypt_count,
            'success': success_count,
            'failed': failed_count,
        }
