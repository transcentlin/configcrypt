"""
Vault 加密引擎单元测试

测试Vault类的核心加密解密功能
"""

import pytest
from configcrypt.core.vault import Vault
from configcrypt.core.exceptions import (
    EncryptionError,
    DecryptionError,
    InvalidTokenError,
)


class TestVaultKeyDerivation:
    """测试密钥派生功能"""
    
    def test_derive_key_basic(self):
        """测试基本的密钥派生"""
        vault = Vault()
        password = "test_password_123"
        salt = b"1234567890123456"  # 16字节盐值
        
        key = vault._derive_key(password, salt)
        
        # 验证密钥长度（Base64编码后的32字节密钥应该是44字节）
        assert len(key) == 44
        assert isinstance(key, bytes)
    
    def test_derive_key_deterministic(self):
        """测试相同密码和盐值生成相同密钥"""
        vault = Vault()
        password = "test_password_123"
        salt = b"1234567890123456"
        
        key1 = vault._derive_key(password, salt)
        key2 = vault._derive_key(password, salt)
        
        assert key1 == key2
    
    def test_derive_key_different_passwords(self):
        """测试不同密码生成不同密钥"""
        vault = Vault()
        salt = b"1234567890123456"
        
        key1 = vault._derive_key("password1", salt)
        key2 = vault._derive_key("password2", salt)
        
        assert key1 != key2
    
    def test_derive_key_different_salts(self):
        """测试不同盐值生成不同密钥"""
        vault = Vault()
        password = "test_password_123"
        
        key1 = vault._derive_key(password, b"1234567890123456")
        key2 = vault._derive_key(password, b"6543210987654321")
        
        assert key1 != key2
    
    def test_derive_key_unicode_password(self):
        """测试Unicode密码"""
        vault = Vault()
        password = "密码测试_🔐_αβγ"
        salt = b"1234567890123456"
        
        key = vault._derive_key(password, salt)
        
        assert len(key) == 44
        assert isinstance(key, bytes)


class TestVaultEncryption:
    """测试加密功能"""
    
    def test_encrypt_bytes_basic(self):
        """测试基本的字节加密"""
        vault = Vault()
        plaintext = b"Hello, World!"
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 验证加密后数据格式：16字节盐值 + Fernet加密数据
        assert len(encrypted) > 16
        assert isinstance(encrypted, bytes)
        # 验证前16字节是盐值（应该与明文不同）
        assert encrypted[:16] != plaintext[:16]
    
    def test_encrypt_bytes_empty(self):
        """测试加密空数据"""
        vault = Vault()
        plaintext = b""
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 即使是空数据，也应该有盐值和Fernet结构
        assert len(encrypted) > 16
    
    def test_encrypt_bytes_large_data(self):
        """测试加密大数据"""
        vault = Vault()
        # 1MB数据
        plaintext = b"A" * (1024 * 1024)
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        assert len(encrypted) > len(plaintext)
        assert isinstance(encrypted, bytes)
    
    def test_encrypt_bytes_random_salt(self):
        """测试每次加密生成不同的盐值"""
        vault = Vault()
        plaintext = b"Same plaintext"
        password = "same_password"
        
        encrypted1 = vault._encrypt_bytes(plaintext, password)
        encrypted2 = vault._encrypt_bytes(plaintext, password)
        
        # 盐值应该不同
        salt1 = encrypted1[:16]
        salt2 = encrypted2[:16]
        assert salt1 != salt2
        
        # 整体加密结果也应该不同
        assert encrypted1 != encrypted2
    
    def test_encrypt_bytes_unicode_content(self):
        """测试加密Unicode内容"""
        vault = Vault()
        plaintext = "你好，世界！🌍".encode('utf-8')
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        assert len(encrypted) > 16
        assert isinstance(encrypted, bytes)


class TestVaultDecryption:
    """测试解密功能"""
    
    def test_decrypt_bytes_basic(self):
        """测试基本的字节解密"""
        vault = Vault()
        plaintext = b"Hello, World!"
        password = "test_password"
        
        # 先加密
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 再解密
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == plaintext
    
    def test_decrypt_bytes_empty(self):
        """测试解密空数据"""
        vault = Vault()
        plaintext = b""
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == plaintext
    
    def test_decrypt_bytes_large_data(self):
        """测试解密大数据"""
        vault = Vault()
        # 1MB数据
        plaintext = b"B" * (1024 * 1024)
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == plaintext
    
    def test_decrypt_bytes_wrong_password(self):
        """测试错误密码解密失败"""
        vault = Vault()
        plaintext = b"Secret data"
        password = "correct_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 使用错误密码解密
        with pytest.raises(InvalidTokenError) as exc_info:
            vault._decrypt_bytes(encrypted, "wrong_password")
        
        assert "密码错误或文件已损坏" in str(exc_info.value)
    
    def test_decrypt_bytes_corrupted_data(self):
        """测试解密被篡改的数据"""
        vault = Vault()
        plaintext = b"Important data"
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 篡改加密数据（修改中间的一个字节）
        corrupted = bytearray(encrypted)
        corrupted[20] ^= 0xFF  # 翻转一个字节
        corrupted = bytes(corrupted)
        
        # 解密应该失败
        with pytest.raises(InvalidTokenError) as exc_info:
            vault._decrypt_bytes(corrupted, password)
        
        assert "密码错误或文件已损坏" in str(exc_info.value)
    
    def test_decrypt_bytes_corrupted_salt(self):
        """测试盐值被篡改的情况"""
        vault = Vault()
        plaintext = b"Test data"
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 篡改盐值
        corrupted = bytearray(encrypted)
        corrupted[0] ^= 0xFF  # 修改盐值的第一个字节
        corrupted = bytes(corrupted)
        
        # 解密应该失败（因为密钥派生会不同）
        with pytest.raises(InvalidTokenError):
            vault._decrypt_bytes(corrupted, password)
    
    def test_decrypt_bytes_invalid_length(self):
        """测试解密长度不足的数据"""
        vault = Vault()
        
        # 创建一个少于16字节的数据
        invalid_data = b"short"
        
        with pytest.raises(DecryptionError) as exc_info:
            vault._decrypt_bytes(invalid_data, "any_password")
        
        assert "文件太小" in str(exc_info.value)
    
    def test_decrypt_bytes_unicode_content(self):
        """测试解密Unicode内容"""
        vault = Vault()
        plaintext = "测试数据_αβγδ_🔒".encode('utf-8')
        password = "test_password"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == plaintext
        assert decrypted.decode('utf-8') == "测试数据_αβγδ_🔒"


class TestVaultRoundTrip:
    """测试加密解密往返一致性"""
    
    def test_roundtrip_basic(self):
        """测试基本的加密解密往返"""
        vault = Vault()
        original = b"Original data"
        password = "test123"
        
        encrypted = vault._encrypt_bytes(original, password)
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == original
    
    def test_roundtrip_multiple_times(self):
        """测试多次往返"""
        vault = Vault()
        original = b"Test data for multiple rounds"
        password = "secure_password"
        
        # 第一次往返
        encrypted1 = vault._encrypt_bytes(original, password)
        decrypted1 = vault._decrypt_bytes(encrypted1, password)
        assert decrypted1 == original
        
        # 第二次往返（使用解密后的数据）
        encrypted2 = vault._encrypt_bytes(decrypted1, password)
        decrypted2 = vault._decrypt_bytes(encrypted2, password)
        assert decrypted2 == original
    
    def test_roundtrip_various_data_sizes(self):
        """测试不同数据大小的往返"""
        vault = Vault()
        password = "test_password"
        
        test_sizes = [0, 1, 100, 1024, 10240, 102400]  # 从0字节到100KB
        
        for size in test_sizes:
            original = b"X" * size
            encrypted = vault._encrypt_bytes(original, password)
            decrypted = vault._decrypt_bytes(encrypted, password)
            assert decrypted == original, f"Failed for size {size}"
    
    def test_roundtrip_binary_data(self):
        """测试二进制数据往返"""
        vault = Vault()
        # 创建包含所有字节值的数据
        original = bytes(range(256))
        password = "binary_test"
        
        encrypted = vault._encrypt_bytes(original, password)
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        assert decrypted == original


class TestVaultConstants:
    """测试Vault常量配置"""
    
    def test_pbkdf2_iterations(self):
        """测试PBKDF2迭代次数符合安全要求"""
        vault = Vault()
        assert vault.PBKDF2_ITERATIONS == 200000
    
    def test_salt_size(self):
        """测试盐值大小"""
        vault = Vault()
        assert vault.SALT_SIZE == 16
    
    def test_key_size(self):
        """测试密钥大小"""
        vault = Vault()
        assert vault.KEY_SIZE == 32


class TestVaultExceptions:
    """测试异常类型"""
    
    def test_exception_inheritance(self):
        """测试异常继承关系"""
        from configcrypt.core.exceptions import KeyVaultError
        
        # InvalidTokenError应该是DecryptionError的子类
        assert issubclass(InvalidTokenError, DecryptionError)
        # DecryptionError应该是KeyVaultError的子类
        assert issubclass(DecryptionError, KeyVaultError)
        # EncryptionError应该是KeyVaultError的子类
        assert issubclass(EncryptionError, KeyVaultError)
    
    def test_wrong_password_raises_invalid_token(self):
        """测试错误密码抛出InvalidTokenError"""
        vault = Vault()
        encrypted = vault._encrypt_bytes(b"data", "correct")
        
        with pytest.raises(InvalidTokenError):
            vault._decrypt_bytes(encrypted, "wrong")
    
    def test_tampered_data_raises_invalid_token(self):
        """测试篡改数据抛出InvalidTokenError"""
        vault = Vault()
        encrypted = vault._encrypt_bytes(b"data", "password")
        
        # 篡改数据
        tampered = bytearray(encrypted)
        tampered[-1] ^= 0xFF
        
        with pytest.raises(InvalidTokenError):
            vault._decrypt_bytes(bytes(tampered), "password")



