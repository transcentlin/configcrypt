"""
测试文件类型自动识别功能

验证GUI能够正确识别.enc文件和明文文件,并触发相应的加密/解密流程。
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QDialog
from configcrypt.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例（如果不存在）"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp, tmp_path):
    """创建MainWindow实例用于测试"""
    # Mock keychain to avoid system keychain interaction
    with patch('keyvault.gui.main_window.KeychainStore') as mock_keychain_class:
        mock_keychain = Mock()
        mock_keychain.get_password.return_value = "test_password123"
        mock_keychain_class.return_value = mock_keychain
        
        # Create window
        window = MainWindow()
        window.show()
        yield window
        window.close()


class TestFileTypeRecognition:
    """文件类型自动识别测试"""
    
    def test_recognizes_enc_file_as_encrypted(self, main_window, tmp_path):
        """
        测试: 识别.enc文件为加密文件
        
        验证: 当用户拖拽或选择.enc文件时,系统应该触发解密流程
        """
        # 创建测试用的.enc文件
        enc_file = tmp_path / "test_config.json.enc"
        enc_file.write_bytes(b"encrypted_content_here")
        
        # Mock _handle_decrypt 方法来验证它被调用
        with patch.object(main_window, '_handle_decrypt') as mock_decrypt:
            with patch.object(main_window, '_handle_encrypt') as mock_encrypt:
                # 调用文件处理方法
                main_window._handle_file(enc_file)
                
                # 验证解密流程被触发
                mock_decrypt.assert_called_once_with(enc_file)
                # 验证加密流程没有被触发
                mock_encrypt.assert_not_called()
    
    def test_recognizes_plaintext_file_as_unencrypted(self, main_window, tmp_path):
        """
        测试: 识别明文文件(非.enc)
        
        验证: 当用户拖拽或选择明文文件时,系统应该触发加密流程
        """
        # 创建测试用的明文文件
        plain_file = tmp_path / "test_config.json"
        plain_file.write_text('{"key": "value"}')
        
        # Mock _handle_encrypt 方法来验证它被调用
        with patch.object(main_window, '_handle_encrypt') as mock_encrypt:
            with patch.object(main_window, '_handle_decrypt') as mock_decrypt:
                # 调用文件处理方法
                main_window._handle_file(plain_file)
                
                # 验证加密流程被触发
                mock_encrypt.assert_called_once_with(plain_file)
                # 验证解密流程没有被触发
                mock_decrypt.assert_not_called()
    
    def test_recognizes_various_plaintext_extensions(self, main_window, tmp_path):
        """
        测试: 识别各种明文文件扩展名
        
        验证: .json, .yaml, .txt, .env 等文件都应该触发加密流程
        """
        test_files = [
            "config.json",
            "settings.yaml",
            "notes.txt",
            ".env",
            "data.xml",
        ]
        
        for filename in test_files:
            file_path = tmp_path / filename
            file_path.write_text("test content")
            
            with patch.object(main_window, '_handle_encrypt') as mock_encrypt:
                with patch.object(main_window, '_handle_decrypt') as mock_decrypt:
                    main_window._handle_file(file_path)
                    
                    # 所有非.enc文件都应触发加密
                    mock_encrypt.assert_called_once_with(file_path)
                    mock_decrypt.assert_not_called()
    
    def test_case_insensitive_enc_recognition(self, main_window, tmp_path):
        """
        测试: .enc扩展名识别不区分大小写
        
        验证: .ENC, .Enc, .enc 都应该被识别为加密文件
        """
        test_cases = [
            "file.enc",
            "file.ENC",
            "file.Enc",
            "file.eNc",
        ]
        
        for filename in test_cases:
            enc_file = tmp_path / filename
            enc_file.write_bytes(b"encrypted")
            
            with patch.object(main_window, '_handle_decrypt') as mock_decrypt:
                with patch.object(main_window, '_handle_encrypt') as mock_encrypt:
                    main_window._handle_file(enc_file)
                    
                    # 所有大小写变体都应触发解密
                    mock_decrypt.assert_called_once_with(enc_file)
                    mock_encrypt.assert_not_called()
    
    def test_handles_multiple_extensions_correctly(self, main_window, tmp_path):
        """
        测试: 正确处理多重扩展名
        
        验证: file.json.enc 应该识别为加密文件
        """
        # 加密文件: file.json.enc
        enc_file = tmp_path / "config.json.enc"
        enc_file.write_bytes(b"encrypted")
        
        with patch.object(main_window, '_handle_decrypt') as mock_decrypt:
            main_window._handle_file(enc_file)
            mock_decrypt.assert_called_once_with(enc_file)
        
        # 明文文件: file.json
        plain_file = tmp_path / "config.json"
        plain_file.write_text("plain")
        
        with patch.object(main_window, '_handle_encrypt') as mock_encrypt:
            main_window._handle_file(plain_file)
            mock_encrypt.assert_called_once_with(plain_file)
    
    def test_drop_zone_file_signal_triggers_recognition(self, main_window, tmp_path):
        """
        测试: DropZone文件信号触发识别
        
        验证: 当DropZone发出file_dropped信号时,自动识别流程被触发
        """
        enc_file = tmp_path / "test.enc"
        enc_file.write_bytes(b"encrypted")
        
        with patch.object(main_window, '_handle_file') as mock_handle:
            # 模拟拖拽文件
            main_window.drop_zone.file_dropped.emit(enc_file)
            
            # 验证_handle_file被调用
            mock_handle.assert_called_once_with(enc_file)


class TestButtonFileSelectionRecognition:
    """测试通过按钮选择文件时的识别"""
    
    def test_encrypt_button_filters_enc_files(self, main_window, tmp_path):
        """
        测试: 加密按钮应该警告用户不要选择.enc文件
        
        验证规则: 
        - 当用户点击"加密"按钮选择.enc文件时,应该显示警告
        - 文件不应该被传递到加密流程
        """
        enc_file = tmp_path / "test.enc"
        enc_file.write_bytes(b"encrypted")
        
        # Mock QFileDialog to return .enc file
        with patch('keyvault.gui.main_window.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (str(enc_file), "")
            
            # Mock QMessageBox.warning to verify it's called
            with patch('keyvault.gui.main_window.QMessageBox.warning') as mock_warning:
                with patch.object(main_window.drop_zone, 'file_dropped') as mock_signal:
                    # 触发加密按钮
                    main_window.drop_zone._on_select_encrypt_file_clicked()
                    
                    # 验证警告被显示
                    mock_warning.assert_called_once()
                    # 验证文件信号没有被发出
                    mock_signal.emit.assert_not_called()
    
    def test_decrypt_button_prompts_for_non_enc_files(self, main_window, tmp_path):
        """
        测试: 解密按钮对非.enc文件显示确认提示
        
        验证规则:
        - 当用户点击"解密"按钮选择非.enc文件时,应该显示确认对话框
        - 如果用户确认,文件应该被传递到解密流程
        - 如果用户取消,文件不应该被处理
        """
        from PySide6.QtWidgets import QMessageBox
        
        plain_file = tmp_path / "test.txt"
        plain_file.write_text("plain text")
        
        # Mock QFileDialog
        with patch('keyvault.gui.main_window.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = (str(plain_file), "")
            
            # 场景1: 用户确认解密
            with patch('keyvault.gui.main_window.QMessageBox.question') as mock_question:
                mock_question.return_value = QMessageBox.StandardButton.Yes  # 使用正确的枚举值
                
                with patch.object(main_window.drop_zone, 'file_dropped') as mock_signal:
                    main_window.drop_zone._on_select_decrypt_file_clicked()
                    
                    # 验证确认对话框被显示
                    mock_question.assert_called_once()
                    # 验证文件信号被发出
                    mock_signal.emit.assert_called_once_with(plain_file)
            
            # 场景2: 用户取消
            with patch('keyvault.gui.main_window.QMessageBox.question') as mock_question:
                mock_question.return_value = QMessageBox.StandardButton.No  # 使用正确的枚举值
                
                with patch.object(main_window.drop_zone, 'file_dropped') as mock_signal:
                    main_window.drop_zone._on_select_decrypt_file_clicked()
                    
                    # 验证文件信号没有被发出
                    mock_signal.emit.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
