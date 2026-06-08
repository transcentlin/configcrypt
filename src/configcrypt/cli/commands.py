"""
ConfigCrypt CLI命令实现

使用click实现命令行界面
"""

import sys
from pathlib import Path
import click
from importlib.metadata import version as get_version

from configcrypt.core.vault import Vault
from configcrypt.core.keychain_store import KeychainStore
from configcrypt.core.editor_launcher import EditorLauncher
from configcrypt.core.exceptions import (
    EncryptionError,
    DecryptionError,
    InvalidTokenError,
    KeychainError,
    EditorNotFoundError
)


def _calculate_password_strength(password: str) -> str:
    """
    计算密码强度
    
    强度等级:
    - 弱: 长度<8 或 只包含字母/数字
    - 中: 长度>=8 且 包含字母+数字
    - 强: 长度>=12 且 包含字母+数字+特殊字符
    
    Args:
        password: 密码字符串
        
    Returns:
        "弱"、"中"或"强"
    """
    if len(password) < 8:
        return "弱"
    
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if len(password) >= 12 and has_letter and has_digit and has_special:
        return "强"
    elif len(password) >= 8 and has_letter and has_digit:
        return "中"
    else:
        return "弱"


@click.group()
@click.version_option(version=get_version('configcrypt'), prog_name='ConfigCrypt')
def cli():
    """ConfigCrypt - 文件级加密工具
    
    安全地加密和解密敏感配置文件
    """
    pass


@cli.command()
def init():
    """初始化ConfigCrypt，设置主密码"""
    click.echo("🔐 ConfigCrypt 初始化")
    click.echo("=" * 50)
    
    keychain = KeychainStore()
    
    # 检查Keychain是否可用
    if not keychain.is_available():
        click.echo("❌ 错误: 系统Keychain不可用")
        click.echo("请确保您的系统支持密码存储功能")
        sys.exit(1)
    
    # 检查是否已有密码
    existing_password = keychain.get_password()
    if existing_password:
        click.echo("⚠️  警告: 已存在主密码")
        if not click.confirm("是否要重新设置主密码？", default=False):
            click.echo("操作已取消")
            sys.exit(0)
    
    # 输入新密码
    while True:
        password = click.prompt(
            "请输入主密码",
            hide_input=True,
            confirmation_prompt=True
        )
        
        # 验证密码长度
        if len(password) < 8:
            click.echo("❌ 密码长度至少为8个字符，请重新输入")
            continue
        
        # 显示密码强度
        strength = _calculate_password_strength(password)
        click.echo(f"密码强度: {strength}")
        
        # 如果密码较弱，询问是否继续
        if strength == "弱":
            if not click.confirm("密码强度较弱，是否继续？", default=False):
                continue
        
        break
    
    # 保存密码到Keychain
    try:
        keychain.save_password(password)
        click.echo("✅ 主密码已成功保存到系统Keychain")
        click.echo("\n现在您可以使用以下命令:")
        click.echo("  cc encrypt <file>  - 加密文件")
        click.echo("  cc decrypt <file>  - 解密文件")
    except KeychainError as e:
        click.echo(f"❌ 保存密码失败: {e}")
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--out',
    type=click.Path(path_type=Path),
    help='输出文件路径（默认: 原文件名.enc）'
)
@click.option(
    '--keep',
    is_flag=True,
    help='保留源文件（默认会删除）'
)
def encrypt(file, out, keep):
    """加密文件
    
    FILE: 要加密的文件路径
    """
    keychain = KeychainStore()
    vault = Vault(keychain_store=keychain)
    
    try:
        # 检查输出文件是否已存在
        output_path = out if out else Path(str(file) + '.enc')
        if output_path.exists():
            if not click.confirm(f"输出文件 {output_path} 已存在，是否覆盖？", default=False):
                click.echo("操作已取消")
                sys.exit(0)
            # 删除已存在的文件以便加密
            output_path.unlink()
        
        # 加密文件
        delete_source = not keep
        encrypted_path = vault.encrypt_file(
            file,
            output_path=out,
            delete_source=delete_source
        )
        
        # 显示成功消息
        click.echo(f"✅ 文件已成功加密")
        click.echo(f"📁 输出文件: {encrypted_path}")
        
        if delete_source:
            click.echo(f"🗑️  源文件已删除: {file}")
        else:
            click.echo(f"📄 源文件保留: {file}")
            
    except FileNotFoundError as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)
    except EncryptionError as e:
        if "未找到保存的密码" in str(e):
            click.echo("❌ 错误: 未找到主密码")
            click.echo("请先运行 'cc init' 初始化并设置主密码")
        elif "输出文件已存在" in str(e):
            click.echo(f"❌ 错误: {e}")
            click.echo("提示: 使用 --out 选项指定不同的输出路径")
        else:
            click.echo(f"❌ 加密失败: {e}")
        sys.exit(1)
    except PermissionError as e:
        click.echo(f"❌ 权限错误: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 未知错误: {e}")
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--out',
    type=click.Path(path_type=Path),
    help='输出文件路径（默认: 移除.enc扩展名）'
)
@click.option(
    '--open',
    'open_editor',
    is_flag=True,
    help='解密后立即用编辑器打开文件'
)
@click.option(
    '--editor',
    type=str,
    help='指定编辑器命令（配合--open使用）'
)
def decrypt(file, out, open_editor, editor):
    """解密文件
    
    FILE: 要解密的文件路径
    """
    keychain = KeychainStore()
    vault = Vault(keychain_store=keychain)
    
    try:
        # 检查输出文件是否已存在
        if out and Path(out).exists():
            if not click.confirm(f"输出文件 {out} 已存在，是否覆盖？", default=False):
                click.echo("操作已取消")
                sys.exit(0)
            # 删除已存在的文件以便解密
            Path(out).unlink()
        
        # 解密文件
        decrypted_path = vault.decrypt_file(
            file,
            output_path=out
        )
        
        # 显示成功消息
        click.echo(f"✅ 文件已成功解密")
        click.echo(f"📁 输出文件: {decrypted_path}")
        
        # 如果指定了--open选项，打开编辑器
        if open_editor:
            try:
                launcher = EditorLauncher()
                launcher.open_file(decrypted_path, editor_command=editor)
                click.echo(f"📝 已用编辑器打开文件")
            except EditorNotFoundError as e:
                click.echo(f"⚠️  警告: {e}")
                click.echo("提示: 使用 --editor 选项指定编辑器命令")
                click.echo("示例: cc decrypt file.enc --open --editor nano")
        
    except FileNotFoundError as e:
        click.echo(f"❌ 错误: {e}")
        sys.exit(1)
    except InvalidTokenError:
        click.echo("❌ 解密失败: 密码错误或文件已损坏/被篡改")
        click.echo("提示: 请确认:")
        click.echo("  1. 主密码是否正确（运行 'kv init' 重新设置）")
        click.echo("  2. 文件是否完整且未被修改")
        sys.exit(1)
    except DecryptionError as e:
        if "未找到保存的密码" in str(e):
            click.echo("❌ 错误: 未找到主密码")
            click.echo("请先运行 'cc init' 初始化并设置主密码")
        elif "输出文件已存在" in str(e):
            click.echo(f"❌ 错误: {e}")
            click.echo("提示: 使用 --out 选项指定不同的输出路径")
        else:
            click.echo(f"❌ 解密失败: {e}")
        sys.exit(1)
    except PermissionError as e:
        click.echo(f"❌ 权限错误: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ 未知错误: {e}")
        sys.exit(1)


@cli.command()
def status():
    """显示ConfigCrypt状态信息"""
    click.echo("🔐 ConfigCrypt 状态")
    click.echo("=" * 50)
    
    keychain = KeychainStore()
    
    # 检查Keychain可用性
    if not keychain.is_available():
        click.echo("❌ Keychain状态: 不可用")
        click.echo("⚠️  警告: 系统Keychain不可用，无法使用ConfigCrypt")
        sys.exit(1)
    else:
        click.echo("✅ Keychain状态: 可用")
    
    # 检查主密码是否已设置
    password = keychain.get_password()
    if password:
        click.echo("✅ 主密码: 已设置")
        click.echo(f"   密码强度: {_calculate_password_strength(password)}")
    else:
        click.echo("❌ 主密码: 未设置")
        click.echo("提示: 运行 'cc init' 设置主密码")
    
    click.echo("\n可用命令:")
    click.echo("  cc init              - 初始化/重置主密码")
    click.echo("  cc encrypt <file>    - 加密文件")
    click.echo("  cc decrypt <file>    - 解密文件")
    click.echo("  cc reset-password    - 修改主密码")
    click.echo("  cc status            - 显示状态信息")


@cli.command('reset-password')
def reset_password():
    """修改主密码
    
    验证旧密码后设置新密码
    """
    click.echo("🔐 修改主密码")
    click.echo("=" * 50)
    
    keychain = KeychainStore()
    vault = Vault(keychain_store=keychain)
    
    # 检查Keychain是否可用
    if not keychain.is_available():
        click.echo("❌ 错误: 系统Keychain不可用")
        sys.exit(1)
    
    # 检查是否已有密码
    old_password = keychain.get_password()
    if not old_password:
        click.echo("❌ 错误: 未找到主密码")
        click.echo("请先运行 'cc init' 初始化并设置主密码")
        sys.exit(1)
    
    # 验证旧密码
    click.echo("请先验证当前主密码")
    input_old_password = click.prompt("当前主密码", hide_input=True)
    
    if input_old_password != old_password:
        click.echo("❌ 错误: 当前密码不正确")
        sys.exit(1)
    
    click.echo("✅ 密码验证成功")
    click.echo()
    
    # 输入新密码
    click.echo("请设置新的主密码")
    while True:
        new_password = click.prompt(
            "新主密码",
            hide_input=True,
            confirmation_prompt=True
        )
        
        # 验证密码长度
        if len(new_password) < 8:
            click.echo("❌ 密码长度至少为8个字符，请重新输入")
            continue
        
        # 不允许使用相同的密码
        if new_password == old_password:
            click.echo("❌ 新密码不能与旧密码相同，请重新输入")
            continue
        
        # 显示密码强度
        strength = _calculate_password_strength(new_password)
        click.echo(f"密码强度: {strength}")
        
        # 如果密码较弱，询问是否继续
        if strength == "弱":
            if not click.confirm("密码强度较弱，是否继续？", default=False):
                continue
        
        break
    
    # 保存新密码
    try:
        keychain.save_password(new_password)
        click.echo("✅ 主密码已成功更新")
        click.echo("\n⚠️  重要提示:")
        click.echo("  - 所有已加密的文件仍使用旧密码加密")
        click.echo("  - 新密码仅用于加密新文件")
        click.echo("  - 若要使用新密码，需重新加密旧文件")
    except KeychainError as e:
        click.echo(f"❌ 保存密码失败: {e}")
        sys.exit(1)


def main():
    """CLI入口点"""
    cli()


if __name__ == '__main__':
    main()
