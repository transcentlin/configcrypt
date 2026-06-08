"""
KeyVault - 文件级加密工具

提供CLI、GUI和Python Library三种使用方式的跨平台文件加密解决方案。
"""

__version__ = "0.1.0"
__author__ = "KeyVault Team"

# 导出主要API
from configcrypt.core.vault import Vault, VaultAPI
from configcrypt.core.exceptions import (
    KeyVaultError,
    EncryptionError,
    DecryptionError,
    InvalidTokenError,
    KeychainError,
    ParseError,
    EditorNotFoundError,
    PasswordValidationError,
)

__all__ = [
    "Vault",
    "VaultAPI",
    "KeyVaultError",
    "EncryptionError",
    "DecryptionError",
    "InvalidTokenError",
    "KeychainError",
    "ParseError",
    "EditorNotFoundError",
    "PasswordValidationError",
]
