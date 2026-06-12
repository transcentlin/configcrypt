"""
Vault 加密引擎模块

基于Fernet对称加密和PBKDF2密钥派生的文件加密引擎。
"""

import base64
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from configcrypt.core.exceptions import (
    EncryptionError,
    DecryptionError,
    InvalidTokenError,
)


class Vault:
    """
    文件加密引擎，基于Fernet对称加密

    加密文件格式:
    [字节0-15]   盐值 (16 bytes, 随机生成)
    [字节16+]    Fernet加密数据
    """

    # PBKDF2迭代次数 (OWASP推荐最小值)
    PBKDF2_ITERATIONS = 200000
    # 盐值长度
    SALT_SIZE = 16
    # Fernet密钥长度
    KEY_SIZE = 32

    def __init__(self, keychain_store=None):
        """
        Args:
            keychain_store: Keychain存储实例，用于获取主密码（当前任务暂不使用）
        """
        self._keychain = keychain_store

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        使用PBKDF2-HMAC-SHA256派生密钥

        Args:
            password: 主密码
            salt: 盐值

        Returns:
            Base64编码的32字节密钥（Fernet格式）
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )
        key = kdf.derive(password.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    def _encrypt_bytes(self, plaintext: bytes, password: str) -> bytes:
        """
        加密字节数据

        格式: [16字节盐值][Fernet加密数据]

        Args:
            plaintext: 明文字节数据
            password: 密码

        Returns:
            加密后的字节数据

        Raises:
            EncryptionError: 加密失败
        """
        try:
            # 生成随机盐值
            salt = os.urandom(self.SALT_SIZE)

            # 派生密钥
            derived_key = self._derive_key(password, salt)

            # Fernet加密
            fernet = Fernet(derived_key)
            encrypted_data = fernet.encrypt(plaintext)

            # 组合格式: [盐值][加密数据]
            return salt + encrypted_data
        except Exception as e:
            raise EncryptionError(f"加密失败: {e}")

    def _decrypt_bytes(self, encrypted: bytes, password: str) -> bytes:
        """
        解密字节数据

        Args:
            encrypted: 加密的字节数据（包含盐值）
            password: 密码

        Returns:
            解密后的明文字节数据

        Raises:
            DecryptionError: 密码错误或通用解密错误
            InvalidTokenError: 文件完整性校验失败（文件被篡改）
        """
        try:
            # 检查最小长度（盐值 + 至少一些加密数据）
            if len(encrypted) < self.SALT_SIZE:
                raise DecryptionError("加密数据格式无效: 文件太小")

            # 提取盐值
            salt = encrypted[: self.SALT_SIZE]
            encrypted_data = encrypted[self.SALT_SIZE :]

            # 派生密钥
            derived_key = self._derive_key(password, salt)

            # Fernet解密（包含HMAC完整性校验）
            fernet = Fernet(derived_key)
            plaintext = fernet.decrypt(encrypted_data)

            return plaintext
        except InvalidToken:
            # Fernet的InvalidToken可能是密码错误或数据被篡改
            # 我们统一抛出InvalidTokenError表示完整性校验失败
            raise InvalidTokenError("解密失败: 密码错误或文件已损坏/被篡改")
        except DecryptionError:
            # 重新抛出我们自己的DecryptionError
            raise
        except Exception as e:
            raise DecryptionError(f"解密失败: {e}")

    def encrypt_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        password: Optional[str] = None,
        delete_source: bool = True,
    ) -> Path:
        """
        加密文件

        Args:
            input_path: 明文文件路径
            output_path: 输出路径，默认为 input_path.enc
            password: 主密码，为None时从Keychain读取
            delete_source: 是否删除源文件

        Returns:
            输出文件路径

        Raises:
            FileNotFoundError: 输入文件不存在
            PermissionError: 无文件读写权限
            EncryptionError: 加密过程出错
        """
        # 转换为Path对象
        input_path = Path(input_path)

        # 检查输入文件是否存在
        if not input_path.exists():
            raise FileNotFoundError(f"文件未找到: {input_path}")

        if not input_path.is_file():
            raise EncryptionError(f"不是一个文件: {input_path}")

        # 获取密码
        if password is None:
            if self._keychain is None:
                raise EncryptionError("未提供密码且未配置KeychainStore")
            password = self._keychain.get_password()
            if password is None:
                raise EncryptionError("未找到保存的密码，请先运行 'kv init' 或提供密码参数")

        # 确定输出路径
        if output_path is None:
            output_path = Path(str(input_path) + ".enc")
        else:
            output_path = Path(output_path)

        # 检查输出文件是否已存在
        if output_path.exists():
            raise EncryptionError(f"输出文件已存在: {output_path}")

        try:
            # 读取输入文件
            with open(input_path, "rb") as f:
                plaintext = f.read()

            # 加密数据
            encrypted_data = self._encrypt_bytes(plaintext, password)

            # 写入输出文件
            with open(output_path, "wb") as f:
                f.write(encrypted_data)

            # 根据参数决定是否删除源文件
            if delete_source:
                input_path.unlink()

            return output_path

        except (FileNotFoundError, EncryptionError):
            # 重新抛出已知异常
            raise
        except PermissionError as e:
            raise PermissionError(f"无权限访问文件: {e}")
        except OSError as e:
            # 处理磁盘空间不足等其他OS错误
            import errno

            if e.errno == errno.ENOSPC:
                raise EncryptionError("磁盘空间不足")
            raise EncryptionError(f"文件操作失败: {e}")
        except Exception as e:
            raise EncryptionError(f"加密过程出错: {e}")

    def decrypt_file(
        self, input_path: Path, output_path: Optional[Path] = None, password: Optional[str] = None
    ) -> Path:
        """
        解密文件

        Args:
            input_path: 加密文件路径
            output_path: 输出路径，默认移除.enc扩展名
            password: 主密码，为None时从Keychain读取

        Returns:
            输出文件路径

        Raises:
            FileNotFoundError: 输入文件不存在
            DecryptionError: 解密失败（密码错误或文件损坏）
            InvalidTokenError: 文件完整性校验失败
        """
        # 转换为Path对象
        input_path = Path(input_path)

        # 检查输入文件是否存在
        if not input_path.exists():
            raise FileNotFoundError(f"文件未找到: {input_path}")

        if not input_path.is_file():
            raise DecryptionError(f"不是一个文件: {input_path}")

        # 获取密码
        if password is None:
            if self._keychain is None:
                raise DecryptionError("未提供密码且未配置KeychainStore")
            password = self._keychain.get_password()
            if password is None:
                raise DecryptionError("未找到保存的密码，请先运行 'kv init' 或提供密码参数")

        # 确定输出路径
        if output_path is None:
            # 默认移除.enc扩展名
            if input_path.suffix == ".enc":
                output_path = input_path.with_suffix("")
            else:
                # 如果没有.enc扩展名，添加.decrypted后缀
                output_path = Path(str(input_path) + ".decrypted")
        else:
            output_path = Path(output_path)

        # 检查输出文件是否已存在
        if output_path.exists():
            raise DecryptionError(f"输出文件已存在: {output_path}")

        try:
            # 读取加密文件
            with open(input_path, "rb") as f:
                encrypted_data = f.read()

            # 解密数据
            plaintext = self._decrypt_bytes(encrypted_data, password)

            # 写入输出文件
            with open(output_path, "wb") as f:
                f.write(plaintext)

            # 在Unix-like系统上设置文件权限为0600（仅所有者可读写）
            import platform

            if platform.system() != "Windows":
                import stat

                output_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

            return output_path

        except (FileNotFoundError, DecryptionError, InvalidTokenError):
            # 重新抛出已知异常
            raise
        except PermissionError as e:
            raise PermissionError(f"无权限访问文件: {e}")
        except OSError as e:
            # 处理磁盘空间不足等其他OS错误
            import errno

            if e.errno == errno.ENOSPC:
                raise DecryptionError("磁盘空间不足")
            raise DecryptionError(f"文件操作失败: {e}")
        except Exception as e:
            raise DecryptionError(f"解密过程出错: {e}")

    def decrypt_to_string(self, input_path: Path, password: Optional[str] = None) -> str:
        """
        解密文件并返回字符串内容（不写入磁盘）

        用于Library API的便捷方法

        Args:
            input_path: 加密文件路径
            password: 主密码，为None时从Keychain读取

        Returns:
            解密后的字符串内容

        Raises:
            FileNotFoundError: 输入文件不存在
            DecryptionError: 解密失败
            InvalidTokenError: 文件完整性校验失败
        """
        # 转换为Path对象
        input_path = Path(input_path)

        # 检查输入文件是否存在
        if not input_path.exists():
            raise FileNotFoundError(f"文件未找到: {input_path}")

        if not input_path.is_file():
            raise DecryptionError(f"不是一个文件: {input_path}")

        # 获取密码
        if password is None:
            if self._keychain is None:
                raise DecryptionError("未提供密码且未配置KeychainStore")
            password = self._keychain.get_password()
            if password is None:
                raise DecryptionError("未找到保存的密码，请先运行 'kv init' 或提供密码参数")

        try:
            # 读取加密文件
            with open(input_path, "rb") as f:
                encrypted_data = f.read()

            # 解密数据
            plaintext_bytes = self._decrypt_bytes(encrypted_data, password)

            # 转换为字符串（使用UTF-8编码）
            return plaintext_bytes.decode("utf-8")

        except (FileNotFoundError, DecryptionError, InvalidTokenError):
            # 重新抛出已知异常
            raise
        except UnicodeDecodeError as e:
            raise DecryptionError(f"无法解码文件内容为UTF-8字符串: {e}")
        except PermissionError as e:
            raise PermissionError(f"无权限访问文件: {e}")
        except Exception as e:
            raise DecryptionError(f"解密过程出错: {e}")


class VaultAPI:
    """
    用户友好的Library API

    提供简洁的Python库接口用于解密和解析加密配置文件。

    Example:
        >>> from configcrypt import VaultAPI
        >>> vault = VaultAPI()
        >>> config = vault.decrypt_json('config.json.enc')
        >>> print(config['database']['password'])
    """

    def __init__(self, password: Optional[str] = None):
        """
        初始化VaultAPI实例

        Args:
            password: 主密码，为None时从Keychain读取
        """
        from configcrypt.core.keychain_store import KeychainStore
        from configcrypt.core.format_parser import FormatParser

        self._password = password
        self._keychain = KeychainStore()
        self._vault = Vault(self._keychain)
        self._parser = FormatParser()

    def decrypt_file(self, path: Path) -> str:
        """
        解密文件并返回字符串内容

        Args:
            path: 加密文件路径

        Returns:
            解密后的字符串内容

        Raises:
            FileNotFoundError: 文件不存在
            DecryptionError: 解密失败（密码错误或文件损坏）
            InvalidTokenError: 文件完整性校验失败

        Example:
            >>> vault = VaultAPI()
            >>> content = vault.decrypt_file('secret.txt.enc')
            >>> print(content)
        """
        return self._vault.decrypt_to_string(path, self._password)

    def decrypt_json(self, path: Path) -> dict:
        """
        解密并解析JSON文件

        Args:
            path: 加密的JSON文件路径

        Returns:
            解析后的字典对象

        Raises:
            FileNotFoundError: 文件不存在
            DecryptionError: 解密失败
            InvalidTokenError: 文件完整性校验失败
            ParseError: JSON格式解析失败

        Example:
            >>> vault = VaultAPI()
            >>> config = vault.decrypt_json('config.json.enc')
            >>> db_host = config['database']['host']
        """
        content = self.decrypt_file(path)
        return self._parser.parse_json(content)

    def decrypt_yaml(self, path: Path) -> dict:
        """
        解密并解析YAML文件

        Args:
            path: 加密的YAML文件路径

        Returns:
            解析后的字典对象

        Raises:
            FileNotFoundError: 文件不存在
            DecryptionError: 解密失败
            InvalidTokenError: 文件完整性校验失败
            ParseError: YAML格式解析失败

        Example:
            >>> vault = VaultAPI()
            >>> config = vault.decrypt_yaml('config.yaml.enc')
            >>> api_key = config['api']['key']
        """
        content = self.decrypt_file(path)
        return self._parser.parse_yaml(content)

    def decrypt_env(self, path: Path) -> dict:
        """
        解密并解析ENV文件

        Args:
            path: 加密的ENV文件路径

        Returns:
            解析后的字典对象（键值对）

        Raises:
            FileNotFoundError: 文件不存在
            DecryptionError: 解密失败
            InvalidTokenError: 文件完整性校验失败
            ParseError: ENV格式解析失败

        Example:
            >>> vault = VaultAPI()
            >>> env_vars = vault.decrypt_env('.env.enc')
            >>> db_password = env_vars['DB_PASSWORD']
        """
        content = self.decrypt_file(path)
        return self._parser.parse_env(content)
