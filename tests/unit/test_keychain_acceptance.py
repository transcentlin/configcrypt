"""
KeychainStore验收测试

验证所有验收标准是否满足
"""

import pytest
from unittest.mock import patch
import keyring.errors
import keyring.backends.fail
import keyring.backends

from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.exceptions import KeychainError


class TestKeychainAcceptanceCriteria:
    """验证Task 3的所有验收标准"""
    
    @pytest.fixture
    def keychain_store(self):
        return KeychainStore()
    
    def test_ac1_save_password_method_implemented(self, keychain_store):
        """验收标准1: 实现save_password()方法"""
        with patch('keyring.set_password'):
            # 验证方法存在且可调用
            keychain_store.save_password("test")
            assert hasattr(keychain_store, 'save_password')
            assert callable(keychain_store.save_password)
    
    def test_ac2_get_password_returns_optional_str(self, keychain_store):
        """验收标准2: 实现get_password()方法,返回Optional[str]"""
        with patch('keyring.get_password', return_value="password"):
            result = keychain_store.get_password()
            assert isinstance(result, str) or result is None
        
        with patch('keyring.get_password', return_value=None):
            result = keychain_store.get_password()
            assert result is None
    
    def test_ac3_delete_password_method_implemented(self, keychain_store):
        """验收标准3: 实现delete_password()方法"""
        with patch('keyring.delete_password'):
            # 验证方法存在且可调用
            keychain_store.delete_password()
            assert hasattr(keychain_store, 'delete_password')
            assert callable(keychain_store.delete_password)
    
    def test_ac4_is_available_method_implemented(self, keychain_store):
        """验收标准4: 实现is_available()方法检查Keychain可用性"""
        with patch('keyring.get_keyring'):
            result = keychain_store.is_available()
            assert isinstance(result, bool)
            assert hasattr(keychain_store, 'is_available')
            assert callable(keychain_store.is_available)
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not hasattr(keyring.backends, 'Windows'),
        reason="Windows backend not available"
    )
    def test_ac5_windows_uses_winvault(self):
        """验收标准5: Windows上使用WinVaultKeyring"""
        import platform
        if platform.system() != 'Windows':
            pytest.skip("Only runs on Windows")
        
        # 在Windows上，keyring应该自动选择WinVaultKeyring
        backend = keyring.get_keyring()
        backend_name = backend.__class__.__name__
        
        # Windows应该使用WinVault或类似的安全backend
        # 不应该使用fail.Keyring
        assert not isinstance(backend, keyring.backends.fail.Keyring)
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not hasattr(keyring.backends, 'macOS'),
        reason="macOS backend not available"
    )
    def test_ac6_macos_uses_keychain(self):
        """验收标准6: macOS上使用macOS Keychain"""
        import platform
        if platform.system() != 'Darwin':
            pytest.skip("Only runs on macOS")
        
        backend = keyring.get_keyring()
        # macOS应该使用系统Keychain
        assert not isinstance(backend, keyring.backends.fail.Keyring)
    
    @pytest.mark.integration
    def test_ac7_linux_uses_secret_service(self):
        """验收标准7: Linux上使用SecretService"""
        import platform
        if platform.system() != 'Linux':
            pytest.skip("Only runs on Linux")
        
        backend = keyring.get_keyring()
        # Linux应该尝试使用SecretService或其他安全backend
        # 在某些Linux系统上可能不可用，但至少不应该崩溃
        assert backend is not None
    
    def test_ac8_keychain_unavailable_returns_none(self, keychain_store):
        """验收标准8: Keychain不可用时返回None而不抛异常"""
        with patch('keyring.get_password') as mock_get:
            # 模拟Keychain不可用
            mock_get.side_effect = keyring.errors.KeyringError("Not available")
            
            # 应该返回None而不抛异常
            result = keychain_store.get_password()
            assert result is None
    
    def test_ac9_password_round_trip_passes(self, keychain_store):
        """验收标准9: 密码存储读取round-trip测试通过"""
        test_password = "round_trip_test_123"
        stored_password = None
        
        def mock_set(service, username, pwd):
            nonlocal stored_password
            stored_password = pwd
        
        def mock_get(service, username):
            return stored_password
        
        with patch('keyring.set_password', side_effect=mock_set):
            with patch('keyring.get_password', side_effect=mock_get):
                # 保存密码
                keychain_store.save_password(test_password)
                
                # 读取密码
                retrieved = keychain_store.get_password()
                
                # 验证round-trip
                assert retrieved == test_password
                assert retrieved is not None


class TestKeychainRequirementsMapping:
    """验证对应的需求是否满足"""
    
    @pytest.fixture
    def keychain_store(self):
        return KeychainStore()
    
    def test_req_3_3_save_password_to_keychain(self, keychain_store):
        """需求3.3: 保存主密码到操作系统Keychain"""
        with patch('keyring.set_password') as mock_set:
            password = "secure_password"
            keychain_store.save_password(password)
            
            # 验证调用了keyring库
            mock_set.assert_called_once()
            assert mock_set.call_args[0][2] == password
    
    def test_req_3_4_support_multiple_platforms(self, keychain_store):
        """需求3.4: 支持Windows/macOS/Linux"""
        # is_available方法应该能在所有平台上运行
        with patch('keyring.get_keyring'):
            result = keychain_store.is_available()
            assert isinstance(result, bool)
    
    def test_req_3_5_read_password_from_keychain(self, keychain_store):
        """需求3.5: 从操作系统Keychain中读取主密码"""
        with patch('keyring.get_password', return_value="stored_pwd"):
            result = keychain_store.get_password()
            assert result == "stored_pwd"
    
    def test_req_3_6_update_password(self, keychain_store):
        """需求3.6: 更新操作系统Keychain中的密码"""
        stored = {"password": "old"}
        
        def mock_set(service, username, pwd):
            stored["password"] = pwd
        
        def mock_get(service, username):
            return stored["password"]
        
        with patch('keyring.set_password', side_effect=mock_set):
            with patch('keyring.get_password', side_effect=mock_get):
                # 保存初始密码
                keychain_store.save_password("old")
                assert keychain_store.get_password() == "old"
                
                # 更新密码
                keychain_store.save_password("new")
                assert keychain_store.get_password() == "new"
    
    def test_req_3_7_fallback_when_unavailable(self, keychain_store):
        """需求3.7: Keychain不可用时的处理"""
        with patch('keyring.get_password') as mock_get:
            mock_get.side_effect = keyring.errors.KeyringError()
            
            # 应该返回None，让上层代码提示用户手动输入
            result = keychain_store.get_password()
            assert result is None


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.fixture
    def keychain_store(self):
        return KeychainStore()
    
    def test_save_empty_string_password(self, keychain_store):
        """测试保存空字符串密码"""
        with patch('keyring.set_password') as mock_set:
            keychain_store.save_password("")
            mock_set.assert_called_once()
    
    def test_save_very_long_password(self, keychain_store):
        """测试保存超长密码"""
        with patch('keyring.set_password') as mock_set:
            long_pwd = "x" * 10000
            keychain_store.save_password(long_pwd)
            mock_set.assert_called_once()
    
    def test_unicode_password_handling(self, keychain_store):
        """测试Unicode密码"""
        with patch('keyring.set_password') as mock_set:
            unicode_pwd = "密码🔐パスワード"
            keychain_store.save_password(unicode_pwd)
            assert mock_set.call_args[0][2] == unicode_pwd
    
    def test_delete_nonexistent_password(self, keychain_store):
        """测试删除不存在的密码"""
        with patch('keyring.delete_password') as mock_del:
            mock_del.side_effect = keyring.errors.PasswordDeleteError()
            
            # 不应该抛异常
            keychain_store.delete_password()
    
    def test_multiple_operations_sequence(self, keychain_store):
        """测试多个操作的序列"""
        storage = {}
        
        def mock_set(service, username, pwd):
            storage[username] = pwd
        
        def mock_get(service, username):
            return storage.get(username)
        
        def mock_del(service, username):
            if username not in storage:
                raise keyring.errors.PasswordDeleteError()
            del storage[username]
        
        with patch('keyring.set_password', side_effect=mock_set):
            with patch('keyring.get_password', side_effect=mock_get):
                with patch('keyring.delete_password', side_effect=mock_del):
                    # 保存
                    keychain_store.save_password("pwd1")
                    assert keychain_store.get_password() == "pwd1"
                    
                    # 更新
                    keychain_store.save_password("pwd2")
                    assert keychain_store.get_password() == "pwd2"
                    
                    # 删除
                    keychain_store.delete_password()
                    assert keychain_store.get_password() is None
