"""
KeyVault GUI 应用程序入口

提供独立的 GUI 应用程序启动点。
"""

import sys
from PySide6.QtWidgets import QApplication

from configcrypt.gui.main_window import MainWindow


def main():
    """
    启动 KeyVault GUI 应用程序

    Returns:
        int: 应用程序退出码
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("ConfigCrypt")
    app.setApplicationDisplayName("ConfigCrypt - 文件加密工具")
    app.setOrganizationName("ConfigCrypt Team")

    # 创建主窗口实例（用于获取图标）
    window = MainWindow()

    # 设置全局应用图标（用于任务栏和系统托盘）
    app.setWindowIcon(window._create_app_icon())

    # 显示主窗口
    window.show()

    # 运行应用程序事件循环
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
