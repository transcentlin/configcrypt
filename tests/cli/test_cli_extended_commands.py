"""
CLI扩展命令测试

测试 kv status 和 kv reset-password 命令，
以及 decrypt 命令的 --open 和 --editor 选项
"""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock

from configcrypt.cli.commands import cli
from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.vault import Vault


@pytest.fixture
def cli_runner():
    """创建CLI运行器"""
    return CliRunner()


@pytest.fixture
def temp_test_file(tmp_path):
    """创建临时测试文件"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content for CLI extended commands")
    return test_file


class TestStatusCommand:
    """测试 kv status 命令"""
    
    def test_status_with_keychain_available_and_password_set(self, cli_runner):
        """测试Keychain可用且密码已设置时的状态"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
                result = cli_runner.invoke(cli, ['status'])
                
                assert result.exit_code == 0
                assert "Keychain状态: 可用" in result.output
                assert "主密码: 已设置" in result.output
                assert "密码强度:" in result.output
    
    def test_status_with_keychain_available_no_password(self, cli_runner):
        """测试Keychain可用但密码未设置时的状态"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value=None):
                result = cli_runner.invoke(cli, ['status'])
                
                assert result.exit_code == 0
                assert "Keychain状态: 可用" in result.output
                assert "主密码: 未设置" in result.output
                assert "运行 'kv init' 设置主密码" in result.output
    
    def test_status_with_keychain_unavailable(self, cli_runner):
        """测试Keychain不可用时的状态"""
        with patch.object(KeychainStore, 'is_available', return_value=False):
            result = cli_runner.invoke(cli, ['status'])
            
            assert result.exit_code == 1
            assert "Keychain状态: 不可用" in result.output


class TestResetPasswordCommand:
    """测试 kv reset-password 命令"""
    
    def test_reset_password_success(self, cli_runner):
        """测试成功修改密码"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value='oldpass123'):
                with patch.object(KeychainStore, 'save_password') as mock_save:
                    result = cli_runner.invoke(
                        cli,
                        ['reset-password'],
                        input='oldpass123\nnewpass456\nnewpass456\n'
                    )
                    
                    assert result.exit_code == 0
                    assert "密码验证成功" in result.output
                    assert "主密码已成功更新" in result.output
                    mock_save.assert_called_once_with('newpass456')
    
    def test_reset_password_wrong_old_password(self, cli_runner):
        """测试旧密码不正确"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value='oldpass123'):
                result = cli_runner.invoke(
                    cli,
                    ['reset-password'],
                    input='wrongpass\n'
                )
                
                assert result.exit_code == 1
                assert "当前密码不正确" in result.output
    
    def test_reset_password_no_existing_password(self, cli_runner):
        """测试没有现有密码时修改"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value=None):
                result = cli_runner.invoke(cli, ['reset-password'])
                
                assert result.exit_code == 1
                assert "未找到主密码" in result.output
    
    def test_reset_password_same_as_old(self, cli_runner):
        """测试新密码与旧密码相同"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value='oldpass123'):
                with patch.object(KeychainStore, 'save_password') as mock_save:
                    result = cli_runner.invoke(
                        cli,
                        ['reset-password'],
                        input='oldpass123\noldpass123\noldpass123\nnewpass456\nnewpass456\n'
                    )
                    
                    assert result.exit_code == 0
                    assert "新密码不能与旧密码相同" in result.output
                    assert "主密码已成功更新" in result.output
                    mock_save.assert_called_once_with('newpass456')
    
    def test_reset_password_too_short(self, cli_runner):
        """测试新密码太短"""
        with patch.object(KeychainStore, 'is_available', return_value=True):
            with patch.object(KeychainStore, 'get_password', return_value='oldpass123'):
                with patch.object(KeychainStore, 'save_password') as mock_save:
                    result = cli_runner.invoke(
                        cli,
                        ['reset-password'],
                        input='oldpass123\nshort\nshort\nnewpass456\nnewpass456\n'
                    )
                    
                    assert result.exit_code == 0
                    assert "密码长度至少为8个字符" in result.output
                    assert "主密码已成功更新" in result.output
                    mock_save.assert_called_once_with('newpass456')


class TestDecryptWithOpen:
    """测试 decrypt 命令的 --open 选项"""
    
    def test_decrypt_with_open_flag(self, cli_runner, temp_test_file):
        """测试--open选项成功打开编辑器"""
        # 先加密文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            vault = Vault()
            encrypted_file = vault.encrypt_file(
                temp_test_file,
                password='testpass123',
                delete_source=True  # 删除源文件避免冲突
            )
        
        # 解密并打开
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            # 需要patch CLI模块中的EditorLauncher
            with patch('keyvault.cli.commands.EditorLauncher') as MockEditorLauncher:
                mock_instance = MockEditorLauncher.return_value
                result = cli_runner.invoke(
                    cli,
                    ['decrypt', str(encrypted_file), '--open']
                )
                
                assert result.exit_code == 0, f"Failed with output: {result.output}"
                assert "文件已成功解密" in result.output
                assert "已用编辑器打开文件" in result.output
                mock_instance.open_file.assert_called_once()
    
    def test_decrypt_with_open_and_editor_option(self, cli_runner, temp_test_file):
        """测试--open和--editor选项一起使用"""
        # 先加密文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            vault = Vault()
            encrypted_file = vault.encrypt_file(
                temp_test_file,
                password='testpass123',
                delete_source=True  # 删除源文件避免冲突
            )
        
        # 解密并用指定编辑器打开
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            with patch('keyvault.cli.commands.EditorLauncher') as MockEditorLauncher:
                mock_instance = MockEditorLauncher.return_value
                result = cli_runner.invoke(
                    cli,
                    ['decrypt', str(encrypted_file), '--open', '--editor', 'nano']
                )
                
                assert result.exit_code == 0, f"Failed with output: {result.output}"
                assert "文件已成功解密" in result.output
                assert "已用编辑器打开文件" in result.output
                # 验证editor_command参数被传递
                mock_instance.open_file.assert_called_once()
                call_args = mock_instance.open_file.call_args
                assert call_args[1]['editor_command'] == 'nano'
    
    def test_decrypt_with_open_editor_not_found(self, cli_runner, temp_test_file):
        """测试--open选项但编辑器未找到"""
        # 先加密文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            vault = Vault()
            encrypted_file = vault.encrypt_file(
                temp_test_file,
                password='testpass123',
                delete_source=True  # 删除源文件避免冲突
            )
        
        # 解密但编辑器未找到
        from configcrypt.core.exceptions import EditorNotFoundError
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            with patch('keyvault.cli.commands.EditorLauncher') as MockEditorLauncher:
                mock_instance = MockEditorLauncher.return_value
                mock_instance.open_file.side_effect = EditorNotFoundError("未找到可用的编辑器")
                
                result = cli_runner.invoke(
                    cli,
                    ['decrypt', str(encrypted_file), '--open']
                )
                
                # 解密应该成功，但打开编辑器失败
                assert result.exit_code == 0, f"Failed with output: {result.output}"
                assert "文件已成功解密" in result.output
                assert "警告: 未找到可用的编辑器" in result.output


class TestFileOverwriteConfirmation:
    """测试文件覆盖确认"""
    
    def test_encrypt_overwrite_confirmed(self, cli_runner, temp_test_file):
        """测试加密时确认覆盖已存在的文件"""
        # 创建已存在的输出文件
        output_file = temp_test_file.parent / f"{temp_test_file.name}.enc"
        output_file.write_text("existing content")
        
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            result = cli_runner.invoke(
                cli,
                ['encrypt', str(temp_test_file), '--keep'],
                input='y\n'  # 确认覆盖
            )
            
            assert result.exit_code == 0
            assert "文件已成功加密" in result.output
    
    def test_encrypt_overwrite_cancelled(self, cli_runner, temp_test_file):
        """测试加密时取消覆盖"""
        # 创建已存在的输出文件
        output_file = temp_test_file.parent / f"{temp_test_file.name}.enc"
        output_file.write_text("existing content")
        
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            result = cli_runner.invoke(
                cli,
                ['encrypt', str(temp_test_file), '--keep'],
                input='n\n'  # 取消覆盖
            )
            
            assert result.exit_code == 0
            assert "操作已取消" in result.output
    
    def test_decrypt_overwrite_confirmed(self, cli_runner, temp_test_file):
        """测试解密时确认覆盖已存在的文件"""
        # 先加密文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            vault = Vault()
            encrypted_file = vault.encrypt_file(
                temp_test_file,
                password='testpass123',
                delete_source=False
            )
        
        # 解密到已存在的文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            result = cli_runner.invoke(
                cli,
                ['decrypt', str(encrypted_file), '--out', str(temp_test_file)],
                input='y\n'  # 确认覆盖
            )
            
            assert result.exit_code == 0
            assert "文件已成功解密" in result.output
    
    def test_decrypt_overwrite_cancelled(self, cli_runner, temp_test_file):
        """测试解密时取消覆盖"""
        # 先加密文件
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            vault = Vault()
            encrypted_file = vault.encrypt_file(
                temp_test_file,
                password='testpass123',
                delete_source=False
            )
        
        # 解密到已存在的文件，但取消
        with patch.object(KeychainStore, 'get_password', return_value='testpass123'):
            result = cli_runner.invoke(
                cli,
                ['decrypt', str(encrypted_file), '--out', str(temp_test_file)],
                input='n\n'  # 取消覆盖
            )
            
            assert result.exit_code == 0
            assert "操作已取消" in result.output
