"""
KeyVault GUI 对话框模块

提供各种对话框组件：
- WelcomeWizard: 欢迎向导（首次启动）
- EncryptDialog: 加密文件对话框
- DecryptDialog: 解密文件对话框
- SettingsDialog: 设置对话框
- ProgressDialog: 进度对话框
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread, QPoint
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QBrush, QRadialGradient, QPen, QPolygon
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QWidget,
)

from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.vault import Vault
from configcrypt.utils import calculate_password_strength, PasswordStrength


def create_dialog_icon(size: int = 32) -> QIcon:
    """
    创建对话框锁图标
    
    用于对话框左上角显示的小锁图标
    
    Args:
        size: 图标尺寸，默认32x32
    
    Returns:
        QIcon: 锁图标
    """
    icon = QIcon()
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 绘制圆形背景（黑色渐变）
    gradient = QRadialGradient(size / 2, size / 2, size / 2)
    gradient.setColorAt(0, QColor("#2a2a2a"))
    gradient.setColorAt(1, QColor("#0d0d0d"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, size, size)
    
    # 绘制锁身（暗金色矩形）
    lock_body_height = int(size * 0.35)
    lock_body_width = int(size * 0.4)
    lock_body_x = int((size - lock_body_width) / 2)
    lock_body_y = int(size * 0.5)
    
    painter.setBrush(QBrush(QColor("#d4af37")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(
        lock_body_x,
        lock_body_y,
        lock_body_width,
        lock_body_height,
        size * 0.05,
        size * 0.05
    )
    
    # 绘制锁梁（暗金色圆弧）
    pen = QPen(QColor("#d4af37"))
    pen.setWidth(max(2, int(size * 0.08)))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    
    shackle_width = int(size * 0.25)
    shackle_height = int(size * 0.25)
    shackle_x = int((size - shackle_width) / 2)
    shackle_y = int(size * 0.25)
    
    painter.drawArc(
        shackle_x,
        shackle_y,
        shackle_width,
        shackle_height,
        0 * 16,  # 起始角度（0度）
        180 * 16  # 扫描角度（180度）
    )
    
    # 绘制钥匙孔（小圆 + 三角形）
    keyhole_center_x = int(size / 2)
    keyhole_center_y = int(size * 0.65)
    keyhole_radius = max(2, int(size * 0.06))
    
    painter.setBrush(QBrush(QColor("#0d0d0d")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(
        keyhole_center_x - keyhole_radius,
        keyhole_center_y - keyhole_radius,
        keyhole_radius * 2,
        keyhole_radius * 2
    )
    
    # 绘制钥匙孔下方的三角形
    triangle_height = int(size * 0.1)
    triangle_width = int(size * 0.08)
    triangle = QPolygon([
        QPoint(keyhole_center_x, keyhole_center_y + keyhole_radius),
        QPoint(keyhole_center_x - triangle_width // 2, keyhole_center_y + keyhole_radius + triangle_height),
        QPoint(keyhole_center_x + triangle_width // 2, keyhole_center_y + keyhole_radius + triangle_height)
    ])
    painter.drawPolygon(triangle)
    
    painter.end()
    
    icon.addPixmap(pixmap)
    return icon


# Shared Dark Gold Elegant Stylesheet - 统一的黑底暗金色高级风格
SHARED_DARK_GOLD_STYLESHEET = """
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1a1a1a, stop:1 #0d0d0d);
    color: #d4af37;
}

QLabel {
    color: #d4af37;
    background: transparent;
}

QLineEdit {
    background-color: #1a1a1a;
    color: #d4af37;
    border: 2px solid #d4af37;
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QLineEdit:focus {
    border: 2px solid #f0c14b;
    background-color: #202020;
}

QLineEdit::placeholder {
    color: #666666;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3a3a3a, stop:1 #2a2a2a);
    color: #d4af37;
    border: 2px solid #d4af37;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-width: 100px;
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

QPushButton:default {
    border: 3px solid #f0c14b;
}

QPushButton:disabled {
    background: #1a1a1a;
    color: #4a4a4a;
    border: 2px solid #2a2a2a;
}

QCheckBox {
    color: #d4af37;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #d4af37;
    border-radius: 4px;
    background-color: #1a1a1a;
}

QCheckBox::indicator:checked {
    background-color: #d4af37;
    image: url(none);
}

QCheckBox::indicator:hover {
    border: 2px solid #f0c14b;
}

QProgressBar {
    border: 2px solid #d4af37;
    border-radius: 6px;
    background-color: #1a1a1a;
    text-align: center;
    color: #d4af37;
    font-weight: bold;
    height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #d4af37, stop:1 #f0c14b);
    border-radius: 4px;
}

QMessageBox {
    background: #0d0d0d;
    color: #d4af37;
}

QMessageBox QLabel {
    color: #d4af37;
    font-size: 13px;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""


class PasswordInputDialog(QDialog):
    """
    密码输入对话框
    
    用于验证主密码
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化密码输入对话框
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        self.password = None
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle("验证密码")
        self.setMinimumSize(400, 180)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🔐 请输入主密码")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # 提示信息
        hint = QLabel("需要验证您的主密码才能继续操作")
        hint.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        
        # 密码输入
        password_label = QLabel("主密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("输入主密码...")
        self.password_input.returnPressed.connect(self._on_ok_clicked)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        ok_button = QPushButton("确定")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self._on_ok_clicked)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        # 添加所有组件
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addSpacing(10)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET)
        
        # 聚焦到密码输入框
        self.password_input.setFocus()
    
    def _on_ok_clicked(self):
        """确定按钮点击事件"""
        self.password = self.password_input.text()
        if not self.password:
            QMessageBox.warning(self, "错误", "请输入密码")
            return
        self.accept()
    
    def get_password(self) -> Optional[str]:
        """
        获取用户输入的密码
        
        Returns:
            str: 密码，如果用户取消则返回None
        """
        return self.password


class WelcomeWizard(QDialog):
    """
    欢迎向导对话框
    
    在首次启动时引导用户设置主密码。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化欢迎向导
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        self._keychain = KeychainStore()
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle("欢迎使用 KeyVault")
        self.setMinimumSize(450, 350)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 欢迎标题
        title = QLabel("🎉 欢迎使用 KeyVault")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 说明文字
        description = QLabel(
            "KeyVault 是一个安全的文件加密工具。\n\n"
            "首先，请设置一个主密码。\n"
            "主密码将用于加密和解密您的文件。"
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 密码输入
        password_label = QLabel("请输入主密码（至少8个字符）：")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("输入密码...")
        self.password_input.textChanged.connect(self._on_password_changed)
        
        # 密码确认
        confirm_label = QLabel("再次输入密码确认：")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("再次输入密码...")
        
        # 密码强度指示器
        self.strength_label = QLabel("密码强度: -")
        self.strength_label.setStyleSheet("color: #666666;")
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.ok_button)
        
        # 添加所有组件
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addWidget(self.strength_label)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET + """
            QLabel[objectName="strength_weak"] {
                color: #ff6666;
            }
            QLabel[objectName="strength_medium"] {
                color: #f0c14b;
            }
            QLabel[objectName="strength_strong"] {
                color: #66ff66;
            }
        """)
    
    def _on_password_changed(self, text: str):
        """密码输入变化时更新强度显示"""
        if len(text) == 0:
            self.strength_label.setText("密码强度: -")
            self.strength_label.setStyleSheet("color: #666666;")
            self.ok_button.setEnabled(False)
            return
        
        # 计算密码强度
        strength = calculate_password_strength(text)
        
        # 更新显示
        if strength == PasswordStrength.WEAK:
            self.strength_label.setText("密码强度: 弱 ⚠️")
            self.strength_label.setStyleSheet("color: #ff6666;")
        elif strength == PasswordStrength.MEDIUM:
            self.strength_label.setText("密码强度: 中 ✓")
            self.strength_label.setStyleSheet("color: #f0c14b;")
        else:  # STRONG
            self.strength_label.setText("密码强度: 强 ✓✓")
            self.strength_label.setStyleSheet("color: #66ff66;")
        
        # 只有密码长度>=8才启用确定按钮
        self.ok_button.setEnabled(len(text) >= 8)
    
    def _on_ok_clicked(self):
        """确定按钮点击事件"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # 验证密码
        if len(password) < 8:
            QMessageBox.warning(self, "密码太短", "密码至少需要8个字符")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "密码不匹配", "两次输入的密码不一致，请重新输入")
            self.confirm_input.clear()
            self.confirm_input.setFocus()
            return
        
        # 保存密码到Keychain
        try:
            self._keychain.save_password(password)
            QMessageBox.information(
                self,
                "设置成功",
                "主密码已保存！\n现在您可以开始使用 KeyVault 加密文件了。"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "保存失败",
                f"无法保存密码到系统密钥链：\n{e}"
            )


class EncryptDialog(QDialog):
    """
    加密文件对话框
    
    显示待加密文件信息和加密选项
    """
    
    def __init__(self, file_path: Path, parent: Optional[QWidget] = None):
        """
        初始化加密对话框
        
        Args:
            file_path: 要加密的文件路径（源文件）
            parent: 父widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.delete_source = True  # 默认删除源文件
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle("加密文件")
        self.setMinimumSize(500, 200)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🔒 加密文件")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # 源文件信息
        file_info_label = QLabel("待加密文件:")
        file_info_label.setStyleSheet("font-weight: bold;")
        
        file_path_label = QLabel(str(self.file_path))
        file_path_label.setObjectName("file_info")
        file_path_label.setWordWrap(True)
        
        # 选项
        self.delete_source_checkbox = QCheckBox("加密后删除原文件")
        self.delete_source_checkbox.setChecked(True)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        encrypt_button = QPushButton("加密")
        encrypt_button.setDefault(True)
        encrypt_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(encrypt_button)
        
        # 添加所有组件
        layout.addWidget(title)
        layout.addWidget(file_info_label)
        layout.addWidget(file_path_label)
        layout.addWidget(self.delete_source_checkbox)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET + """
            QLabel[objectName="file_info"] {
                color: #f0c14b;
                padding: 8px;
                background-color: rgba(212, 175, 55, 0.1);
                border: 1px solid #d4af37;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
    
    def get_options(self):
        """
        获取用户选择的选项
        
        Returns:
            dict: 包含删除源文件选项
        """
        return {
            'delete_source': self.delete_source_checkbox.isChecked()
        }


class DecryptDialog(QDialog):
    """
    解密文件对话框
    
    显示待解密文件信息和解密选项
    """
    
    def __init__(self, file_path: Path, parent: Optional[QWidget] = None):
        """
        初始化解密对话框
        
        Args:
            file_path: 要解密的文件路径（加密文件 .enc）
            parent: 父widget
        """
        super().__init__(parent)
        self.file_path = file_path
        self.open_editor = True  # 默认打开编辑器
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle("解密文件")
        self.setMinimumSize(500, 200)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🔓 解密文件")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # 源文件信息
        file_info_label = QLabel("待解密文件:")
        file_info_label.setStyleSheet("font-weight: bold;")
        
        file_path_label = QLabel(str(self.file_path))
        file_path_label.setObjectName("file_info")
        file_path_label.setWordWrap(True)
        
        # 选项
        self.open_editor_checkbox = QCheckBox("解密后打开编辑器")
        self.open_editor_checkbox.setChecked(True)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        decrypt_button = QPushButton("解密")
        decrypt_button.setDefault(True)
        decrypt_button.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(decrypt_button)
        
        # 添加所有组件
        layout.addWidget(title)
        layout.addWidget(file_info_label)
        layout.addWidget(file_path_label)
        layout.addWidget(self.open_editor_checkbox)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET + """
            QLabel[objectName="file_info"] {
                color: #f0c14b;
                padding: 8px;
                background-color: rgba(212, 175, 55, 0.1);
                border: 1px solid #d4af37;
                border-radius: 6px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
        """)
    
    def get_options(self):
        """
        获取用户选择的选项
        
        Returns:
            dict: 包含打开编辑器选项
        """
        return {
            'open_editor': self.open_editor_checkbox.isChecked()
        }


class SettingsDialog(QDialog):
    """
    设置对话框
    
    用于管理主密码和应用设置。
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化设置对话框
        
        Args:
            parent: 父widget
        """
        super().__init__(parent)
        self._keychain = KeychainStore()
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle("设置")
        self.setMinimumSize(400, 300)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("⚙️ 设置")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # 主密码部分
        password_section = QLabel("主密码管理")
        password_section_font = QFont()
        password_section_font.setBold(True)
        password_section.setFont(password_section_font)
        
        # 显示密码状态
        has_password = self._keychain.get_password() is not None
        if has_password:
            status_text = "✓ 已设置主密码"
            status_color = "#66ff66"
        else:
            status_text = "⚠ 未设置主密码"
            status_color = "#ff6666"
        
        self.status_label = QLabel(status_text)
        self.status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        # 修改密码按钮
        reset_button = QPushButton("修改主密码...")
        reset_button.clicked.connect(self._on_reset_password_clicked)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        
        button_layout.addWidget(close_button)
        
        # 添加所有组件
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(password_section)
        layout.addWidget(self.status_label)
        layout.addWidget(reset_button)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET)
    
    def _on_reset_password_clicked(self):
        """修改密码按钮点击事件"""
        # 创建密码修改对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("修改主密码")
        dialog.setMinimumSize(350, 200)
        
        # 设置窗口图标
        dialog.setWindowIcon(create_dialog_icon(32))
        
        layout = QVBoxLayout()
        
        # 旧密码
        old_label = QLabel("当前密码:")
        old_input = QLineEdit()
        old_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 新密码
        new_label = QLabel("新密码:")
        new_input = QLineEdit()
        new_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 确认新密码
        confirm_label = QLabel("确认新密码:")
        confirm_input = QLineEdit()
        confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        
        ok_btn = QPushButton("确定")
        ok_btn.setDefault(True)
        
        def on_ok():
            old_pwd = old_input.text()
            new_pwd = new_input.text()
            confirm_pwd = confirm_input.text()
            
            # 验证旧密码
            stored_pwd = self._keychain.get_password()
            if stored_pwd != old_pwd:
                QMessageBox.warning(dialog, "错误", "当前密码不正确")
                return
            
            # 验证新密码
            if len(new_pwd) < 8:
                QMessageBox.warning(dialog, "错误", "新密码至少需要8个字符")
                return
            
            if new_pwd != confirm_pwd:
                QMessageBox.warning(dialog, "错误", "两次输入的新密码不一致")
                return
            
            # 保存新密码
            try:
                self._keychain.save_password(new_pwd)
                QMessageBox.information(dialog, "成功", "主密码已更新")
                dialog.accept()
                
                # 更新状态显示
                self.status_label.setText("✓ 已设置主密码")
                self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
            except Exception as e:
                QMessageBox.critical(dialog, "错误", f"无法保存新密码：\n{e}")
        
        ok_btn.clicked.connect(on_ok)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addWidget(old_label)
        layout.addWidget(old_input)
        layout.addWidget(new_label)
        layout.addWidget(new_input)
        layout.addWidget(confirm_label)
        layout.addWidget(confirm_input)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET)
        dialog.exec()


class ProgressDialog(QDialog):
    """
    进度对话框
    
    显示加密/解密操作的进度。
    """
    
    def __init__(self, operation: str, parent: Optional[QWidget] = None):
        """
        初始化进度对话框
        
        Args:
            operation: 操作名称（"加密" 或 "解密"）
            parent: 父widget
        """
        super().__init__(parent)
        self.operation = operation
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI组件"""
        self.setWindowTitle(f"{self.operation}中...")
        self.setMinimumSize(350, 150)
        self.setModal(True)
        
        # 设置窗口图标
        self.setWindowIcon(create_dialog_icon(32))
        
        # 禁用关闭按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 提示文字
        self.label = QLabel(f"正在{self.operation}文件，请稍候...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # 设置样式 - 使用统一的暗金色主题
        self.setStyleSheet(SHARED_DARK_GOLD_STYLESHEET)
    
    def set_message(self, message: str):
        """更新提示消息"""
        self.label.setText(message)
