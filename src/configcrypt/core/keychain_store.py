"""
KeychainStore 密钥管理模块

使用keyring库实现跨平台Keychain抽象层，支持:
- Windows: Windows Credential Manager (WinVaultKeyring)
- macOS: macOS Keychain
- Linux: Secret Service API (SecretService.Keyring)
"""

from typing import Optional
import keyring
import keyring.backends.fail

from .exceptions import KeychainError


class KeychainStore:
    """跨平台Keychain抽象层，使用keyring库"""
    
    SERVICE_NAME = "KeyVault"
    USERNAME = "master_password"
    
    def save_password(self, password: str) -> None:
        """
        保存主密码到Keychain
        
        Args:
            password: 主密码字符串
            
        Raises:
            KeychainError: Keychain不可用或操作失败
        """
        try:
            keyring.set_password(self.SERVICE_NAME, self.USERNAME, password)
        except keyring.errors.KeyringError as e:
            raise KeychainError(f"无法保存密码到Keychain: {e}")
    
    def get_password(self) -> Optional[str]:
        """
        从Keychain读取主密码
        
        Returns:
            主密码字符串，未设置时返回None
        """
        try:
            return keyring.get_password(self.SERVICE_NAME, self.USERNAME)
        except keyring.errors.KeyringError:
            return None
    
    def delete_password(self) -> None:
        """
        删除Keychain中的主密码
        
        不抛出异常，即使密码不存在也会静默成功
        """
        try:
            keyring.delete_password(self.SERVICE_NAME, self.USERNAME)
        except keyring.errors.PasswordDeleteError:
            pass  # 密码不存在时忽略
    
    def is_available(self) -> bool:
        """
        检查Keychain是否可用
        
        keyring库会在不支持的平台上回退到明文文件存储(fail.Keyring),
        需要检测并拒绝使用这种不安全的backend。
        
        Returns:
            True表示Keychain可用，False表示不可用
        """
        backend = keyring.get_keyring()
        # 检查是否是失败回退backend
        return not isinstance(backend, keyring.backends.fail.Keyring)
