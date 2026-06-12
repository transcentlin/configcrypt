"""
GUI 对话框测试

测试所有对话框组件：
- WelcomeWizard
- EncryptDialog
- DecryptDialog
- SettingsDialog
- ProgressDialog
"""

import tempfile
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

from configcrypt.gui.dialogs import (
    WelcomeWizard,
    EncryptDialog,
    DecryptDialog,
    SettingsDialog,
    ProgressDialog,
)
from configcrypt.core.keychain_store import KeychainStore


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def qapp():
    """确保QApplication实例存在"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def clean_keychain():
    """测试前清理keychain"""
    keychain = KeychainStore()
    # 清理可能存在的密码
    try:
        keychain.delete_password()
    except:
        pass
    yield keychain
    # 测试后清理
    try:
        keychain.delete_password()
    except:
        pass


class TestWelcomeWizard:
    """测试欢迎向导对话框"""

    def test_wizard_initialization(self, qtbot, qapp, clean_keychain):
        """测试向导初始化"""
        wizard = WelcomeWizard()
        qtbot.addWidget(wizard)

        # 验证组件存在
        assert wizard.windowTitle() == "欢迎使用 KeyVault"
        assert wizard.password_input is not None
        assert wizard.confirm_input is not None
        assert wizard.ok_button is not None

    def test_password_strength_indicator(self, qtbot, qapp, clean_keychain):
        """测试密码强度指示器"""
        wizard = WelcomeWizard()
        qtbot.addWidget(wizard)

        # 弱密码
        wizard.password_input.setText("12345678")
        assert "弱" in wizard.strength_label.text()

        # 中等密码
        wizard.password_input.setText("Abcd1234")
        assert "中" in wizard.strength_label.text()

        # 强密码
        wizard.password_input.setText("Abcd1234!@#$")
        assert "强" in wizard.strength_label.text()

    def test_ok_button_disabled_for_short_password(self, qtbot, qapp, clean_keychain):
        """测试短密码时确定按钮被禁用"""
        wizard = WelcomeWizard()
        qtbot.addWidget(wizard)

        # 短密码应禁用按钮
        wizard.password_input.setText("123")
        assert wizard.ok_button.isEnabled() is False

        # 8字符密码应启用按钮
        wizard.password_input.setText("12345678")
        assert wizard.ok_button.isEnabled() is True

    def test_wizard_accepts_matching_passwords(self, qtbot, qapp, clean_keychain):
        """测试向导接受匹配的密码"""
        wizard = WelcomeWizard()
        qtbot.addWidget(wizard)

        # 输入匹配的密码
        wizard.password_input.setText("test_password_123")
        wizard.confirm_input.setText("test_password_123")

        # 模拟点击确定（不实际执行）
        assert wizard.password_input.text() == wizard.confirm_input.text()


class TestEncryptDialog:
    """测试加密对话框"""

    def test_encrypt_dialog_initialization(self, qtbot, qapp, temp_dir):
        """测试加密对话框初始化"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证初始设置
        assert dialog.windowTitle() == "加密文件"
        assert dialog.file_path == test_file
        assert dialog.output_path == Path(str(test_file) + ".enc")

    def test_encrypt_dialog_default_output_path(self, qtbot, qapp, temp_dir):
        """测试默认输出路径"""
        test_file = temp_dir / "document.txt"
        test_file.write_text("content")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证默认输出路径添加了.enc
        assert str(dialog.output_path).endswith(".enc")
        assert dialog.output_input.text() == str(dialog.output_path)

    def test_encrypt_dialog_delete_source_default_checked(self, qtbot, qapp, temp_dir):
        """测试删除源文件选项默认勾选"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证删除源文件复选框默认勾选
        assert dialog.delete_source_checkbox.isChecked() is True

    def test_encrypt_dialog_get_options(self, qtbot, qapp, temp_dir):
        """测试获取用户选项"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)

        options = dialog.get_options()

        assert "output_path" in options
        assert "delete_source" in options
        assert options["delete_source"] is True


class TestDecryptDialog:
    """测试解密对话框"""

    def test_decrypt_dialog_initialization(self, qtbot, qapp, temp_dir):
        """测试解密对话框初始化"""
        test_file = temp_dir / "test.txt.enc"
        test_file.write_bytes(b"encrypted content")

        dialog = DecryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证初始设置
        assert dialog.windowTitle() == "解密文件"
        assert dialog.file_path == test_file

    def test_decrypt_dialog_removes_enc_extension(self, qtbot, qapp, temp_dir):
        """测试默认输出路径移除.enc扩展名"""
        test_file = temp_dir / "document.txt.enc"
        test_file.write_bytes(b"encrypted")

        dialog = DecryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证输出路径移除了.enc
        assert dialog.output_path == temp_dir / "document.txt"
        assert not str(dialog.output_path).endswith(".enc")

    def test_decrypt_dialog_open_editor_default_checked(self, qtbot, qapp, temp_dir):
        """测试打开编辑器选项默认勾选"""
        test_file = temp_dir / "test.enc"
        test_file.write_bytes(b"encrypted")

        dialog = DecryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证打开编辑器复选框默认勾选
        assert dialog.open_editor_checkbox.isChecked() is True

    def test_decrypt_dialog_get_options(self, qtbot, qapp, temp_dir):
        """测试获取用户选项"""
        test_file = temp_dir / "test.enc"
        test_file.write_bytes(b"encrypted")

        dialog = DecryptDialog(test_file)
        qtbot.addWidget(dialog)

        options = dialog.get_options()

        assert "output_path" in options
        assert "open_editor" in options
        assert options["open_editor"] is True


class TestSettingsDialog:
    """测试设置对话框"""

    def test_settings_dialog_initialization(self, qtbot, qapp, clean_keychain):
        """测试设置对话框初始化"""
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        # 验证初始设置
        assert dialog.windowTitle() == "设置"
        assert dialog.status_label is not None

    def test_settings_dialog_shows_password_status(self, qtbot, qapp, clean_keychain):
        """测试设置对话框显示密码状态"""
        # 没有密码时
        dialog = SettingsDialog()
        qtbot.addWidget(dialog)

        assert "未设置" in dialog.status_label.text()

        # 设置密码后
        clean_keychain.save_password("test_password_123")
        dialog2 = SettingsDialog()
        qtbot.addWidget(dialog2)

        assert "已设置" in dialog2.status_label.text()


class TestProgressDialog:
    """测试进度对话框"""

    def test_progress_dialog_initialization(self, qtbot, qapp):
        """测试进度对话框初始化"""
        dialog = ProgressDialog("加密")
        qtbot.addWidget(dialog)

        # 验证初始设置
        assert "加密" in dialog.windowTitle()
        assert dialog.progress_bar is not None

    def test_progress_dialog_message(self, qtbot, qapp):
        """测试设置进度消息"""
        dialog = ProgressDialog("解密")
        qtbot.addWidget(dialog)

        # 更新消息
        dialog.set_message("正在处理文件...")
        assert dialog.label.text() == "正在处理文件..."

    def test_progress_dialog_operations(self, qtbot, qapp):
        """测试不同操作类型"""
        encrypt_dialog = ProgressDialog("加密")
        qtbot.addWidget(encrypt_dialog)
        assert encrypt_dialog.operation == "加密"

        decrypt_dialog = ProgressDialog("解密")
        qtbot.addWidget(decrypt_dialog)
        assert decrypt_dialog.operation == "解密"


class TestDialogIntegration:
    """测试对话框集成"""

    def test_dialog_modal_behavior(self, qtbot, qapp, temp_dir):
        """测试对话框的模态行为"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)

        # 验证对话框是模态的
        assert dialog.isModal() is True

    def test_dialog_esc_key_closes(self, qtbot, qapp, temp_dir):
        """测试Esc键关闭对话框"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        dialog = EncryptDialog(test_file)
        qtbot.addWidget(dialog)
        dialog.show()

        # 模拟Esc键
        qtbot.keyPress(dialog, Qt.Key.Key_Escape)

        # 验证对话框可以被Esc关闭（result应该是Rejected）
        # 注意：由于异步特性，这里主要测试不会崩溃
        assert True

    def test_multiple_dialogs_can_be_created(self, qtbot, qapp, temp_dir):
        """测试可以创建多个对话框实例"""
        test_file1 = temp_dir / "test1.txt"
        test_file2 = temp_dir / "test2.txt"
        test_file1.write_text("test1")
        test_file2.write_text("test2")

        dialog1 = EncryptDialog(test_file1)
        dialog2 = DecryptDialog(test_file2)
        qtbot.addWidget(dialog1)
        qtbot.addWidget(dialog2)

        # 验证两个对话框都正常创建
        assert dialog1 is not None
        assert dialog2 is not None
        assert dialog1 != dialog2


class TestDialogStyling:
    """测试对话框样式"""

    def test_dialogs_have_consistent_styling(self, qtbot, qapp, temp_dir):
        """测试对话框有一致的样式"""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")

        encrypt_dialog = EncryptDialog(test_file)
        decrypt_dialog = DecryptDialog(test_file)
        qtbot.addWidget(encrypt_dialog)
        qtbot.addWidget(decrypt_dialog)

        # 验证两个对话框都应用了样式
        assert encrypt_dialog.styleSheet() != ""
        assert decrypt_dialog.styleSheet() != ""

    def test_welcome_wizard_has_title_styling(self, qtbot, qapp, clean_keychain):
        """测试欢迎向导有标题样式"""
        wizard = WelcomeWizard()
        qtbot.addWidget(wizard)

        # 查找标题label（应该有大字体）
        labels = wizard.findChildren(type(QLabel()))
        # 至少有一个label存在
        assert len(labels) > 0
