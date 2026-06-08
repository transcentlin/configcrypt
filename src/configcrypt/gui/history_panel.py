"""
KeyVault 操作历史面板

显示加密/解密操作历史记录的UI组件
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QMessageBox,
)

from configcrypt.gui.history import HistoryManager


class HistoryPanel(QWidget):
    """
    操作历史面板
    
    显示加密/解密操作的历史记录
    
    Signals:
        file_selected(Path): 当用户双击历史项时发出信号
    """
    
    file_selected = Signal(Path)
    
    def __init__(self, history_manager: HistoryManager, parent: Optional[QWidget] = None):
        """
        初始化历史面板
        
        Args:
            history_manager: 共享的历史管理器实例
            parent: 父widget
        """
        super().__init__(parent)
        self.history_manager = history_manager
        self._setup_ui()
        self._load_history()
    
    def _setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 15, 80, 20)  # 左右增加边距，与上面拖拽区对齐
        layout.setSpacing(10)
        
        # 标题和按钮在同一行
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📋 操作历史")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # 刷新按钮（小按钮）
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.setToolTip("刷新")
        self.refresh_button.clicked.connect(self._load_history)
        
        # 清除历史按钮（小按钮）
        self.clear_button = QPushButton("🗑️")
        self.clear_button.setFixedSize(32, 32)
        self.clear_button.setToolTip("清除历史")
        self.clear_button.clicked.connect(self._on_clear_history)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #8a8a8a;")
        
        header_layout.addWidget(title_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.clear_button)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        
        # 历史记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "时间", "操作", "文件", "输出", "状态"
        ])
        
        # 设置表格属性
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        # 设置列宽 - 允许用户拖拽调整
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # 时间 - 可调整
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # 操作 - 可调整
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # 文件 - 可调整
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # 输出 - 可调整
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # 状态 - 可调整
        
        # 设置默认列宽
        self.table.setColumnWidth(0, 150)  # 时间
        self.table.setColumnWidth(1, 100)  # 操作
        self.table.setColumnWidth(2, 250)  # 文件
        self.table.setColumnWidth(3, 250)  # 输出
        self.table.setColumnWidth(4, 80)   # 状态
        
        # 双击事件
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # 添加到主布局
        layout.addLayout(header_layout)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
        # 设置样式
        self._setup_style()
    
    def _setup_style(self):
        """设置组件样式 - 黑底暗金色高级风格"""
        self.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                color: #d4af37;
            }
            
            QLabel {
                color: #d4af37;
                background: transparent;
            }
            
            QTableWidget {
                background-color: #1a1a1a;
                border: 1px solid #d4af37;
                border-radius: 6px;
                gridline-color: #2a2a2a;
                color: #d4af37;
                selection-background-color: #2a2a2a;
                selection-color: #f0c14b;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a2a;
            }
            
            QTableWidget::item:selected {
                background-color: #2a2a2a;
                color: #f0c14b;
            }
            
            QTableWidget::item:hover {
                background-color: #252525;
            }
            
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                color: #d4af37;
                padding: 8px;
                border: 1px solid #3a3a3a;
                border-bottom: 2px solid #d4af37;
                font-weight: bold;
                font-size: 13px;
            }
            
            QHeaderView::section:hover {
                background-color: #2a2a2a;
                color: #f0c14b;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: #d4af37;
                border: 2px solid #d4af37;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 2px solid #f0c14b;
                color: #f0c14b;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 2px solid #b8941e;
                color: #b8941e;
            }
        """)
    
    def _load_history(self):
        """加载并显示历史记录"""
        # 强制从文件重新加载历史记录
        self.history_manager._load_history()
        
        # 获取历史记录
        records = self.history_manager.get_records(limit=100)
        
        # 更新统计信息
        stats = self.history_manager.get_stats()
        self.stats_label.setText(
            f"总计: {stats['total']} | "
            f"加密: {stats['encrypt']} | "
            f"解密: {stats['decrypt']} | "
            f"成功: {stats['success']} | "
            f"失败: {stats['failed']}"
        )
        
        # 清空表格
        self.table.setRowCount(0)
        
        # 填充数据
        for record in records:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # 时间
            time_item = QTableWidgetItem(record['timestamp'])
            self.table.setItem(row_position, 0, time_item)
            
            # 操作类型
            operation = "🔒 加密" if record['operation'] == 'encrypt' else "🔓 解密"
            operation_item = QTableWidgetItem(operation)
            self.table.setItem(row_position, 1, operation_item)
            
            # 源文件（只显示文件名）
            source_file = Path(record['source_file']).name
            source_item = QTableWidgetItem(source_file)
            source_item.setToolTip(record['source_file'])  # 完整路径作为提示
            self.table.setItem(row_position, 2, source_item)
            
            # 输出文件（只显示文件名）
            output_file = Path(record['output_file']).name
            output_item = QTableWidgetItem(output_file)
            output_item.setToolTip(record['output_file'])  # 完整路径作为提示
            self.table.setItem(row_position, 3, output_item)
            
            # 状态
            status = "✓ 成功" if record['status'] == 'success' else "✗ 失败"
            status_item = QTableWidgetItem(status)
            
            # 设置状态颜色（暗金色系）
            if record['status'] == 'success':
                status_item.setForeground(QColor(180, 148, 30))  # 暗金色 #b8941e
            else:
                status_item.setForeground(QColor(180, 100, 100))  # 暗红色
                # 如果有错误消息，添加到提示
                if 'error_message' in record:
                    status_item.setToolTip(record['error_message'])
            
            self.table.setItem(row_position, 4, status_item)
    
    def _on_clear_history(self):
        """清除历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清除",
            "确定要清除所有历史记录吗？\n此操作无法撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.history_manager.clear_history()
            self._load_history()
            QMessageBox.information(
                self,
                "清除成功",
                "历史记录已清除"
            )
    
    def _on_row_double_clicked(self, row: int, column: int):
        """
        处理行双击事件
        
        双击历史记录，发出文件选择信号（可用于快速重新操作）
        
        Args:
            row: 行索引
            column: 列索引
        """
        # 获取源文件路径
        source_item = self.table.item(row, 2)
        if source_item:
            # 从tooltip获取完整路径
            file_path = source_item.toolTip()
            if file_path:
                self.file_selected.emit(Path(file_path))
    
    def add_record(
        self,
        operation: str,
        source_file: Path,
        output_file: Path,
        status: str = 'success',
        error_message: Optional[str] = None
    ):
        """
        添加操作记录并刷新显示
        
        Args:
            operation: 操作类型 ('encrypt' 或 'decrypt')
            source_file: 源文件路径
            output_file: 输出文件路径
            status: 状态 ('success' 或 'failed')
            error_message: 错误消息（如果失败）
        """
        self.history_manager.add_record(
            operation=operation,
            source_file=str(source_file),
            output_file=str(output_file),
            status=status,
            error_message=error_message
        )
        self._load_history()
