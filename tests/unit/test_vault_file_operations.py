"""
Vault 文件加解密操作测试

测试encrypt_file(), decrypt_file(), decrypt_to_string()方法
"""

import pytest
import tempfile
import os
from pathlib import Path

from configcrypt.core.vault import Vault
from configcrypt.core.exceptions import EncryptionError, DecryptionError, InvalidTokenError


class TestVaultFileEncryption:
    """文件加密功能测试"""

    @pytest.fixture
    def vault(self):
        """创建Vault实例"""
        return Vault()

    @pytest.fixture
    def temp_file(self):
        """创建临时测试文件"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("测试内容\nTest content\n密钥: secret123")
            temp_path = Path(f.name)
        yield temp_path
        # 清理
        if temp_path.exists():
            temp_path.unlink()

    def test_encrypt_file_basic(self, vault, temp_file):
        """测试基本文件加密功能"""
        password = "test_password_123"

        # 加密文件
        encrypted_path = vault.encrypt_file(temp_file, password=password, delete_source=False)

        # 验证加密文件存在
        assert encrypted_path.exists()
        assert encrypted_path == Path(str(temp_file) + ".enc")

        # 验证源文件仍然存在（delete_source=False）
        assert temp_file.exists()

        # 清理
        encrypted_path.unlink()

    def test_encrypt_file_delete_source(self, vault, temp_file):
        """测试加密后删除源文件"""
        password = "test_password_123"

        # 加密文件并删除源文件
        encrypted_path = vault.encrypt_file(temp_file, password=password, delete_source=True)

        # 验证加密文件存在
        assert encrypted_path.exists()

        # 验证源文件已被删除
        assert not temp_file.exists()

        # 清理
        encrypted_path.unlink()

    def test_encrypt_file_custom_output_path(self, vault, temp_file):
        """测试自定义输出路径"""
        password = "test_password_123"
        custom_output = temp_file.parent / "custom_encrypted.bin"

        try:
            # 使用自定义输出路径加密
            encrypted_path = vault.encrypt_file(
                temp_file, output_path=custom_output, password=password, delete_source=False
            )

            # 验证使用了自定义路径
            assert encrypted_path == custom_output
            assert custom_output.exists()
        finally:
            # 清理
            if custom_output.exists():
                custom_output.unlink()

    def test_encrypt_file_not_found(self, vault):
        """测试加密不存在的文件"""
        password = "test_password"
        nonexistent_file = Path("nonexistent_file_12345.txt")

        with pytest.raises(FileNotFoundError):
            vault.encrypt_file(nonexistent_file, password=password)

    def test_encrypt_file_output_exists(self, vault, temp_file):
        """测试输出文件已存在时抛出异常"""
        password = "test_password"

        # 创建一个已存在的输出文件
        output_path = Path(str(temp_file) + ".enc")
        output_path.touch()

        try:
            with pytest.raises(EncryptionError, match="输出文件已存在"):
                vault.encrypt_file(temp_file, password=password, delete_source=False)
        finally:
            # 清理
            if output_path.exists():
                output_path.unlink()

    def test_encrypt_large_file(self, vault):
        """测试加密大文件（模拟100MB）"""
        password = "test_password"

        # 创建一个较大的测试文件（简化版，使用1MB代替100MB以加快测试）
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # 写入1MB数据
            f.write(b"X" * (1024 * 1024))
            large_file = Path(f.name)

        try:
            # 加密大文件
            encrypted_path = vault.encrypt_file(large_file, password=password, delete_source=False)

            # 验证加密成功
            assert encrypted_path.exists()
            assert encrypted_path.stat().st_size > 0

        finally:
            # 清理
            if large_file.exists():
                large_file.unlink()
            if encrypted_path.exists():
                encrypted_path.unlink()


class TestVaultFileDecryption:
    """文件解密功能测试"""

    @pytest.fixture
    def vault(self):
        """创建Vault实例"""
        return Vault()

    @pytest.fixture
    def encrypted_file(self, vault):
        """创建加密的测试文件"""
        # 创建临时明文文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("测试内容\nTest content")
            temp_path = Path(f.name)

        # 加密文件
        password = "test_password_123"
        encrypted_path = vault.encrypt_file(temp_path, password=password, delete_source=True)

        yield encrypted_path, password

        # 清理
        if encrypted_path.exists():
            encrypted_path.unlink()

    def test_decrypt_file_basic(self, vault, encrypted_file):
        """测试基本文件解密功能"""
        encrypted_path, password = encrypted_file

        # 解密文件
        decrypted_path = vault.decrypt_file(encrypted_path, password=password)

        # 验证解密文件存在
        assert decrypted_path.exists()
        # 验证文件不为空
        assert decrypted_path.stat().st_size > 0

        # 清理
        decrypted_path.unlink()

    def test_decrypt_file_removes_enc_extension(self, vault, encrypted_file):
        """测试解密自动移除.enc扩展名"""
        encrypted_path, password = encrypted_file

        # 解密文件
        decrypted_path = vault.decrypt_file(encrypted_path, password=password)

        # 验证移除了.enc扩展名
        assert decrypted_path.suffix != ".enc"
        assert not str(decrypted_path).endswith(".enc")

        # 清理
        decrypted_path.unlink()

    def test_decrypt_file_custom_output_path(self, vault, encrypted_file):
        """测试自定义输出路径"""
        encrypted_path, password = encrypted_file
        custom_output = encrypted_path.parent / "custom_decrypted.txt"

        try:
            # 使用自定义输出路径解密
            decrypted_path = vault.decrypt_file(
                encrypted_path, output_path=custom_output, password=password
            )

            # 验证使用了自定义路径
            assert decrypted_path == custom_output
            assert custom_output.exists()
        finally:
            # 清理
            if custom_output.exists():
                custom_output.unlink()

    def test_decrypt_file_wrong_password(self, vault, encrypted_file):
        """测试错误密码抛出InvalidTokenError"""
        encrypted_path, _ = encrypted_file
        wrong_password = "wrong_password"

        with pytest.raises(InvalidTokenError):
            vault.decrypt_file(encrypted_path, password=wrong_password)

    def test_decrypt_file_not_found(self, vault):
        """测试解密不存在的文件"""
        password = "test_password"
        nonexistent_file = Path("nonexistent_encrypted_12345.enc")

        with pytest.raises(FileNotFoundError):
            vault.decrypt_file(nonexistent_file, password=password)

    def test_decrypt_file_output_exists(self, vault, encrypted_file):
        """测试输出文件已存在时抛出异常"""
        encrypted_path, password = encrypted_file

        # 创建已存在的输出文件
        output_path = encrypted_path.with_suffix("")
        output_path.touch()

        try:
            with pytest.raises(DecryptionError, match="输出文件已存在"):
                vault.decrypt_file(encrypted_path, password=password)
        finally:
            # 清理
            if output_path.exists():
                output_path.unlink()


class TestVaultDecryptToString:
    """decrypt_to_string方法测试"""

    @pytest.fixture
    def vault(self):
        """创建Vault实例"""
        return Vault()

    @pytest.fixture
    def encrypted_file(self, vault):
        """创建加密的测试文件"""
        # 创建临时明文文件
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="utf-8"
        ) as f:
            f.write("测试内容\nTest content\n密钥: secret123")
            temp_path = Path(f.name)

        # 加密文件
        password = "test_password_123"
        encrypted_path = vault.encrypt_file(temp_path, password=password, delete_source=True)

        yield encrypted_path, password

        # 清理
        if encrypted_path.exists():
            encrypted_path.unlink()

    def test_decrypt_to_string_basic(self, vault, encrypted_file):
        """测试decrypt_to_string基本功能"""
        encrypted_path, password = encrypted_file

        # 解密为字符串
        content = vault.decrypt_to_string(encrypted_path, password=password)

        # 验证内容
        assert isinstance(content, str)
        assert "测试内容" in content
        assert "Test content" in content
        assert "密钥: secret123" in content

    def test_decrypt_to_string_no_file_created(self, vault, encrypted_file):
        """测试decrypt_to_string不创建文件"""
        encrypted_path, password = encrypted_file

        # 记录目录中的文件数
        parent_dir = encrypted_path.parent
        files_before = set(parent_dir.iterdir())

        # 解密为字符串
        vault.decrypt_to_string(encrypted_path, password=password)

        # 验证没有新文件创建
        files_after = set(parent_dir.iterdir())
        assert files_before == files_after

    def test_decrypt_to_string_wrong_password(self, vault, encrypted_file):
        """测试decrypt_to_string使用错误密码"""
        encrypted_path, _ = encrypted_file
        wrong_password = "wrong_password"

        with pytest.raises(InvalidTokenError):
            vault.decrypt_to_string(encrypted_path, password=wrong_password)

    def test_decrypt_to_string_not_found(self, vault):
        """测试decrypt_to_string文件不存在"""
        password = "test_password"
        nonexistent_file = Path("nonexistent_12345.enc")

        with pytest.raises(FileNotFoundError):
            vault.decrypt_to_string(nonexistent_file, password=password)


class TestVaultRoundTrip:
    """加密解密往返测试"""

    @pytest.fixture
    def vault(self):
        """创建Vault实例"""
        return Vault()

    def test_encrypt_decrypt_round_trip(self, vault):
        """测试加密解密往返一致性"""
        password = "test_password_123"
        original_content = "原始内容\nOriginal content\n特殊字符: @#$%^&*()"

        # 创建临时文件（使用binary模式避免换行符转换）
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(original_content.encode("utf-8"))
            original_path = Path(f.name)

        encrypted_path = None
        decrypted_path = None
        try:
            # 加密（删除源文件以避免路径冲突）
            encrypted_path = vault.encrypt_file(
                original_path, password=password, delete_source=True
            )

            # 解密
            decrypted_path = vault.decrypt_file(encrypted_path, password=password)

            # 验证内容一致（使用bytes比较，避免换行符问题）
            decrypted_bytes = decrypted_path.read_bytes()
            original_bytes = original_content.encode("utf-8")
            assert decrypted_bytes == original_bytes

        finally:
            # 清理
            if original_path.exists():
                original_path.unlink()
            if encrypted_path and encrypted_path.exists():
                encrypted_path.unlink()
            if decrypted_path and decrypted_path.exists():
                decrypted_path.unlink()

    def test_multiple_encrypt_decrypt_cycles(self, vault):
        """测试多次加密解密循环"""
        password = "test_password"
        original_content = "循环测试内容"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write(original_content)
            temp_path = Path(f.name)

        try:
            current_path = temp_path

            # 执行3次加密-解密循环
            for i in range(3):
                # 加密
                encrypted_path = vault.encrypt_file(
                    current_path, password=password, delete_source=True
                )

                # 解密
                decrypted_path = vault.decrypt_file(encrypted_path, password=password)

                # 验证内容
                content = decrypted_path.read_text(encoding="utf-8")
                assert content == original_content

                # 清理加密文件
                if encrypted_path.exists():
                    encrypted_path.unlink()

                current_path = decrypted_path

        finally:
            # 最终清理
            if current_path.exists():
                current_path.unlink()


class TestVaultFileOperationsEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def vault(self):
        return Vault()

    def test_empty_file_encryption(self, vault):
        """测试加密空文件"""
        password = "test_password"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            # 创建空文件
            pass
        empty_file = Path(f.name)

        encrypted_path = None
        decrypted_path = None
        try:
            # 加密空文件（删除源文件以避免路径冲突）
            encrypted_path = vault.encrypt_file(empty_file, password=password, delete_source=True)

            # 解密
            decrypted_path = vault.decrypt_file(encrypted_path, password=password)

            # 验证解密文件也是空的
            assert decrypted_path.stat().st_size == 0

        finally:
            # 清理
            if empty_file.exists():
                empty_file.unlink()
            if encrypted_path and encrypted_path.exists():
                encrypted_path.unlink()
            if decrypted_path and decrypted_path.exists():
                decrypted_path.unlink()

    def test_unicode_filename(self, vault):
        """测试Unicode文件名"""
        password = "test_password"

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix="_测试文件_🔐.txt", encoding="utf-8"
        ) as f:
            f.write("Unicode文件名测试")
            unicode_file = Path(f.name)

        try:
            # 加密
            encrypted_path = vault.encrypt_file(
                unicode_file, password=password, delete_source=False
            )

            # 验证加密成功
            assert encrypted_path.exists()

        finally:
            # 清理
            if unicode_file.exists():
                unicode_file.unlink()
            if encrypted_path.exists():
                encrypted_path.unlink()

    def test_binary_content_preservation(self, vault):
        """测试二进制内容保持一致"""
        password = "test_password"

        # 创建包含二进制数据的文件
        binary_data = bytes(range(256))  # 0-255所有字节值

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(binary_data)
            binary_file = Path(f.name)

        encrypted_path = None
        decrypted_path = None
        try:
            # 加密（删除源文件以避免路径冲突）
            encrypted_path = vault.encrypt_file(binary_file, password=password, delete_source=True)

            # 解密
            decrypted_path = vault.decrypt_file(encrypted_path, password=password)

            # 验证二进制内容完全一致
            decrypted_data = decrypted_path.read_bytes()
            assert decrypted_data == binary_data

        finally:
            # 清理
            if binary_file.exists():
                binary_file.unlink()
            if encrypted_path and encrypted_path.exists():
                encrypted_path.unlink()
            if decrypted_path and decrypted_path.exists():
                decrypted_path.unlink()
