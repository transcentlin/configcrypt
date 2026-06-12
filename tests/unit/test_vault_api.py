"""
VaultAPI Library API 单元测试

测试VaultAPI类的所有方法，包括:
- 构造函数(有/无密码参数)
- decrypt_file()方法
- decrypt_json()方法
- decrypt_yaml()方法
- decrypt_env()方法
- 异常处理(DecryptionError, FileNotFoundError, ParseError)
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from configcrypt.core.vault import Vault, VaultAPI
from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.exceptions import (
    DecryptionError,
    ParseError,
    InvalidTokenError,
)


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_password():
    """测试密码"""
    return "test_password_12345"


@pytest.fixture
def vault_with_password(test_password):
    """创建带KeychainStore的Vault实例"""
    keychain = KeychainStore()
    vault = Vault(keychain)
    return vault, test_password


class TestVaultAPIConstructor:
    """测试VaultAPI构造函数"""

    def test_init_with_password(self):
        """测试使用密码参数初始化"""
        password = "my_secret_password"
        vault_api = VaultAPI(password=password)

        assert vault_api._password == password
        assert vault_api._keychain is not None
        assert vault_api._vault is not None
        assert vault_api._parser is not None

    def test_init_without_password(self):
        """测试不提供密码参数初始化（将从Keychain读取）"""
        vault_api = VaultAPI()

        assert vault_api._password is None
        assert vault_api._keychain is not None
        assert vault_api._vault is not None
        assert vault_api._parser is not None


class TestVaultAPIDecryptFile:
    """测试VaultAPI.decrypt_file()方法"""

    def test_decrypt_file_success(self, temp_dir, vault_with_password):
        """测试成功解密文件并返回字符串"""
        vault, password = vault_with_password

        # 准备测试数据
        test_content = "Hello, World!\nThis is a test file."
        plaintext_file = temp_dir / "test.txt"
        encrypted_file = temp_dir / "test.txt.enc"

        # 使用二进制模式写入以避免平台换行符差异
        plaintext_file.write_bytes(test_content.encode("utf-8"))

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 使用VaultAPI解密
        vault_api = VaultAPI(password=password)
        decrypted_content = vault_api.decrypt_file(encrypted_file)

        assert decrypted_content == test_content

    def test_decrypt_file_unicode_content(self, temp_dir, vault_with_password):
        """测试解密包含Unicode字符的文件"""
        vault, password = vault_with_password

        # 包含中文和emoji的测试数据
        test_content = "你好世界 🌍\nこんにちは 🗾"
        plaintext_file = temp_dir / "unicode.txt"
        encrypted_file = temp_dir / "unicode.txt.enc"

        # 使用二进制模式写入以避免平台换行符差异
        plaintext_file.write_bytes(test_content.encode("utf-8"))

        # 加密并解密
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)
        vault_api = VaultAPI(password=password)
        decrypted_content = vault_api.decrypt_file(encrypted_file)

        assert decrypted_content == test_content

    def test_decrypt_file_not_found(self):
        """测试解密不存在的文件抛出FileNotFoundError"""
        vault_api = VaultAPI(password="test_password")
        non_existent_file = Path("/tmp/non_existent_file.enc")

        with pytest.raises(FileNotFoundError):
            vault_api.decrypt_file(non_existent_file)

    def test_decrypt_file_wrong_password(self, temp_dir, vault_with_password):
        """测试使用错误密码解密抛出异常"""
        vault, correct_password = vault_with_password

        # 准备并加密文件
        test_content = "Secret data"
        plaintext_file = temp_dir / "secret.txt"
        encrypted_file = temp_dir / "secret.txt.enc"

        plaintext_file.write_text(test_content, encoding="utf-8")
        vault.encrypt_file(plaintext_file, encrypted_file, correct_password, delete_source=False)

        # 使用错误密码解密
        vault_api = VaultAPI(password="wrong_password")

        with pytest.raises(InvalidTokenError):
            vault_api.decrypt_file(encrypted_file)


class TestVaultAPIDecryptJSON:
    """测试VaultAPI.decrypt_json()方法"""

    def test_decrypt_json_success(self, temp_dir, vault_with_password):
        """测试成功解密并解析JSON文件"""
        vault, password = vault_with_password

        # 准备JSON测试数据
        test_data = {
            "database": {"host": "localhost", "port": 5432, "password": "secret123"},
            "api": {"key": "abc123", "enabled": True},
        }

        plaintext_file = temp_dir / "config.json"
        encrypted_file = temp_dir / "config.json.enc"

        plaintext_file.write_text(json.dumps(test_data, indent=2), encoding="utf-8")

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 使用VaultAPI解密并解析
        vault_api = VaultAPI(password=password)
        decrypted_data = vault_api.decrypt_json(encrypted_file)

        assert decrypted_data == test_data
        assert decrypted_data["database"]["password"] == "secret123"
        assert decrypted_data["api"]["enabled"] is True

    def test_decrypt_json_invalid_format(self, temp_dir, vault_with_password):
        """测试解密格式无效的JSON文件抛出ParseError"""
        vault, password = vault_with_password

        # 准备无效JSON数据
        invalid_json = "{invalid json content"
        plaintext_file = temp_dir / "invalid.json"
        encrypted_file = temp_dir / "invalid.json.enc"

        plaintext_file.write_text(invalid_json, encoding="utf-8")

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 尝试解密并解析，应该抛出ParseError
        vault_api = VaultAPI(password=password)

        with pytest.raises(ParseError) as exc_info:
            vault_api.decrypt_json(encrypted_file)

        assert "JSON解析失败" in str(exc_info.value)

    def test_decrypt_json_empty_object(self, temp_dir, vault_with_password):
        """测试解密空JSON对象"""
        vault, password = vault_with_password

        plaintext_file = temp_dir / "empty.json"
        encrypted_file = temp_dir / "empty.json.enc"

        plaintext_file.write_text("{}", encoding="utf-8")

        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        vault_api = VaultAPI(password=password)
        decrypted_data = vault_api.decrypt_json(encrypted_file)

        assert decrypted_data == {}


class TestVaultAPIDecryptYAML:
    """测试VaultAPI.decrypt_yaml()方法"""

    def test_decrypt_yaml_success(self, temp_dir, vault_with_password):
        """测试成功解密并解析YAML文件"""
        vault, password = vault_with_password

        # 准备YAML测试数据
        test_data = {
            "server": {"host": "example.com", "port": 8080},
            "credentials": {"username": "admin", "password": "secret_pass"},
        }

        plaintext_file = temp_dir / "config.yaml"
        encrypted_file = temp_dir / "config.yaml.enc"

        plaintext_file.write_text(yaml.dump(test_data), encoding="utf-8")

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 使用VaultAPI解密并解析
        vault_api = VaultAPI(password=password)
        decrypted_data = vault_api.decrypt_yaml(encrypted_file)

        assert decrypted_data == test_data
        assert decrypted_data["server"]["host"] == "example.com"
        assert decrypted_data["credentials"]["password"] == "secret_pass"

    def test_decrypt_yaml_invalid_format(self, temp_dir, vault_with_password):
        """测试解密格式无效的YAML文件抛出ParseError"""
        vault, password = vault_with_password

        # 准备无效YAML数据（缩进错误）
        invalid_yaml = """
        key1: value1
      key2: value2
        """
        plaintext_file = temp_dir / "invalid.yaml"
        encrypted_file = temp_dir / "invalid.yaml.enc"

        plaintext_file.write_text(invalid_yaml, encoding="utf-8")

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 尝试解密并解析，应该抛出ParseError
        vault_api = VaultAPI(password=password)

        with pytest.raises(ParseError) as exc_info:
            vault_api.decrypt_yaml(encrypted_file)

        assert "YAML解析失败" in str(exc_info.value)

    def test_decrypt_yaml_empty_file(self, temp_dir, vault_with_password):
        """测试解密空YAML文件返回空字典"""
        vault, password = vault_with_password

        plaintext_file = temp_dir / "empty.yaml"
        encrypted_file = temp_dir / "empty.yaml.enc"

        plaintext_file.write_text("", encoding="utf-8")

        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        vault_api = VaultAPI(password=password)
        decrypted_data = vault_api.decrypt_yaml(encrypted_file)

        assert decrypted_data == {}


class TestVaultAPIDecryptENV:
    """测试VaultAPI.decrypt_env()方法"""

    def test_decrypt_env_success(self, temp_dir, vault_with_password):
        """测试成功解密并解析ENV文件"""
        vault, password = vault_with_password

        # 准备ENV测试数据
        env_content = """
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secret123

# API configuration
API_KEY="abc123xyz"
API_SECRET='very_secret'
export DEBUG_MODE=true
"""

        plaintext_file = temp_dir / ".env"
        encrypted_file = temp_dir / ".env.enc"

        plaintext_file.write_text(env_content, encoding="utf-8")

        # 加密文件
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        # 使用VaultAPI解密并解析
        vault_api = VaultAPI(password=password)
        env_vars = vault_api.decrypt_env(encrypted_file)

        assert env_vars["DB_HOST"] == "localhost"
        assert env_vars["DB_PORT"] == "5432"
        assert env_vars["DB_PASSWORD"] == "secret123"
        assert env_vars["API_KEY"] == "abc123xyz"  # 引号已被移除
        assert env_vars["API_SECRET"] == "very_secret"  # 引号已被移除
        assert env_vars["DEBUG_MODE"] == "true"  # export已被处理

    def test_decrypt_env_comments_and_empty_lines(self, temp_dir, vault_with_password):
        """测试ENV解析正确处理注释和空行"""
        vault, password = vault_with_password

        env_content = """
# This is a comment

KEY1=value1

# Another comment
KEY2=value2

"""

        plaintext_file = temp_dir / ".env"
        encrypted_file = temp_dir / ".env.enc"

        plaintext_file.write_text(env_content, encoding="utf-8")
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        vault_api = VaultAPI(password=password)
        env_vars = vault_api.decrypt_env(encrypted_file)

        assert env_vars == {"KEY1": "value1", "KEY2": "value2"}

    def test_decrypt_env_invalid_format(self, temp_dir, vault_with_password):
        """测试解密格式无效的ENV文件抛出ParseError"""
        vault, password = vault_with_password

        # 准备无效ENV数据（缺少=分隔符）
        invalid_env = """
KEY1=value1
INVALID_LINE_WITHOUT_EQUALS
KEY2=value2
"""

        plaintext_file = temp_dir / ".env"
        encrypted_file = temp_dir / ".env.enc"

        plaintext_file.write_text(invalid_env, encoding="utf-8")
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        vault_api = VaultAPI(password=password)

        with pytest.raises(ParseError) as exc_info:
            vault_api.decrypt_env(encrypted_file)

        assert "ENV解析失败" in str(exc_info.value)
        assert "行" in str(exc_info.value)  # 应该包含行号信息

    def test_decrypt_env_empty_file(self, temp_dir, vault_with_password):
        """测试解密空ENV文件返回空字典"""
        vault, password = vault_with_password

        plaintext_file = temp_dir / ".env"
        encrypted_file = temp_dir / ".env.enc"

        plaintext_file.write_text("", encoding="utf-8")
        vault.encrypt_file(plaintext_file, encrypted_file, password, delete_source=False)

        vault_api = VaultAPI(password=password)
        env_vars = vault_api.decrypt_env(encrypted_file)

        assert env_vars == {}


class TestVaultAPIIntegration:
    """VaultAPI集成测试"""

    def test_full_workflow_json(self, temp_dir, vault_with_password):
        """测试完整的加密解密JSON工作流"""
        vault, password = vault_with_password

        # 创建配置文件
        config = {
            "app_name": "MyApp",
            "version": "1.0.0",
            "secrets": {"api_key": "super_secret_key", "db_password": "db_pass_123"},
        }

        config_file = temp_dir / "app_config.json"
        config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

        # 加密
        encrypted_file = vault.encrypt_file(config_file, password=password, delete_source=False)

        # 使用Library API读取
        vault_api = VaultAPI(password=password)
        loaded_config = vault_api.decrypt_json(encrypted_file)

        # 验证数据完整性
        assert loaded_config == config
        assert loaded_config["secrets"]["api_key"] == "super_secret_key"

    def test_multiple_formats_same_password(self, temp_dir, vault_with_password):
        """测试同一密码可以解密多种格式的文件"""
        vault, password = vault_with_password

        # JSON文件
        json_data = {"key": "value"}
        json_file = temp_dir / "data.json"
        json_file.write_text(json.dumps(json_data), encoding="utf-8")
        json_enc = vault.encrypt_file(json_file, password=password, delete_source=False)

        # YAML文件
        yaml_data = {"key": "value"}
        yaml_file = temp_dir / "data.yaml"
        yaml_file.write_text(yaml.dump(yaml_data), encoding="utf-8")
        yaml_enc = vault.encrypt_file(yaml_file, password=password, delete_source=False)

        # ENV文件
        env_file = temp_dir / ".env"
        env_file.write_text("KEY=value", encoding="utf-8")
        env_enc = vault.encrypt_file(env_file, password=password, delete_source=False)

        # 使用同一VaultAPI实例解密所有文件
        vault_api = VaultAPI(password=password)

        json_result = vault_api.decrypt_json(json_enc)
        yaml_result = vault_api.decrypt_yaml(yaml_enc)
        env_result = vault_api.decrypt_env(env_enc)

        assert json_result == {"key": "value"}
        assert yaml_result == {"key": "value"}
        assert env_result == {"KEY": "value"}
