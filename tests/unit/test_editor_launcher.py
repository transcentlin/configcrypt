"""
EditorLauncher单元测试

测试跨平台编辑器启动功能
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from configcrypt.core.editor_launcher import EditorLauncher
from configcrypt.core.exceptions import EditorNotFoundError


class TestEditorLauncher:
    """测试EditorLauncher基础功能"""

    def test_open_file_with_specified_editor(self, tmp_path):
        """测试使用指定编辑器打开文件"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file, editor_command="nano")

                # 验证Popen被调用
                mock_popen.assert_called_once_with(["nano", str(test_file)])

    def test_open_file_with_editor_env_variable(self, tmp_path, monkeypatch):
        """测试使用$EDITOR环境变量"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 设置$EDITOR环境变量
        monkeypatch.setenv("EDITOR", "vim")

        with patch("shutil.which", return_value="/usr/bin/vim"):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file)

                # 验证使用了$EDITOR
                mock_popen.assert_called_once_with(["vim", str(test_file)])

    def test_open_file_specified_editor_priority(self, tmp_path, monkeypatch):
        """测试指定编辑器优先级最高"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 设置$EDITOR环境变量
        monkeypatch.setenv("EDITOR", "vim")

        # 指定编辑器应该优先于$EDITOR
        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file, editor_command="nano")

                # 验证使用了指定的编辑器而不是$EDITOR
                mock_popen.assert_called_once_with(["nano", str(test_file)])

    def test_open_file_unavailable_specified_editor(self, tmp_path):
        """测试指定的编辑器不可用时抛出异常"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value=None):
            with pytest.raises(EditorNotFoundError) as exc_info:
                launcher.open_file(test_file, editor_command="nonexistent_editor")

            assert "指定的编辑器不可用" in str(exc_info.value)
            assert "nonexistent_editor" in str(exc_info.value)

    def test_open_file_no_available_editor(self, tmp_path):
        """测试没有可用编辑器时抛出异常"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 所有编辑器都不可用（包括 Windows 特殊处理）
        with patch("shutil.which", return_value=None):
            with patch("subprocess.Popen", side_effect=OSError("Editor not found")):
                with patch("os.startfile", side_effect=OSError("No application")):
                    with pytest.raises(EditorNotFoundError) as exc_info:
                        launcher.open_file(test_file)

                    assert "未找到可用的编辑器" in str(exc_info.value)

    def test_try_open_success(self, tmp_path):
        """测试_try_open成功打开"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                result = launcher._try_open("nano", test_file)

                assert result is True
                mock_popen.assert_called_once_with(["nano", str(test_file)])

    def test_try_open_editor_not_found(self, tmp_path):
        """测试_try_open编辑器不存在"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value=None):
            result = launcher._try_open("nonexistent", test_file)
            assert result is False

    def test_try_open_with_popen_exception(self, tmp_path):
        """测试_try_open时Popen抛出异常"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen", side_effect=OSError("Permission denied")):
                result = launcher._try_open("nano", test_file)
                assert result is False

    def test_editor_with_arguments(self, tmp_path):
        """测试编辑器命令带参数"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/open"):
            with patch("subprocess.Popen") as mock_popen:
                result = launcher._try_open("open -e", test_file)

                assert result is True
                mock_popen.assert_called_once_with(["open", "-e", str(test_file)])


class TestPlatformDefaultEditors:
    """测试平台默认编辑器列表"""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only test")
    def test_windows_default_editors(self, tmp_path):
        """测试Windows平台默认编辑器"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 模拟只有notepad可用
        def which_side_effect(cmd):
            if cmd == "notepad":
                return "C:\\Windows\\System32\\notepad.exe"
            return None

        with patch("shutil.which", side_effect=which_side_effect):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file)

                # 验证使用了notepad.exe（Windows实际调用的命令）
                mock_popen.assert_called_once()
                call_args = mock_popen.call_args[0][0]
                assert call_args[0] == "notepad.exe"

    @pytest.mark.skip(reason="macOS not supported - Windows only project")
    def test_macos_default_editors(self, tmp_path):
        """测试macOS平台默认编辑器"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 模拟只有open可用
        def which_side_effect(cmd):
            if cmd == "open":
                return "/usr/bin/open"
            return None

        with patch("shutil.which", side_effect=which_side_effect):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file)

                # 验证使用了open -e
                mock_popen.assert_called_once()
                call_args = mock_popen.call_args[0][0]
                assert call_args[0] == "open"
                assert call_args[1] == "-e"

    @pytest.mark.skip(reason="Linux not supported - Windows only project")
    def test_linux_default_editors(self, tmp_path):
        """测试Linux平台默认编辑器"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 模拟只有nano可用
        def which_side_effect(cmd):
            if cmd == "nano":
                return "/usr/bin/nano"
            return None

        with patch("shutil.which", side_effect=which_side_effect):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file)

                # 验证使用了nano
                mock_popen.assert_called_once()
                call_args = mock_popen.call_args[0][0]
                assert call_args[0] == "nano"

    @pytest.mark.skip(reason="Linux not supported - Windows only project")
    def test_vscode_priority(self, tmp_path):
        """测试VS Code优先级最高"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # VS Code和nano都可用时，应该优先使用VS Code
        def which_side_effect(cmd):
            if cmd in ["code", "nano"]:
                return f"/usr/bin/{cmd}"
            return None

        with patch("shutil.which", side_effect=which_side_effect):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file)

                # 验证使用了code而不是nano
                mock_popen.assert_called_once()
                call_args = mock_popen.call_args[0][0]
                assert call_args[0] == "code"


class TestEditorFallback:
    """测试编辑器回退机制"""

    @pytest.mark.skip(reason="Linux not supported - Windows only project")
    def test_fallback_to_second_editor(self, tmp_path):
        """测试回退到第二个编辑器"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 第一个编辑器不可用，第二个可用
        def which_side_effect(cmd):
            if cmd == "gedit":
                return "/usr/bin/gedit"
            return None

        with patch("sys.platform", "linux"):
            with patch("shutil.which", side_effect=which_side_effect):
                with patch("subprocess.Popen") as mock_popen:
                    launcher.open_file(test_file)

                    # 验证使用了gedit（列表中第二个）
                    mock_popen.assert_called_once()
                    call_args = mock_popen.call_args[0][0]
                    assert call_args[0] == "gedit"

    @pytest.mark.skip(reason="Linux not supported - Windows only project")
    def test_fallback_to_last_editor(self, tmp_path):
        """测试回退到最后一个编辑器"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 只有最后一个编辑器可用
        def which_side_effect(cmd):
            if cmd == "vim":
                return "/usr/bin/vim"
            return None

        with patch("sys.platform", "linux"):
            with patch("shutil.which", side_effect=which_side_effect):
                with patch("subprocess.Popen") as mock_popen:
                    launcher.open_file(test_file)

                    # 验证使用了vim（列表中最后一个）
                    mock_popen.assert_called_once()
                    call_args = mock_popen.call_args[0][0]
                    assert call_args[0] == "vim"


class TestEdgeCases:
    """测试边界情况"""

    def test_file_path_with_spaces(self, tmp_path):
        """测试文件路径包含空格"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test file with spaces.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file, editor_command="nano")

                # 验证路径正确传递
                call_args = mock_popen.call_args[0][0]
                assert str(test_file) in call_args

    def test_file_path_with_unicode(self, tmp_path):
        """测试文件路径包含Unicode字符"""
        launcher = EditorLauncher()
        test_file = tmp_path / "测试文件.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                launcher.open_file(test_file, editor_command="nano")

                # 验证路径正确传递
                call_args = mock_popen.call_args[0][0]
                assert str(test_file) in call_args

    def test_multiple_spaces_in_editor_command(self, tmp_path):
        """测试编辑器命令包含多个空格"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/open"):
            with patch("subprocess.Popen") as mock_popen:
                # 命令包含多个参数
                result = launcher._try_open("open  -e  -a", test_file)

                # 验证参数被正确分割
                assert result is True
                call_args = mock_popen.call_args[0][0]
                # split()会自动处理多个空格
                assert "open" in call_args

    @pytest.mark.skip(reason="Linux not supported - Windows only project")
    def test_env_editor_empty_string(self, tmp_path, monkeypatch):
        """测试$EDITOR为空字符串"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # 设置$EDITOR为空字符串
        monkeypatch.setenv("EDITOR", "")

        # 模拟nano可用
        def which_side_effect(cmd):
            if cmd == "nano":
                return "/usr/bin/nano"
            return None

        with patch("sys.platform", "linux"):
            with patch("shutil.which", side_effect=which_side_effect):
                with patch("subprocess.Popen") as mock_popen:
                    launcher.open_file(test_file)

                    # 应该跳过空的$EDITOR，使用默认编辑器
                    mock_popen.assert_called_once()
                    call_args = mock_popen.call_args[0][0]
                    assert call_args[0] == "nano"

    def test_unknown_platform(self, tmp_path):
        """测试未知平台"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("sys.platform", "unknown_os"):
            with patch("shutil.which", return_value=None):
                with pytest.raises(EditorNotFoundError):
                    launcher.open_file(test_file)


class TestNonBlockingLaunch:
    """测试非阻塞启动"""

    def test_popen_non_blocking(self, tmp_path):
        """测试使用Popen非阻塞启动"""
        launcher = EditorLauncher()
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        with patch("shutil.which", return_value="/usr/bin/nano"):
            with patch("subprocess.Popen") as mock_popen:
                # 模拟Popen返回进程对象
                mock_process = MagicMock()
                mock_popen.return_value = mock_process

                launcher.open_file(test_file, editor_command="nano")

                # 验证使用了Popen而不是run或call
                mock_popen.assert_called_once()

                # 验证没有调用wait()方法（非阻塞）
                mock_process.wait.assert_not_called()
                mock_process.communicate.assert_not_called()
