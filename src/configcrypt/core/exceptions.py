"""
KeyVault 异常定义模块

定义所有KeyVault相关的异常类型。
"""


class KeyVaultError(Exception):
    """所有KeyVault异常的基类"""
    pass


class EncryptionError(KeyVaultError):
    """加密操作失败"""
    pass


class DecryptionError(KeyVaultError):
    """解密操作失败（密码错误或通用解密错误）"""
    pass


class InvalidTokenError(DecryptionError):
    """文件完整性校验失败（文件被篡改）"""
    pass


class KeychainError(KeyVaultError):
    """Keychain操作失败"""
    pass


class ParseError(KeyVaultError):
    """配置文件格式解析失败"""
    pass


class EditorNotFoundError(KeyVaultError):
    """未找到可用的编辑器"""
    pass


class PasswordValidationError(KeyVaultError):
    """密码不符合安全要求"""
    pass
