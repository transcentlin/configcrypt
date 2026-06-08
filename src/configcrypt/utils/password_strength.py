"""
密码强度计算工具模块

提供密码强度评估功能，供 CLI 和 GUI 使用。
"""

from enum import Enum


class PasswordStrength(Enum):
    """密码强度枚举"""
    WEAK = 0      # 0-40分
    MEDIUM = 1    # 41-70分
    STRONG = 2    # 71-100分


def calculate_password_strength(password: str) -> PasswordStrength:
    """
    计算密码强度
    
    评分因素:
    - 长度: 8-11字符(10分), 12-15(20分), 16+(30分)
    - 大写字母: 存在(15分)
    - 小写字母: 存在(15分)
    - 数字: 存在(15分)
    - 特殊字符: 存在(25分)
    
    Args:
        password: 要评估的密码
        
    Returns:
        PasswordStrength: 密码强度等级
        
    Example:
        >>> calculate_password_strength("12345678")
        PasswordStrength.WEAK
        
        >>> calculate_password_strength("Abc12345")
        PasswordStrength.MEDIUM
        
        >>> calculate_password_strength("Abc123!@#")
        PasswordStrength.STRONG
    """
    score = 0
    
    # 长度评分
    length = len(password)
    if length >= 16:
        score += 30
    elif length >= 12:
        score += 20
    elif length >= 8:
        score += 10
    
    # 字符类型评分
    if any(c.isupper() for c in password):
        score += 15
    
    if any(c.islower() for c in password):
        score += 15
    
    if any(c.isdigit() for c in password):
        score += 15
    
    # 特殊字符
    special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    if any(c in special_chars for c in password):
        score += 25
    
    # 根据分数返回强度等级
    if score <= 40:
        return PasswordStrength.WEAK
    elif score <= 70:
        return PasswordStrength.MEDIUM
    else:
        return PasswordStrength.STRONG


def get_password_strength_text(strength: PasswordStrength) -> str:
    """
    获取密码强度的文本描述
    
    Args:
        strength: 密码强度等级
        
    Returns:
        str: 强度描述文本
    """
    strength_map = {
        PasswordStrength.WEAK: "弱",
        PasswordStrength.MEDIUM: "中",
        PasswordStrength.STRONG: "强",
    }
    return strength_map.get(strength, "未知")
