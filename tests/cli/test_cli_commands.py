"""
CLI命令测试

测试cc init, cc encrypt, cc decrypt命令
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from configcrypt.cli.commands import cli, _calculate_password_strength
from configcrypt.core.exceptions import EncryptionError, DecryptionError, InvalidTokenError


class TestPasswordStrength:
    """密码强度计算测试"""

    def test_weak_password_short(self):
        """测试短密码为弱"""
        assert _calculate_password_strength("abc") == "弱"
        assert _calculate_password_strength("1234567") == "弱"

    def test_weak_password_only_letters(self):
        """测试仅字母密码为弱"""
        assert _calculate_password_strength("abcdefgh") == "弱"

    def test_weak_password_only_digits(self):
        """测试仅数字密码为弱"""
        assert _calculate_password_strength("12345678") == "弱"

    def test_medium_password(self):
        """测试中等强度密码"""
        assert _calculate_password_strength("abc12345") == "中"
        assert _calculate_password_strength("password1") == "中"

    def test_strong_password(self):
        """测试强密码"""
        assert _calculate_password_strength("Abc123!@#$%^") == "强"
        assert _calculate_password_strength("MyP@ssw0rd123") == "强"

    def test_password_strength_monotonicity(self):
        """测试密码强度单调性：更长且更复杂的密码不应更弱"""
        # 8字符字母+数字 vs 12字符字母+数字+特殊字符
        medium = _calculate_password_strength("abc12345")
        strong = _calculate_password_strength("abc12345!@#$")

        assert medium == "中"
        assert strong == "强"


class TestInitCommand:
    """cc init命令测试"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_init_keychain_unavailable(self, runner):
        """测试Keychain不可用时的处理"""
        with patch("configcrypt.cli.commands.KeychainStore") as MockKeychain:
            mock_keychain = MockKeychain.return_value
            mock_keychain.is_available.return_value = False

            result = runner.invoke(cli, ["init"])

            assert result.exit_code == 1
            assert "Keychain不可用" in result.output

    def test_init_new_password(self, runner):
        """测试设置新密码"""
        with patch("configcrypt.cli.commands.KeychainStore") as MockKeychain:
            mock_keychain = MockKeychain.return_value
            mock_keychain.is_available.return_value = True
            mock_keychain.get_password.return_value = None

            # 输入密码（需要两次确认）
            result = runner.invoke(cli, ["init"], input="MyP@ssw0rd123\nMyP@ssw0rd123\n")

            assert result.exit_code == 0
            assert "主密码已成功保存" in result.output
            mock_keychain.save_password.assert_called_once()

    def test_init_password_too_short(self, runner):
        """测试密码太短时重新输入"""
        with patch("configcrypt.cli.commands.KeychainStore") as MockKeychain:
            mock_keychain = MockKeychain.return_value
            mock_keychain.is_available.return_value = True
            mock_keychain.get_password.return_value = None

            # 第一次输入太短，第二次输入正确
            result = runner.invoke(
                cli, ["init"], input="short\nshort\nMyP@ssw0rd123\nMyP@ssw0rd123\n"
            )

            assert result.exit_code == 0
            assert "密码长度至少为8个字符" in result.output
            assert "主密码已成功保存" in result.output

    def test_init_weak_password_declined(self, runner):
        """测试拒绝使用弱密码"""
        with patch("configcrypt.cli.commands.KeychainStore") as MockKeychain:
            mock_keychain = MockKeychain.return_value
            mock_keychain.is_available.return_value = True
            mock_keychain.get_password.return_value = None

            # 输入弱密码并拒绝，然后输入强密码
            result = runner.invoke(
                cli, ["init"], input="weakpass\nweakpass\nn\nMyP@ssw0rd123\nMyP@ssw0rd123\n"
            )

            assert result.exit_code == 0
            assert "密码强度: 弱" in result.output
            assert "密码强度较弱" in result.output

    def test_init_password_exists_cancel(self, runner):
        """测试已有密码时取消操作"""
        with patch("configcrypt.cli.commands.KeychainStore") as MockKeychain:
            mock_keychain = MockKeychain.return_value
            mock_keychain.is_available.return_value = True
            mock_keychain.get_password.return_value = "existing_password"

            result = runner.invoke(cli, ["init"], input="n\n")  # 取消重新设置

            assert result.exit_code == 0
            assert "已存在主密码" in result.output
            assert "操作已取消" in result.output


class TestEncryptCommand:
    """cc encrypt命令测试"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def temp_file(self):
        """创建临时测试文件"""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="utf-8"
        ) as f:
            f.write("测试内容")
            temp_path = Path(f.name)
        yield temp_path
        # 清理
        if temp_path.exists():
            temp_path.unlink()
        encrypted = Path(str(temp_path) + ".enc")
        if encrypted.exists():
            encrypted.unlink()

    def test_encrypt_success(self, runner, temp_file):
        """测试成功加密文件"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            encrypted_path = Path(str(temp_file) + ".enc")
            mock_vault.encrypt_file.return_value = encrypted_path

            result = runner.invoke(cli, ["encrypt", str(temp_file)])

            assert result.exit_code == 0
            assert "文件已成功加密" in result.output
            assert "源文件已删除" in result.output
            mock_vault.encrypt_file.assert_called_once()

    def test_encrypt_with_keep_flag(self, runner, temp_file):
        """测试使用--keep选项保留源文件"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            encrypted_path = Path(str(temp_file) + ".enc")
            mock_vault.encrypt_file.return_value = encrypted_path

            result = runner.invoke(cli, ["encrypt", str(temp_file), "--keep"])

            assert result.exit_code == 0
            assert "源文件保留" in result.output
            # 验证传递了delete_source=False
            call_kwargs = mock_vault.encrypt_file.call_args[1]
            assert call_kwargs["delete_source"] is False

    def test_encrypt_with_custom_output(self, runner, temp_file):
        """测试使用--out选项指定输出路径"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            custom_output = Path("/tmp/custom.enc")
            mock_vault.encrypt_file.return_value = custom_output

            result = runner.invoke(cli, ["encrypt", str(temp_file), "--out", str(custom_output)])

            assert result.exit_code == 0
            # 验证传递了正确的输出路径
            call_kwargs = mock_vault.encrypt_file.call_args[1]
            assert call_kwargs["output_path"] == custom_output

    def test_encrypt_file_not_found(self, runner):
        """测试加密不存在的文件"""
        result = runner.invoke(cli, ["encrypt", "nonexistent_file.txt"])

        # Click会在文件不存在时提前退出
        assert result.exit_code != 0

    def test_encrypt_no_password(self, runner, temp_file):
        """测试未设置主密码时的错误"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            mock_vault.encrypt_file.side_effect = EncryptionError("未找到保存的密码")

            result = runner.invoke(cli, ["encrypt", str(temp_file)])

            assert result.exit_code == 1
            assert "未找到主密码" in result.output
            assert "cc init" in result.output

    def test_encrypt_output_exists(self, runner, temp_file):
        """测试输出文件已存在"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            mock_vault.encrypt_file.side_effect = EncryptionError("输出文件已存在: test.enc")

            result = runner.invoke(cli, ["encrypt", str(temp_file)])

            assert result.exit_code == 1
            assert "输出文件已存在" in result.output
            assert "--out" in result.output


class TestDecryptCommand:
    """cc decrypt命令测试"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def temp_encrypted_file(self):
        """创建临时加密文件"""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".enc") as f:
            f.write(b"encrypted_data")
            temp_path = Path(f.name)
        yield temp_path
        # 清理
        if temp_path.exists():
            temp_path.unlink()
        decrypted = temp_path.with_suffix("")
        if decrypted.exists():
            decrypted.unlink()

    def test_decrypt_success(self, runner, temp_encrypted_file):
        """测试成功解密文件"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            decrypted_path = temp_encrypted_file.with_suffix("")
            mock_vault.decrypt_file.return_value = decrypted_path

            result = runner.invoke(cli, ["decrypt", str(temp_encrypted_file)])

            assert result.exit_code == 0
            assert "文件已成功解密" in result.output
            mock_vault.decrypt_file.assert_called_once()

    def test_decrypt_with_custom_output(self, runner, temp_encrypted_file):
        """测试使用--out选项指定输出路径"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            custom_output = Path("/tmp/decrypted.txt")
            mock_vault.decrypt_file.return_value = custom_output

            result = runner.invoke(
                cli, ["decrypt", str(temp_encrypted_file), "--out", str(custom_output)]
            )

            assert result.exit_code == 0
            # 验证传递了正确的输出路径
            call_kwargs = mock_vault.decrypt_file.call_args[1]
            assert call_kwargs["output_path"] == custom_output

    def test_decrypt_wrong_password(self, runner, temp_encrypted_file):
        """测试错误密码"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            mock_vault.decrypt_file.side_effect = InvalidTokenError("密码错误")

            result = runner.invoke(cli, ["decrypt", str(temp_encrypted_file)])

            assert result.exit_code == 1
            assert "密码错误" in result.output
            assert "cc init" in result.output

    def test_decrypt_no_password(self, runner, temp_encrypted_file):
        """测试未设置主密码"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            mock_vault.decrypt_file.side_effect = DecryptionError("未找到保存的密码")

            result = runner.invoke(cli, ["decrypt", str(temp_encrypted_file)])

            assert result.exit_code == 1
            assert "未找到主密码" in result.output
            assert "cc init" in result.output

    def test_decrypt_output_exists(self, runner, temp_encrypted_file):
        """测试输出文件已存在"""
        with patch("configcrypt.cli.commands.Vault") as MockVault:
            mock_vault = MockVault.return_value
            mock_vault.decrypt_file.side_effect = DecryptionError("输出文件已存在: test.txt")

            result = runner.invoke(cli, ["decrypt", str(temp_encrypted_file)])

            assert result.exit_code == 1
            assert "输出文件已存在" in result.output
            assert "--out" in result.output


class TestCLIIntegration:
    """CLI集成测试"""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_help_command(self, runner):
        """测试帮助命令"""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "KeyVault" in result.output
        assert "文件级加密工具" in result.output
        assert "init" in result.output
        assert "encrypt" in result.output
        assert "decrypt" in result.output

    def test_init_help(self, runner):
        """测试init命令帮助"""
        result = runner.invoke(cli, ["init", "--help"])

        assert result.exit_code == 0
        assert "初始化" in result.output

    def test_encrypt_help(self, runner):
        """测试encrypt命令帮助"""
        result = runner.invoke(cli, ["encrypt", "--help"])

        assert result.exit_code == 0
        assert "加密文件" in result.output
        assert "--out" in result.output
        assert "--keep" in result.output

    def test_decrypt_help(self, runner):
        """测试decrypt命令帮助"""
        result = runner.invoke(cli, ["decrypt", "--help"])

        assert result.exit_code == 0
        assert "解密文件" in result.output
        assert "--out" in result.output
