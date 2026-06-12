"""
KeychainStore 单元测试

测试跨平台密码管理功能
"""

import pytest
from unittest.mock import patch, MagicMock
import keyring.errors
import keyring.backends.fail

from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.exceptions import KeychainError


class TestKeychainStore:
    """KeychainStore类单元测试"""

    @pytest.fixture
    def keychain_store(self):
        """创建KeychainStore实例"""
        return KeychainStore()

    def test_save_password_success(self, keychain_store):
        """测试成功保存密码到Keychain"""
        with patch("keyring.set_password") as mock_set:
            password = "test_password_123"
            keychain_store.save_password(password)

            # 验证调用了正确的参数
            mock_set.assert_called_once_with(
                KeychainStore.SERVICE_NAME, KeychainStore.USERNAME, password
            )

    def test_save_password_with_special_characters(self, keychain_store):
        """测试保存包含特殊字符的密码"""
        with patch("keyring.set_password") as mock_set:
            password = "p@ssw0rd!#$%^&*()中文密码"
            keychain_store.save_password(password)

            mock_set.assert_called_once()
            call_args = mock_set.call_args[0]
            assert call_args[2] == password

    def test_save_password_keychain_error(self, keychain_store):
        """测试Keychain操作失败时抛出异常"""
        with patch("keyring.set_password") as mock_set:
            mock_set.side_effect = keyring.errors.KeyringError("Keychain unavailable")

            with pytest.raises(KeychainError) as exc_info:
                keychain_store.save_password("test")

            assert "无法保存密码到Keychain" in str(exc_info.value)

    def test_get_password_success(self, keychain_store):
        """测试成功从Keychain读取密码"""
        with patch("keyring.get_password") as mock_get:
            expected_password = "stored_password"
            mock_get.return_value = expected_password

            result = keychain_store.get_password()

            assert result == expected_password
            mock_get.assert_called_once_with(KeychainStore.SERVICE_NAME, KeychainStore.USERNAME)

    def test_get_password_not_found(self, keychain_store):
        """测试密码未设置时返回None"""
        with patch("keyring.get_password") as mock_get:
            mock_get.return_value = None

            result = keychain_store.get_password()

            assert result is None

    def test_get_password_keychain_error(self, keychain_store):
        """测试Keychain读取错误时返回None而不抛异常"""
        with patch("keyring.get_password") as mock_get:
            mock_get.side_effect = keyring.errors.KeyringError("Access denied")

            result = keychain_store.get_password()

            assert result is None

    def test_delete_password_success(self, keychain_store):
        """测试成功删除密码"""
        with patch("keyring.delete_password") as mock_delete:
            keychain_store.delete_password()

            mock_delete.assert_called_once_with(KeychainStore.SERVICE_NAME, KeychainStore.USERNAME)

    def test_delete_password_not_exists(self, keychain_store):
        """测试删除不存在的密码时静默成功"""
        with patch("keyring.delete_password") as mock_delete:
            mock_delete.side_effect = keyring.errors.PasswordDeleteError("Password not found")

            # 不应该抛出异常
            keychain_store.delete_password()

            mock_delete.assert_called_once()

    def test_is_available_true(self, keychain_store):
        """测试Keychain可用时返回True"""
        # 创建一个非fail backend的mock
        mock_backend = MagicMock()
        mock_backend.__class__ = type("MockKeyring", (), {})

        with patch("keyring.get_keyring", return_value=mock_backend):
            assert keychain_store.is_available() is True

    def test_is_available_false_with_fail_backend(self, keychain_store):
        """测试使用fail backend时返回False"""
        # 创建fail.Keyring实例
        fail_backend = keyring.backends.fail.Keyring()

        with patch("keyring.get_keyring", return_value=fail_backend):
            assert keychain_store.is_available() is False

    def test_password_round_trip(self, keychain_store):
        """测试密码保存和读取的往返一致性"""
        password = "round_trip_test_password"
        stored_password = None

        def mock_set(service, username, pwd):
            nonlocal stored_password
            stored_password = pwd

        def mock_get(service, username):
            return stored_password

        with patch("keyring.set_password", side_effect=mock_set):
            with patch("keyring.get_password", side_effect=mock_get):
                # 保存密码
                keychain_store.save_password(password)

                # 读取密码
                result = keychain_store.get_password()

                # 验证一致性
                assert result == password

    def test_update_password(self, keychain_store):
        """测试更新已存在的密码"""
        old_password = "old_password"
        new_password = "new_password"
        stored_password = old_password

        def mock_set(service, username, pwd):
            nonlocal stored_password
            stored_password = pwd

        def mock_get(service, username):
            return stored_password

        with patch("keyring.set_password", side_effect=mock_set):
            with patch("keyring.get_password", side_effect=mock_get):
                # 保存初始密码
                keychain_store.save_password(old_password)
                assert keychain_store.get_password() == old_password

                # 更新密码
                keychain_store.save_password(new_password)
                assert keychain_store.get_password() == new_password

    def test_delete_then_get_returns_none(self, keychain_store):
        """测试删除密码后读取返回None"""
        stored_password = "some_password"

        def mock_set(service, username, pwd):
            nonlocal stored_password
            stored_password = pwd

        def mock_get(service, username):
            return stored_password

        def mock_delete(service, username):
            nonlocal stored_password
            stored_password = None

        with patch("keyring.set_password", side_effect=mock_set):
            with patch("keyring.get_password", side_effect=mock_get):
                with patch("keyring.delete_password", side_effect=mock_delete):
                    # 保存密码
                    keychain_store.save_password("password")

                    # 删除密码
                    keychain_store.delete_password()

                    # 读取应该返回None
                    assert keychain_store.get_password() is None

    def test_service_name_and_username_constants(self):
        """测试服务名和用户名常量正确定义"""
        assert KeychainStore.SERVICE_NAME == "KeyVault"
        assert KeychainStore.USERNAME == "master_password"

    def test_empty_password(self, keychain_store):
        """测试保存空字符串密码"""
        with patch("keyring.set_password") as mock_set:
            keychain_store.save_password("")

            mock_set.assert_called_once()
            call_args = mock_set.call_args[0]
            assert call_args[2] == ""

    def test_long_password(self, keychain_store):
        """测试保存超长密码（1000字符）"""
        with patch("keyring.set_password") as mock_set:
            long_password = "a" * 1000
            keychain_store.save_password(long_password)

            mock_set.assert_called_once()
            call_args = mock_set.call_args[0]
            assert call_args[2] == long_password

    def test_unicode_password(self, keychain_store):
        """测试保存Unicode密码（表情符号、各语言字符）"""
        with patch("keyring.set_password") as mock_set:
            unicode_password = "密码🔐パスワード🔑пароль"
            keychain_store.save_password(unicode_password)

            mock_set.assert_called_once()
            call_args = mock_set.call_args[0]
            assert call_args[2] == unicode_password


class TestKeychainStoreIntegration:
    """KeychainStore集成测试（需要真实Keychain）"""

    @pytest.mark.integration
    def test_real_keychain_round_trip(self):
        """测试真实Keychain的保存和读取（集成测试）"""
        keychain_store = KeychainStore()

        # 检查Keychain是否可用
        if not keychain_store.is_available():
            pytest.skip("Keychain not available on this system")

        test_password = "integration_test_password_12345"

        try:
            # 保存密码
            keychain_store.save_password(test_password)

            # 读取密码
            retrieved = keychain_store.get_password()

            # 验证
            assert retrieved == test_password
        finally:
            # 清理
            keychain_store.delete_password()

    @pytest.mark.integration
    def test_real_keychain_availability(self):
        """测试真实Keychain可用性检测（集成测试）"""
        keychain_store = KeychainStore()

        # 在大多数开发环境中，Keychain应该是可用的
        # 但在某些CI环境或容器中可能不可用
        is_available = keychain_store.is_available()

        # 只验证返回值是布尔类型
        assert isinstance(is_available, bool)
