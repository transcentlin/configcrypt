#!/usr/bin/env python3
"""
ConfigCrypt Windows 可执行文件构建脚本

使用 PyInstaller 创建独立的 Windows 可执行文件

使用方法:
    python build_executable.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def main():
    """构建 Windows 可执行文件"""
    print("=" * 70)
    print("ConfigCrypt Windows 可执行文件构建器")
    print("=" * 70)
    print()
    
    # 检查是否在 Windows 上
    if sys.platform != 'win32':
        print("⚠️  警告：此脚本主要用于 Windows 平台")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
    
    # 检查 PyInstaller 是否安装
    print("1️⃣  检查 PyInstaller...")
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller 已安装（版本 {PyInstaller.__version__}）")
    except ImportError:
        print("   ❌ PyInstaller 未安装")
        print("   正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("   ✅ PyInstaller 安装完成")
    
    print()
    
    # 清理旧的构建文件
    print("2️⃣  清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   删除 {dir_name}/")
            shutil.rmtree(dir_path)
    print("   ✅ 清理完成")
    print()
    
    # 运行 PyInstaller
    print("3️⃣  开始构建可执行文件...")
    print("   这可能需要几分钟时间，请耐心等待...")
    print()
    
    try:
        # 使用 spec 文件构建
        if Path('configcrypt.spec').exists():
            print("   使用 configcrypt.spec 配置文件")
            subprocess.check_call(['pyinstaller', 'configcrypt.spec', '--clean'])
        else:
            # 如果没有 spec 文件，使用命令行参数
            print("   使用默认配置")
            subprocess.check_call([
                'pyinstaller',
                '--name=ConfigCrypt',
                '--onefile',
                '--windowed',
                '--clean',
                'run.py'
            ])
        
        print()
        print("   ✅ 构建完成")
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 构建失败: {e}")
        return 1
    
    print()
    
    # 检查生成的可执行文件
    print("4️⃣  验证可执行文件...")
    exe_path = Path('dist') / 'ConfigCrypt.exe'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ ConfigCrypt.exe 已生成")
        print(f"   📦 文件大小: {size_mb:.2f} MB")
        print(f"   📁 位置: {exe_path.absolute()}")
    else:
        print("   ❌ 未找到 ConfigCrypt.exe")
        return 1
    
    print()
    
    # 完成
    print("=" * 70)
    print("🎉 构建成功！")
    print("=" * 70)
    print()
    print("📝 使用说明:")
    print("   1. 可执行文件位于: dist/ConfigCrypt.exe")
    print("   2. 可以直接双击运行")
    print("   3. 可以分发给其他 Windows 用户")
    print("   4. 无需安装 Python 环境")
    print()
    print("⚠️  注意事项:")
    print("   - 首次运行时可能被杀毒软件拦截（这是正常的）")
    print("   - 添加到杀毒软件白名单即可")
    print("   - 可执行文件较大是因为包含了完整的 Python 运行时")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
