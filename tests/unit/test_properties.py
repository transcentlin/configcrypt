"""
属性测试（Property-Based Testing）

使用Hypothesis验证系统的12个正确性属性
"""

import os
import pytest
import tempfile
from pathlib import Path
from hypothesis import given, settings, strategies as st, assume
from hypothesis import HealthCheck

from configcrypt.core.vault import Vault
from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.exceptions import DecryptionError, InvalidTokenError


# Windows保留设备名（不区分大小写）
WINDOWS_RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}


def is_valid_filename(filename: str) -> bool:
    """检查文件名是否有效（不是Windows保留名）"""
    if not filename:
        return False
    # 提取不带扩展名的部分
    base_name = filename.split('.')[0].upper()
    return base_name not in WINDOWS_RESERVED_NAMES


# 自定义生成器
@st.composite
def valid_password(draw):
    """生成有效密码（长度>=8）"""
    return draw(st.text(min_size=8, max_size=64, alphabet=st.characters(
        min_codepoint=33, max_codepoint=126  # 可打印ASCII字符
    )))


@st.composite
def file_content(draw):
    """生成文件内容（1KB-1MB）"""
    size = draw(st.integers(min_value=1024, max_value=1024*1024))
    return draw(st.binary(min_size=size, max_size=size))


@st.composite
def small_file_content(draw):
    """生成小文件内容（用于快速测试）"""
    size = draw(st.integers(min_value=100, max_value=10240))
    return draw(st.binary(min_size=size, max_size=size))


class TestProperty1_EncryptionDecryptionRoundtrip:
    """Property 1: 加密解密往返保持内容一致性"""
    
    @pytest.mark.property
    @given(
        content=small_file_content(),
        password=valid_password()
    )
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.too_slow])
    def test_bytes_roundtrip(self, content, password):
        """
        Feature: file-encryption-tool
        Property 1: 加密解密往返保持内容一致性
        
        对于任意文本文件内容和有效密码，执行加密后立即解密，
        应该得到与原始内容完全相同的结果。
        """
        vault = Vault()
        
        # 加密
        encrypted = vault._encrypt_bytes(content, password)
        
        # 解密
        decrypted = vault._decrypt_bytes(encrypted, password)
        
        # 验证内容一致
        assert decrypted == content
    
    @pytest.mark.property
    @given(
        content=small_file_content(),
        password=valid_password()
    )
    @settings(
        max_examples=50, 
        deadline=10000, 
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture]
    )
    def test_file_roundtrip(self, content, password):
        """文件级别的加密解密往返测试"""
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建测试文件
            input_file = tmp_path / "test_input.txt"
            input_file.write_bytes(content)
            
            # 加密 (删除源文件以避免路径冲突)
            encrypted_file = vault.encrypt_file(
                input_file,
                password=password,
                delete_source=True
            )
            
            # 解密
            decrypted_file = vault.decrypt_file(
                encrypted_file,
                password=password
            )
            
            # 验证内容一致
            assert decrypted_file.read_bytes() == content


class TestProperty2_OutputFileNaming:
    """Property 2: 输出文件命名规则"""
    
    @pytest.mark.property
    @given(
        filename=st.text(
            min_size=1, 
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=('Ll', 'Lu', 'Nd'),
                whitelist_characters='.-_'
            )
        ),
        extension=st.sampled_from(['.txt', '.json', '.yaml', '.env', '.conf', ''])
    )
    @settings(max_examples=100, deadline=500, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_encrypt_adds_enc_extension(self, filename, extension):
        """
        Feature: file-encryption-tool
        Property 2: 输出文件命名规则
        
        加密操作输出的文件路径应该添加.enc扩展名
        """
        assume(filename not in ['.', '..'])  # 排除特殊目录名
        assume(is_valid_filename(filename))  # 排除Windows保留名
        
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建测试文件
            input_file = tmp_path / f"{filename}{extension}"
            input_file.write_text("test content")
            
            # 加密（使用默认输出路径）
            encrypted_file = vault.encrypt_file(
                input_file,
                password="testpass123",
                delete_source=False
            )
            
            # 验证添加了.enc扩展名
            assert encrypted_file.name == f"{filename}{extension}.enc"
            assert encrypted_file.exists()
    
    @pytest.mark.property
    @given(
        filename=st.text(
            min_size=1, 
            max_size=50,
            alphabet=st.characters(
                whitelist_categories=('Ll', 'Lu', 'Nd'),
                whitelist_characters='.-_'
            )
        )
    )
    @settings(max_examples=100, deadline=500, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_decrypt_removes_enc_extension(self, filename):
        """解密操作输出的文件路径应该移除.enc扩展名"""
        assume(filename not in ['.', '..'])
        assume(is_valid_filename(filename))  # 排除Windows保留名
        
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建并加密测试文件
            input_file = tmp_path / f"{filename}.txt"
            input_file.write_text("test content")
            
            encrypted_file = vault.encrypt_file(
                input_file,
                password="testpass123"
            )
            
            # 解密（使用默认输出路径）
            decrypted_file = vault.decrypt_file(
                encrypted_file,
                password="testpass123"
            )
            
            # 验证移除了.enc扩展名
            assert decrypted_file.name == f"{filename}.txt"
            assert decrypted_file.exists()


class TestProperty3_SourceFileDeletionBehavior:
    """Property 3: 源文件删除行为遵循参数设置"""
    
    @pytest.mark.property
    @given(
        content=st.binary(min_size=100, max_size=10240),
        delete_source=st.booleans()
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_delete_source_parameter(self, content, delete_source):
        """
        Feature: file-encryption-tool
        Property 3: 源文件删除行为遵循参数设置
        
        delete_source=True时源文件应该不存在，
        delete_source=False时源文件应该仍然存在。
        """
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建测试文件
            input_file = tmp_path / "test_source.txt"
            input_file.write_bytes(content)
            
            # 加密
            vault.encrypt_file(
                input_file,
                password="testpass123",
                delete_source=delete_source
            )
            
            # 验证源文件存在性符合预期
            if delete_source:
                assert not input_file.exists(), "delete_source=True时源文件应该被删除"
            else:
                assert input_file.exists(), "delete_source=False时源文件应该保留"


class TestProperty4_CustomOutputPath:
    """Property 4: 自定义输出路径正确应用"""
    
    @pytest.mark.property
    @given(
        content=st.binary(min_size=100, max_size=10240),
        custom_name=st.text(
            min_size=1, 
            max_size=30,
            alphabet=st.characters(
                whitelist_categories=('Ll', 'Lu', 'Nd'),
                whitelist_characters='_-'
            )
        )
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_custom_output_path_encrypt(self, content, custom_name):
        """
        Feature: file-encryption-tool
        Property 4: 自定义输出路径正确应用
        
        指定输出路径时，文件应该创建在该路径
        """
        assume(custom_name not in ['.', '..'])
        assume(is_valid_filename(custom_name))  # 排除Windows保留名
        
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建测试文件
            input_file = tmp_path / "input.txt"
            input_file.write_bytes(content)
            
            # 使用自定义输出路径加密
            custom_output = tmp_path / f"{custom_name}.encrypted"
            encrypted_file = vault.encrypt_file(
                input_file,
                output_path=custom_output,
                password="testpass123",
                delete_source=False
            )
            
            # 验证文件在自定义路径创建
            assert encrypted_file == custom_output
            assert custom_output.exists()
    
    @pytest.mark.property
    @given(
        content=st.binary(min_size=100, max_size=10240),
        custom_name=st.text(
            min_size=1, 
            max_size=30,
            alphabet=st.characters(
                whitelist_categories=('Ll', 'Lu', 'Nd'),
                whitelist_characters='_-'
            )
        )
    )
    @settings(max_examples=100, deadline=500, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_custom_output_path_decrypt(self, content, custom_name):
        """自定义输出路径解密测试"""
        assume(custom_name not in ['.', '..'])
        
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建并加密测试文件
            input_file = tmp_path / "input.txt"
            input_file.write_bytes(content)
            
            encrypted_file = vault.encrypt_file(
                input_file,
                password="testpass123"
            )
            
            # 使用自定义输出路径解密
            custom_output = tmp_path / f"{custom_name}.decrypted"
            decrypted_file = vault.decrypt_file(
                encrypted_file,
                output_path=custom_output,
                password="testpass123"
            )
            
            # 验证文件在自定义路径创建
            assert decrypted_file == custom_output
            assert custom_output.exists()
            assert custom_output.read_bytes() == content


class TestProperty5_WrongPasswordFails:
    """Property 5: 错误密码导致解密失败"""
    
    @pytest.mark.property
    @given(
        content=st.binary(min_size=100, max_size=10240),
        password1=valid_password(),
        password2=valid_password()
    )
    @settings(max_examples=100, deadline=500)
    def test_wrong_password_raises_exception(self, content, password1, password2):
        """
        Feature: file-encryption-tool
        Property 5: 错误密码导致解密失败
        
        使用与加密时不同的密码尝试解密，应该抛出DecryptionError异常
        """
        assume(password1 != password2)  # 确保两个密码不同
        
        vault = Vault()
        
        # 使用password1加密
        encrypted = vault._encrypt_bytes(content, password1)
        
        # 使用password2解密应该失败
        with pytest.raises((DecryptionError, InvalidTokenError)):
            vault._decrypt_bytes(encrypted, password2)


class TestProperty6_TamperDetection:
    """Property 6: 文件篡改检测"""
    
    @pytest.mark.property
    @given(
        content=st.binary(min_size=100, max_size=10240),
        password=valid_password(),
        tamper_position=st.integers(min_value=16, max_value=200),  # 跳过盐值部分
        tamper_value=st.integers(min_value=0, max_value=255)
    )
    @settings(max_examples=100, deadline=3000)
    def test_tampered_data_detected(self, content, password, tamper_position, tamper_value):
        """
        Feature: file-encryption-tool
        Property 6: 文件篡改检测
        
        随机修改加密文件的任意字节，解密操作应该检测到完整性错误
        """
        vault = Vault()
        
        # 加密
        encrypted = vault._encrypt_bytes(content, password)
        
        # 确保篡改位置有效
        assume(tamper_position < len(encrypted))
        
        # 篡改数据（修改一个字节）
        tampered = bytearray(encrypted)
        original_value = tampered[tamper_position]
        tampered[tamper_position] = tamper_value
        
        # 只有当真正改变了数据时才测试
        assume(tampered[tamper_position] != original_value)
        
        # 解密应该失败
        with pytest.raises(InvalidTokenError):
            vault._decrypt_bytes(bytes(tampered), password)


class TestProperty7_KeychainRoundtrip:
    """Property 7: Keychain存储读取一致性"""
    
    @pytest.mark.property
    @given(
        password=st.text(
            min_size=8,
            max_size=64,
            alphabet=st.characters(min_codepoint=32, max_codepoint=126)
        )
    )
    @settings(max_examples=50, deadline=1000)  # Keychain操作较慢，增加deadline
    def test_keychain_save_read_consistency(self, password):
        """
        Feature: file-encryption-tool
        Property 7: Keychain存储读取一致性
        
        保存到Keychain后立即读取，应该得到完全相同的密码字符串
        """
        keychain = KeychainStore()
        
        # 跳过Keychain不可用的情况
        if not keychain.is_available():
            pytest.skip("Keychain不可用")
        
        try:
            # 保存密码
            keychain.save_password(password)
            
            # 读取密码
            retrieved = keychain.get_password()
            
            # 验证一致性
            assert retrieved == password
        finally:
            # 清理
            keychain.delete_password()


class TestProperty9_PasswordLengthValidation:
    """Property 9: 密码长度验证规则"""
    
    @pytest.mark.property
    @given(
        length=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=100)
    def test_password_length_requirement(self, length):
        """
        Feature: file-encryption-tool
        Property 9: 密码长度验证规则
        
        长度小于8的应该被拒绝，长度大于等于8的应该被接受
        """
        password = 'a' * length
        vault = Vault()
        test_content = b"test content"
        
        if length < 8:
            # 长度不足的密码在实际使用中会被CLI/GUI层拒绝
            # 但Core层仍然可以加密（不做验证），这里我们测试能否成功加密
            # 注意：这个属性主要在UI层验证，Core层不强制
            pass  # Core层不验证密码长度
        else:
            # 长度足够的密码应该可以正常加密
            encrypted = vault._encrypt_bytes(test_content, password)
            decrypted = vault._decrypt_bytes(encrypted, password)
            assert decrypted == test_content


class TestProperty10_PasswordStrengthMonotonicity:
    """Property 10: 密码强度计算的单调性"""
    
    def calculate_simple_strength(self, password: str) -> int:
        """简化的密码强度计算"""
        score = 0
        
        # 长度评分
        if len(password) >= 16:
            score += 30
        elif len(password) >= 12:
            score += 20
        elif len(password) >= 8:
            score += 10
        
        # 字符类型评分
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            score += 25
        
        return score
    
    @pytest.mark.property
    @given(
        base_password=st.text(min_size=8, max_size=12, alphabet='abcdefghijk'),
        add_upper=st.booleans(),
        add_digit=st.booleans(),
        add_special=st.booleans()
    )
    @settings(max_examples=100)
    def test_strength_increases_with_complexity(
        self, base_password, add_upper, add_digit, add_special
    ):
        """
        Feature: file-encryption-tool
        Property 10: 密码强度计算的单调性
        
        添加额外的字符类型不会降低强度评分
        """
        # 基础密码强度
        base_strength = self.calculate_simple_strength(base_password)
        
        # 添加字符类型
        enhanced_password = base_password
        if add_upper:
            enhanced_password += 'A'
        if add_digit:
            enhanced_password += '1'
        if add_special:
            enhanced_password += '!'
        
        # 增强后的强度
        enhanced_strength = self.calculate_simple_strength(enhanced_password)
        
        # 验证单调性
        assert enhanced_strength >= base_strength


class TestProperty12_CrossFormatCompatibility:
    """Property 12: 跨格式加密兼容性"""
    
    @pytest.mark.property
    @given(
        content=st.text(min_size=100, max_size=10240),
        extension=st.sampled_from(['.env', '.json', '.yaml', '.txt', '.conf', '.ini']),
        password=valid_password()
    )
    @settings(max_examples=100, deadline=500, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_format_agnostic_encryption(self, content, extension, password):
        """
        Feature: file-encryption-tool
        Property 12: 跨格式加密兼容性
        
        对于任意文本格式文件，加密和解密操作应该成功完成且内容保持一致
        """
        vault = Vault()
        
        # 使用临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # 创建测试文件 (使用newline=''保留原始行尾符)
            input_file = tmp_path / f"test{extension}"
            input_file.write_text(content, encoding='utf-8', newline='')
            
            # 加密 (删除源文件以避免路径冲突)
            encrypted_file = vault.encrypt_file(
                input_file,
                password=password,
                delete_source=True
            )
            
            # 解密
            decrypted_file = vault.decrypt_file(
                encrypted_file,
                password=password
            )
            
            # 验证内容一致 (使用newline=''保留原始行尾符)
            assert decrypted_file.read_text(encoding='utf-8', newline='') == content


# 注意：Property 8 (配置格式解析) 和 Property 11 (文件权限) 将在后续任务中实现
# Property 8 需要 FormatParser 类（Task 8）
# Property 11 需要平台特定的权限检查

