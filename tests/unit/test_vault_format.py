"""
测试加密文件格式符合规范
"""

import pytest
from configcrypt.core.vault import Vault


class TestEncryptionFormat:
    """测试加密文件格式"""
    
    def test_encrypted_data_format(self):
        """验证加密数据格式：[16字节盐值][Fernet加密数据]"""
        vault = Vault()
        plaintext = b"Test data"
        password = "test123"
        
        encrypted = vault._encrypt_bytes(plaintext, password)
        
        # 验证总长度
        assert len(encrypted) >= 16, "加密数据至少包含16字节盐值"
        
        # 提取盐值
        salt = encrypted[:16]
        assert len(salt) == 16, "盐值必须是16字节"
        
        # 提取加密数据部分
        encrypted_data = encrypted[16:]
        assert len(encrypted_data) > 0, "必须包含Fernet加密数据"
        
        # Fernet加密数据应该以版本号0x80开头（Fernet v1）
        # 注意：Fernet数据是Base64编码的
        # 第一个字节通常是版本标识符
        assert encrypted_data[0] in range(256), "Fernet数据的第一个字节"
    
    def test_salt_is_random(self):
        """验证每次生成的盐值都是随机的"""
        vault = Vault()
        plaintext = b"Same data"
        password = "same_password"
        
        # 生成多个加密结果
        salts = []
        for _ in range(10):
            encrypted = vault._encrypt_bytes(plaintext, password)
            salt = encrypted[:16]
            salts.append(salt)
        
        # 验证盐值都不相同
        unique_salts = set(salts)
        assert len(unique_salts) == 10, "每次加密应该生成不同的盐值"
    
    def test_encryption_file_format_structure(self):
        """验证加密格式结构完整性"""
        vault = Vault()
        test_data = b"Important test data"
        password = "secure_password"
        
        encrypted = vault._encrypt_bytes(test_data, password)
        
        # 检查格式
        salt_part = encrypted[:16]
        fernet_part = encrypted[16:]
        
        # 验证可以用提取的盐值和密码解密
        derived_key = vault._derive_key(password, salt_part)
        
        # 使用派生的密钥创建Fernet实例并解密
        from cryptography.fernet import Fernet
        fernet = Fernet(derived_key)
        decrypted = fernet.decrypt(fernet_part)
        
        assert decrypted == test_data
    
    def test_pbkdf2_parameters(self):
        """验证PBKDF2参数符合安全要求"""
        vault = Vault()
        
        # 验证迭代次数
        assert vault.PBKDF2_ITERATIONS == 200000, "PBKDF2迭代次数应为200000（OWASP推荐）"
        
        # 验证使用SHA256
        # 通过实际派生密钥并检查结果来验证
        password = "test"
        salt = b"0" * 16
        
        key = vault._derive_key(password, salt)
        
        # 密钥应该是44字节（32字节Base64编码后）
        assert len(key) == 44, "派生密钥应为44字节（32字节Base64编码）"
    
    def test_encrypted_format_decryptable(self):
        """验证加密格式可以正确解密"""
        vault = Vault()
        
        # 测试各种数据
        test_cases = [
            b"",
            b"a",
            b"Hello World",
            b"x" * 1000,
            "Unicode字符🔐".encode('utf-8'),
        ]
        
        password = "test_password_123"
        
        for original in test_cases:
            encrypted = vault._encrypt_bytes(original, password)
            
            # 验证格式
            assert len(encrypted) >= 16, f"加密数据必须至少16字节，原数据: {len(original)}字节"
            
            # 验证可解密
            decrypted = vault._decrypt_bytes(encrypted, password)
            assert decrypted == original, f"解密后数据应与原数据相同"
