"""
KeyVault 主窗口模块

提供 GUI 应用程序的主窗口界面，包括文件拖拽功能。
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QMimeData, QThread
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QPalette,
    QColor,
    QFont,
    QAction,
    QIcon,
    QPixmap,
    QPainter,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMenu,
    QMenuBar,
    QDialog,
    QSplitter,
)

from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.vault import Vault
from configcrypt.core.editor_launcher import EditorLauncher
from configcrypt.core.exceptions import DecryptionError, InvalidTokenError, EncryptionError
from configcrypt.gui.dialogs import (
    WelcomeWizard,
    EncryptDialog,
    DecryptDialog,
    SettingsDialog,
    ProgressDialog,
    PasswordInputDialog,
)
from configcrypt.gui.history_panel import HistoryPanel
from configcrypt.gui.history import HistoryManager


class DropZoneWidget(QWidget):
    """
    文件拖拽区组件

    支持拖拽文件到窗口进行加密/解密操作，
    也支持通过按钮选择文件。

    Signals:
        file_dropped(Path): 当文件被拖入或选择时发出信号
    """

    file_dropped = Signal(Path)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        初始化拖拽区组件

        Args:
            parent: 父widget
        """
        super().__init__(parent)
        self._setup_ui()
        self._setup_drag_drop()

    def _setup_ui(self):
        """设置UI组件"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # 主提示文字
        hint_label = QLabel("拖拽文件到此处")
        hint_font = QFont()
        hint_font.setPointSize(14)
        hint_font.setBold(True)
        hint_label.setFont(hint_font)
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #d4af37;")

        # 拖拽区域容器（锁图标和两个按钮在同一行）
        drop_area_layout = QHBoxLayout()
        drop_area_layout.setSpacing(80)  # 增加间距，按钮放到两边
        drop_area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 左侧加密按钮（缩小到70x70，红色文字）
        encrypt_button = QPushButton("加密")
        encrypt_button.setFixedSize(70, 70)
        encrypt_button.clicked.connect(self._on_select_encrypt_file_clicked)
        encrypt_font = QFont()
        encrypt_font.setPointSize(10)
        encrypt_font.setBold(True)
        encrypt_button.setFont(encrypt_font)
        encrypt_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: #ff6666;
                border: 3px solid #d4af37;
                border-radius: 35px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 3px solid #ff6666;
                color: #ff8888;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 3px solid #cc4444;
                color: #cc4444;
            }
        """)

        # 中间锁图标
        icon_label = QLabel("🔐")
        icon_font = QFont()
        icon_font.setPointSize(56)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 右侧解密按钮（缩小到70x70，绿色文字）
        decrypt_button = QPushButton("解密")
        decrypt_button.setFixedSize(70, 70)
        decrypt_button.clicked.connect(self._on_select_decrypt_file_clicked)
        decrypt_font = QFont()
        decrypt_font.setPointSize(10)
        decrypt_font.setBold(True)
        decrypt_button.setFont(decrypt_font)
        decrypt_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: #66ff66;
                border: 3px solid #d4af37;
                border-radius: 35px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 3px solid #66ff66;
                color: #88ff88;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 3px solid #44cc44;
                color: #44cc44;
            }
        """)

        drop_area_layout.addWidget(encrypt_button)
        drop_area_layout.addWidget(icon_label)
        drop_area_layout.addWidget(decrypt_button)

        # 添加组件到布局
        layout.addStretch()
        layout.addWidget(hint_label)
        layout.addSpacing(20)
        layout.addLayout(drop_area_layout)
        layout.addStretch()

        self.setLayout(layout)

        # 设置样式
        self._setup_style()

    def _setup_style(self):
        """设置组件样式 - 黑底暗金色高级风格"""
        self.setStyleSheet("""
            DropZoneWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1a1a1a, stop:1 #0d0d0d);
                border: 2px dashed #d4af37;
                border-radius: 12px;
            }
            DropZoneWidget[dragActive="true"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #2a2a2a, stop:1 #1a1a1a);
                border: 3px dashed #f0c14b;
            }
            QLabel {
                color: #d4af37;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: #d4af37;
                border: 2px solid #d4af37;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px 20px;
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

    def _setup_drag_drop(self):
        """设置拖拽功能"""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        拖拽进入事件

        Args:
            event: 拖拽事件
        """
        # 检查是否包含文件URL
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            # 只接受单个文件
            if len(urls) == 1 and urls[0].isLocalFile():
                file_path = Path(urls[0].toLocalFile())
                if file_path.is_file():
                    event.acceptProposedAction()
                    # 设置拖拽激活状态
                    self.setProperty("dragActive", "true")
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return

        event.ignore()

    def dragLeaveEvent(self, event):
        """
        拖拽离开事件

        Args:
            event: 拖拽事件
        """
        # 取消拖拽激活状态
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        """
        文件放下事件

        Args:
            event: 放下事件
        """
        # 取消拖拽激活状态
        self.setProperty("dragActive", "false")
        self.style().unpolish(self)
        self.style().polish(self)

        # 获取文件路径
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            file_path = Path(urls[0].toLocalFile())
            if file_path.is_file():
                # 发出文件选择信号
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
            else:
                QMessageBox.warning(self, "无效文件", f"不是一个有效的文件: {file_path}")

    def _on_select_encrypt_file_clicked(self):
        """处理选择加密文件按钮点击事件 - 只显示明文文件"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择要加密的文件",
            "",
            "所有文件 (*);;文本文件 (*.txt);;配置文件 (*.json *.yaml *.yml *.env)",
            "所有文件 (*)",  # Default filter
        )

        if file_path:
            # 检查是否选择了 .enc 文件
            if Path(file_path).suffix.lower() == ".enc":
                QMessageBox.warning(
                    self, "文件类型错误", "加密操作不能选择 .enc 文件。\n请选择明文文件进行加密。"
                )
                return
            self.file_dropped.emit(Path(file_path))

    def _on_select_decrypt_file_clicked(self):
        """处理选择解密文件按钮点击事件 - 只显示 .enc 文件"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择要解密的文件",
            "",
            "加密文件 (*.enc);;所有文件 (*)",
            "加密文件 (*.enc)",  # Default filter - 默认显示 .enc 文件
        )

        if file_path:
            # 检查是否选择了非 .enc 文件
            if Path(file_path).suffix.lower() != ".enc":
                reply = QMessageBox.question(
                    self,
                    "文件类型提示",
                    f"您选择的文件不是 .enc 格式。\n确定要解密此文件吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            self.file_dropped.emit(Path(file_path))

    def _on_add_file_clicked(self):
        """处理中央添加文件按钮点击事件 - 智能选择文件"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有文件 (*);;加密文件 (*.enc);;文本文件 (*.txt);;配置文件 (*.json *.yaml *.yml *.env)",
            "所有文件 (*)",
        )

        if file_path:
            self.file_dropped.emit(Path(file_path))


class MainWindow(QMainWindow):
    """
    KeyVault 主窗口

    提供文件加密解密的图形用户界面。
    """

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self._keychain = KeychainStore()
        self._vault = Vault(self._keychain)
        self._editor_launcher = EditorLauncher()
        self.history_manager = HistoryManager()
        self._setup_window()
        self._setup_menu()
        self._setup_ui()
        self._check_first_run()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("ConfigCrypt - 文件加密工具")

        # 设置应用图标
        self.setWindowIcon(self._create_app_icon())

        # 获取屏幕尺寸
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 设置窗口大小为屏幕的38.5%宽度和35%高度（缩小30%）
        window_width = int(screen_width * 0.385)
        window_height = int(screen_height * 0.35)

        self.setMinimumSize(900, 600)
        self.resize(window_width, window_height)

        # 设置窗口位置：屏幕中上部偏左
        # X: 屏幕宽度的22.5%位置（居中偏左）
        # Y: 屏幕高度的15%位置（偏上）
        x_position = int(screen_width * 0.225)
        y_position = int(screen_height * 0.15)
        self.move(x_position, y_position)

    def _create_app_icon(self) -> QIcon:
        """
        创建应用图标

        使用程序化方式创建一个黑底暗金色的锁图标

        Returns:
            QIcon: 应用图标
        """
        # 创建不同尺寸的图标
        icon = QIcon()
        for size in [16, 32, 48, 64, 128, 256]:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 绘制圆形背景（黑色渐变）
            from PySide6.QtGui import QBrush, QRadialGradient

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
                size * 0.05,
            )

            # 绘制锁梁（暗金色圆弧）
            from PySide6.QtGui import QPen

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
                180 * 16,  # 扫描角度（180度）
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
                keyhole_radius * 2,
            )

            # 绘制钥匙孔下方的三角形
            from PySide6.QtGui import QPolygon
            from PySide6.QtCore import QPoint

            triangle_height = int(size * 0.1)
            triangle_width = int(size * 0.08)
            triangle = QPolygon(
                [
                    QPoint(keyhole_center_x, keyhole_center_y + keyhole_radius),
                    QPoint(
                        keyhole_center_x - triangle_width // 2,
                        keyhole_center_y + keyhole_radius + triangle_height,
                    ),
                    QPoint(
                        keyhole_center_x + triangle_width // 2,
                        keyhole_center_y + keyhole_radius + triangle_height,
                    ),
                ]
            )
            painter.drawPolygon(triangle)

            painter.end()

            icon.addPixmap(pixmap)

        return icon

    def _setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        open_action = QAction("打开文件(&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("退出(&Q)", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # 查看菜单
        view_menu = menubar.addMenu("查看(&V)")

        self.history_action = QAction("显示历史面板(&H)", self)
        self.history_action.setCheckable(True)
        self.history_action.setChecked(True)
        self.history_action.triggered.connect(self._toggle_history_panel)
        view_menu.addAction(self.history_action)

        # 设置菜单
        settings_menu = menubar.addMenu("设置(&S)")

        settings_action = QAction("首选项(&P)...", self)
        settings_action.triggered.connect(self._on_settings)
        settings_menu.addAction(settings_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)...", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _center_window(self):
        """将窗口居中显示"""
        from PySide6.QtWidgets import QApplication

        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _setup_ui(self):
        """设置UI组件"""
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局（上下结构）
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建标题区域（黑底暗金色）
        title_widget = QWidget()
        title_widget.setFixedHeight(80)
        title_widget.setStyleSheet("""
            QWidget {
                background: #0d0d0d;
                border-bottom: 2px solid #d4af37;
            }
        """)
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(30, 15, 30, 15)
        title_layout.setSpacing(5)

        # 主标题
        title_label = QLabel("🔐 ConfigCrypt 文件加密工具")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #d4af37;")

        # 副标题
        subtitle_label = QLabel("安全 · 简洁 · 高效")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #a0a0a0;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_widget.setLayout(title_layout)

        # 创建分割器 (Drop Zone 和 History Panel) - 改为垂直分割
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # 创建拖拽区
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self._handle_file)

        # 创建历史面板（传入共享的history_manager）
        self.history_panel = HistoryPanel(self.history_manager)
        self.history_panel.file_selected.connect(self._handle_file)

        # 添加到分割器
        self.splitter.addWidget(self.drop_zone)
        self.splitter.addWidget(self.history_panel)

        # 设置分割器比例 (50% drop zone, 50% history)
        self.splitter.setStretchFactor(0, 50)
        self.splitter.setStretchFactor(1, 50)

        # 添加组件到布局
        main_layout.addWidget(title_widget)
        main_layout.addWidget(self.splitter, stretch=1)

        central_widget.setLayout(main_layout)

        # 设置应用样式
        self._setup_app_style()

    def _setup_app_style(self):
        """设置应用程序样式 - 黑底暗金色高级风格"""
        self.setStyleSheet("""
            QMainWindow {
                background: #0d0d0d;
            }
            QMenuBar {
                background: #1a1a1a;
                color: #d4af37;
                border-bottom: 1px solid #d4af37;
                font-weight: bold;
                font-size: 13px;
                padding: 4px 0px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 10px 16px;
                margin: 0px 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: #2a2a2a;
                color: #f0c14b;
            }
            QMenu {
                background-color: #1a1a1a;
                color: #d4af37;
                border: 2px solid #d4af37;
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                margin: 2px 4px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #2a2a2a;
                color: #f0c14b;
            }
            QMenu::separator {
                height: 1px;
                background: #3a3a3a;
                margin: 6px 10px;
            }
            QSplitter::handle {
                background: #d4af37;
                height: 2px;
            }
            QSplitter::handle:hover {
                background: #f0c14b;
                height: 3px;
            }
        """)

    def _toggle_history_panel(self, checked: bool):
        """显示/隐藏历史面板"""
        if checked:
            self.history_panel.show()
        else:
            self.history_panel.hide()

    def _handle_file(self, file_path: Path):
        """
        处理文件选择或拖拽

        根据文件类型自动识别是加密还是解密操作

        Args:
            file_path: 文件路径
        """
        # 识别文件类型
        if file_path.suffix.lower() == ".enc":
            # 加密文件 - 触发解密流程
            self._handle_decrypt(file_path)
        else:
            # 明文文件 - 触发加密流程
            self._handle_encrypt(file_path)

    def _handle_encrypt(self, file_path: Path):
        """
        处理加密操作

        Args:
            file_path: 要加密的文件路径
        """
        # 显示加密对话框
        dialog = EncryptDialog(file_path, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # 获取用户选项
        options = dialog.get_options()
        delete_source = options["delete_source"]

        # 询问用户加密后文件的保存位置
        default_output = Path(str(file_path) + ".enc")
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存加密文件",
            str(default_output),
            "加密文件 (*.enc);;所有文件 (*)",
            "加密文件 (*.enc)",
        )

        if not output_path:
            # 用户取消了保存
            return

        output_path = Path(output_path)

        # 检查输出文件是否已存在
        if output_path.exists():
            reply = QMessageBox.question(
                self,
                "文件已存在",
                f"文件 {output_path.name} 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            # 删除已存在的文件
            output_path.unlink()

        # 显示进度对话框
        progress = ProgressDialog("加密", self)
        progress.show()

        # 执行加密
        try:
            self._vault.encrypt_file(
                file_path, output_path, password=None, delete_source=delete_source  # 从Keychain读取
            )

            progress.close()

            # ✅ 记录历史 - 成功
            self.history_manager.add_record(
                operation="encrypt",
                source_file=file_path,
                output_file=output_path,
                status="success",
            )
            self.history_panel._load_history()  # 刷新历史面板

            # 显示成功消息
            QMessageBox.information(
                self,
                "加密成功",
                f"文件已成功加密！\n\n"
                f"源文件: {file_path.name}\n"
                f"加密文件: {output_path.name}",
            )

        except FileNotFoundError:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="encrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=f"文件不存在: {file_path}",
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "错误", f"文件不存在: {file_path}")
        except EncryptionError as e:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="encrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=str(e),
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "加密失败", f"无法加密文件:\n{e}")
        except Exception as e:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="encrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=str(e),
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "错误", f"发生未知错误:\n{e}")

    def _handle_decrypt(self, file_path: Path):
        """
        处理解密操作

        Args:
            file_path: 要解密的文件路径（.enc文件）
        """
        # 显示解密对话框
        dialog = DecryptDialog(file_path, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        # 获取用户选项
        options = dialog.get_options()
        open_editor = options["open_editor"]

        # ✅ 问题2修复：验证主密码
        password_dialog = PasswordInputDialog(self)
        if password_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        input_password = password_dialog.get_password()

        # 验证密码是否正确
        stored_password = self._keychain.get_password()
        if stored_password is None:
            QMessageBox.critical(self, "错误", "未设置主密码。请先运行首次设置。")
            return

        if input_password != stored_password:
            QMessageBox.critical(self, "密码错误", "主密码不正确，无法解密文件。")
            return

        # 询问用户解密后文件的保存位置
        # 默认路径：移除.enc扩展名，与加密文件同目录
        if file_path.suffix.lower() == ".enc":
            default_output = file_path.with_suffix("")
        else:
            default_output = Path(str(file_path) + ".decrypted")

        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存解密文件", str(default_output), "所有文件 (*)"
        )

        if not output_path:
            # 用户取消了保存
            return

        output_path = Path(output_path)

        # 检查输出文件是否已存在
        if output_path.exists():
            reply = QMessageBox.question(
                self,
                "文件已存在",
                f"文件 {output_path.name} 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            # 删除已存在的文件
            output_path.unlink()

        # 显示进度对话框
        progress = ProgressDialog("解密", self)
        progress.show()

        # 执行解密
        try:
            self._vault.decrypt_file(
                file_path, output_path, password=input_password  # 使用用户输入的密码
            )

            progress.close()

            # ✅ 记录历史 - 成功
            self.history_manager.add_record(
                operation="decrypt",
                source_file=file_path,
                output_file=output_path,
                status="success",
            )
            self.history_panel._load_history()  # 刷新历史面板

            # 显示成功消息
            QMessageBox.information(
                self,
                "解密成功",
                f"文件已成功解密！\n\n"
                f"加密文件: {file_path.name}\n"
                f"解密文件: {output_path.name}",
            )

            # 如果选择打开编辑器
            if open_editor:
                try:
                    self._editor_launcher.open_file(output_path)
                except Exception as e:
                    QMessageBox.warning(
                        self, "无法打开编辑器", f"文件已解密，但无法打开编辑器:\n{e}"
                    )

        except FileNotFoundError:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="decrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=f"文件不存在: {file_path}",
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "错误", f"文件不存在: {file_path}")
        except InvalidTokenError:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="decrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message="密码错误或文件已损坏/被篡改",
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "解密失败", "密码错误或文件已损坏/被篡改")
        except DecryptionError as e:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="decrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=str(e),
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "解密失败", f"无法解密文件:\n{e}")
        except Exception as e:
            progress.close()
            # ✅ 记录历史 - 失败
            self.history_manager.add_record(
                operation="decrypt",
                source_file=file_path,
                output_file=output_path,
                status="failed",
                error_message=str(e),
            )
            self.history_panel._load_history()

            QMessageBox.critical(self, "错误", f"发生未知错误:\n{e}")

    def _check_first_run(self):
        """检查是否首次运行，如果是则显示欢迎向导"""
        password = self._keychain.get_password()
        if password is None:
            # 首次运行，显示欢迎向导
            wizard = WelcomeWizard(self)
            if wizard.exec() != QDialog.DialogCode.Accepted:
                # 用户取消了向导，关闭应用
                self.close()

    def _on_open_file(self):
        """文件菜单 - 打开文件"""
        # Explicitly set the default filter to "所有文件 (*)"
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "选择要加密或解密的文件",
            "",
            "所有文件 (*);;加密文件 (*.enc)",
            "所有文件 (*)",  # Default filter
        )

        if file_path:
            self._handle_file(Path(file_path))

    def _on_settings(self):
        """设置菜单 - 首选项"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def _on_about(self):
        """帮助菜单 - 关于"""
        QMessageBox.about(
            self,
            "关于 ConfigCrypt",
            "<h3>ConfigCrypt 文件加密工具</h3>"
            "<p>版本 0.1.0</p>"
            "<p>一个安全、易用的文件加密工具</p>"
            "<p>支持 CLI、GUI 和 Python Library 三种使用方式</p>"
            "<p><br>© 2025 ConfigCrypt Team</p>",
        )
