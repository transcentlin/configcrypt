"""
FormatParser 格式解析模块

提供JSON、YAML和ENV格式的配置文件解析功能。
"""

import json
from typing import Dict, Any

import yaml

from .exceptions import ParseError


class FormatParser:
    """配置文件格式解析器"""

    @staticmethod
    def parse_json(content: str) -> Dict[str, Any]:
        """
        解析JSON格式

        Args:
            content: JSON格式的字符串内容

        Returns:
            解析后的字典对象

        Raises:
            ParseError: JSON解析失败,包含详细错误信息
        """
        try:
            # 移除UTF-8 BOM（如果存在）
            if content.startswith("\ufeff"):
                content = content[1:]
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ParseError(f"JSON解析失败 (行{e.lineno}, 列{e.colno}): {e.msg}")

    @staticmethod
    def parse_yaml(content: str) -> Dict[str, Any]:
        """
        解析YAML格式

        Args:
            content: YAML格式的字符串内容

        Returns:
            解析后的字典对象

        Raises:
            ParseError: YAML解析失败,包含详细错误信息
        """
        try:
            # 移除UTF-8 BOM（如果存在）
            if content.startswith("\ufeff"):
                content = content[1:]

            result = yaml.safe_load(content)
            # yaml.safe_load可能返回None(空文件)或其他类型
            if result is None:
                return {}
            if not isinstance(result, dict):
                raise ParseError(f"YAML解析失败: 期望字典类型,但得到{type(result).__name__}")
            return result
        except yaml.YAMLError as e:
            # 提取行号和列号信息(如果可用)
            error_msg = str(e)
            if hasattr(e, "problem_mark"):
                mark = e.problem_mark
                error_msg = f"行{mark.line + 1}, 列{mark.column + 1}: {error_msg}"
            raise ParseError(f"YAML解析失败: {error_msg}")

    @staticmethod
    def parse_env(content: str) -> Dict[str, str]:
        """
        解析ENV格式 (KEY=VALUE)

        支持:
        - 注释行 (# 开头)
        - 空行
        - 单引号和双引号包裹的值
        - 导出语句 (export KEY=VALUE)

        Args:
            content: ENV格式的字符串内容

        Returns:
            解析后的字典对象(键值对)

        Raises:
            ParseError: ENV解析失败,包含详细错误信息(行号)
        """
        # 移除UTF-8 BOM（如果存在）
        if content.startswith("\ufeff"):
            content = content[1:]

        result = {}

        for line_num, line in enumerate(content.splitlines(), 1):
            # 保留原始行用于错误消息
            original_line = line
            line = line.strip()

            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue

            # 移除 export 前缀
            if line.startswith("export "):
                line = line[7:].strip()

            # 解析 KEY=VALUE
            if "=" not in line:
                raise ParseError(
                    f"ENV解析失败 (行{line_num}): 无效的格式,缺少'='分隔符\n"
                    f"问题行: {original_line}"
                )

            # 分割键值对(只分割第一个=)
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            # 验证键名有效性
            if not key:
                raise ParseError(
                    f"ENV解析失败 (行{line_num}): 键名为空\n" f"问题行: {original_line}"
                )

            # 移除引号
            if len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

            result[key] = value

        return result
