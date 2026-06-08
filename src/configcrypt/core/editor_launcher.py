"""
EditorLauncher 编辑器启动模块

跨平台编辑器启动器，支持Windows、macOS和Linux系统
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

from .exceptions import EditorNotFoundError


class EditorLauncher:
    """跨平台编辑器启动器"""
    
    # 各平台默认编辑器列表（优先级从高到低）
    DEFAULT_EDITORS = {
        'win32': ['code', 'notepad++', 'notepad', 'start'],  # start 使用 Windows 默认程序
        'darwin': ['code', 'subl', 'open'],
        'linux': ['code', 'gedit', 'nano', 'vim']
    }
    
    def open_file(
        self,
        file_path: Path,
        editor_command: Optional[str] = None
    ) -> None:
        """
        打开文件编辑
        
        优先级:
        1. editor_command参数
        2. $EDITOR环境变量
        3. 平台默认编辑器列表
        
        Args:
            file_path: 要打开的文件路径
            editor_command: 指定的编辑器命令
            
        Raises:
            EditorNotFoundError: 无可用编辑器
        """
        # 优先使用指定的编辑器
        if editor_command:
            if self._try_open(editor_command, file_path):
                return
            raise EditorNotFoundError(f"指定的编辑器不可用: {editor_command}")
        
        # 尝试 $EDITOR 环境变量
        editor_env = os.environ.get('EDITOR')
        if editor_env and self._try_open(editor_env, file_path):
            return
        
        # 尝试平台默认编辑器
        platform = sys.platform
        editor_list = self.DEFAULT_EDITORS.get(platform, [])
        for editor in editor_list:
            if self._try_open(editor, file_path):
                return
        
        raise EditorNotFoundError("未找到可用的编辑器")
    
    def _try_open(self, editor: str, file_path: Path) -> bool:
        """
        尝试用指定编辑器打开文件
        
        Args:
            editor: 编辑器命令（可能包含参数）
            file_path: 要打开的文件路径
            
        Returns:
            成功返回True，失败返回False
        """
        # 特殊处理：Windows 的 notepad 和 macOS 的 open 命令
        editor_parts = editor.split()
        editor_name = editor_parts[0]
        
        # Windows 特殊处理
        if sys.platform == 'win32':
            if editor_name == 'notepad':
                # notepad 是 Windows 内置命令，不需要检查 which
                try:
                    subprocess.Popen(['notepad.exe', str(file_path)])
                    return True
                except Exception:
                    return False
            elif editor_name == 'start':
                # 使用 Windows 默认程序打开
                try:
                    os.startfile(str(file_path))
                    return True
                except Exception:
                    return False
        
        # macOS 特殊处理
        if sys.platform == 'darwin' and editor_name == 'open':
            try:
                subprocess.Popen([*editor_parts, str(file_path)])
                return True
            except Exception:
                return False
        
        # 检查编辑器是否存在（普通编辑器）
        if not shutil.which(editor_name):
            return False
        
        try:
            # 使用subprocess.Popen非阻塞启动
            subprocess.Popen([*editor_parts, str(file_path)])
            return True
        except Exception:
            return False
