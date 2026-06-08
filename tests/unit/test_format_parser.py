"""
FormatParser单元测试

测试JSON、YAML和ENV格式解析功能
"""

import pytest

from configcrypt.core.format_parser import FormatParser
from configcrypt.core.exceptions import ParseError


class TestParseJSON:
    """测试JSON格式解析"""
    
    def test_parse_simple_json(self):
        """测试解析简单JSON对象"""
        content = '{"name": "John", "age": 30}'
        result = FormatParser.parse_json(content)
        assert result == {"name": "John", "age": 30}
    
    def test_parse_nested_json(self):
        """测试解析嵌套JSON对象"""
        content = '''
        {
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {
                    "username": "admin",
                    "password": "secret123"
                }
            }
        }
        '''
        result = FormatParser.parse_json(content)
        assert result["database"]["host"] == "localhost"
        assert result["database"]["credentials"]["password"] == "secret123"
    
    def test_parse_json_array(self):
        """测试解析包含数组的JSON"""
        content = '{"servers": ["server1", "server2"], "count": 2}'
        result = FormatParser.parse_json(content)
        assert result["servers"] == ["server1", "server2"]
        assert result["count"] == 2
    
    def test_parse_json_with_unicode(self):
        """测试解析包含Unicode字符的JSON"""
        content = '{"message": "你好世界", "emoji": "😀"}'
        result = FormatParser.parse_json(content)
        assert result["message"] == "你好世界"
        assert result["emoji"] == "😀"
    
    def test_parse_empty_json_object(self):
        """测试解析空JSON对象"""
        content = '{}'
        result = FormatParser.parse_json(content)
        assert result == {}
    
    def test_parse_json_with_special_types(self):
        """测试解析包含特殊类型的JSON"""
        content = '{"null_value": null, "bool_true": true, "bool_false": false}'
        result = FormatParser.parse_json(content)
        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False
    
    def test_parse_invalid_json_syntax_error(self):
        """测试解析语法错误的JSON"""
        content = '{"name": "John", "age": 30'  # 缺少闭合括号
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_json(content)
        assert "JSON解析失败" in str(exc_info.value)
        assert "行" in str(exc_info.value)
        assert "列" in str(exc_info.value)
    
    def test_parse_invalid_json_unexpected_comma(self):
        """测试解析包含多余逗号的JSON"""
        content = '{"name": "John",}'
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_json(content)
        assert "JSON解析失败" in str(exc_info.value)
    
    def test_parse_invalid_json_single_quotes(self):
        """测试解析使用单引号的JSON(JSON标准不支持)"""
        content = "{'name': 'John'}"
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_json(content)
        assert "JSON解析失败" in str(exc_info.value)


class TestParseYAML:
    """测试YAML格式解析"""
    
    def test_parse_simple_yaml(self):
        """测试解析简单YAML"""
        content = """
        name: John
        age: 30
        """
        result = FormatParser.parse_yaml(content)
        assert result == {"name": "John", "age": 30}
    
    def test_parse_nested_yaml(self):
        """测试解析嵌套YAML"""
        content = """
        database:
          host: localhost
          port: 5432
          credentials:
            username: admin
            password: secret123
        """
        result = FormatParser.parse_yaml(content)
        assert result["database"]["host"] == "localhost"
        assert result["database"]["credentials"]["password"] == "secret123"
    
    def test_parse_yaml_with_arrays(self):
        """测试解析包含数组的YAML"""
        content = """
        servers:
          - server1
          - server2
          - server3
        count: 3
        """
        result = FormatParser.parse_yaml(content)
        assert result["servers"] == ["server1", "server2", "server3"]
        assert result["count"] == 3
    
    def test_parse_yaml_with_comments(self):
        """测试解析包含注释的YAML"""
        content = """
        # Database configuration
        database:
          host: localhost  # Production server
          port: 5432
        """
        result = FormatParser.parse_yaml(content)
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == 5432
    
    def test_parse_yaml_with_multiline_strings(self):
        """测试解析包含多行字符串的YAML"""
        content = """
        description: |
          This is a multi-line
          string in YAML format
          that preserves newlines
        """
        result = FormatParser.parse_yaml(content)
        assert "multi-line" in result["description"]
        assert "\n" in result["description"]
    
    def test_parse_empty_yaml(self):
        """测试解析空YAML文件"""
        content = ""
        result = FormatParser.parse_yaml(content)
        assert result == {}
    
    def test_parse_yaml_with_special_types(self):
        """测试解析包含特殊类型的YAML"""
        content = """
        null_value: null
        bool_true: true
        bool_false: false
        number: 42
        float: 3.14
        """
        result = FormatParser.parse_yaml(content)
        assert result["null_value"] is None
        assert result["bool_true"] is True
        assert result["bool_false"] is False
        assert result["number"] == 42
        assert result["float"] == 3.14
    
    def test_parse_invalid_yaml_indentation(self):
        """测试解析缩进错误的YAML"""
        content = """
        database:
          host: localhost
        port: 5432
        """
        # 注意：这实际上是有效的YAML，port在根级别
        result = FormatParser.parse_yaml(content)
        assert "database" in result
        assert "port" in result  # port在根级别
    
    def test_parse_invalid_yaml_syntax(self):
        """测试解析语法错误的YAML"""
        content = """
        database:
          host: localhost
          port: [invalid syntax
        """
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_yaml(content)
        assert "YAML解析失败" in str(exc_info.value)
    
    def test_parse_yaml_non_dict_root(self):
        """测试解析根元素不是字典的YAML"""
        content = """
        - item1
        - item2
        - item3
        """
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_yaml(content)
        assert "期望字典类型" in str(exc_info.value)
        assert "list" in str(exc_info.value)


class TestParseENV:
    """测试ENV格式解析"""
    
    def test_parse_simple_env(self):
        """测试解析简单ENV格式"""
        content = """
        DB_HOST=localhost
        DB_PORT=5432
        DB_USER=admin
        """
        result = FormatParser.parse_env(content)
        assert result == {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_USER": "admin"
        }
    
    def test_parse_env_with_comments(self):
        """测试解析包含注释的ENV"""
        content = """
        # Database configuration
        DB_HOST=localhost
        # DB_PORT=3306  # This line is commented out
        DB_PORT=5432
        """
        result = FormatParser.parse_env(content)
        assert result == {
            "DB_HOST": "localhost",
            "DB_PORT": "5432"
        }
    
    def test_parse_env_with_empty_lines(self):
        """测试解析包含空行的ENV"""
        content = """
        DB_HOST=localhost
        
        DB_PORT=5432
        
        
        DB_USER=admin
        """
        result = FormatParser.parse_env(content)
        assert result == {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_USER": "admin"
        }
    
    def test_parse_env_with_double_quotes(self):
        """测试解析双引号包裹的值"""
        content = """
        DB_PASSWORD="my secret password"
        DB_CONNECTION="host=localhost port=5432"
        """
        result = FormatParser.parse_env(content)
        assert result["DB_PASSWORD"] == "my secret password"
        assert result["DB_CONNECTION"] == "host=localhost port=5432"
    
    def test_parse_env_with_single_quotes(self):
        """测试解析单引号包裹的值"""
        content = """
        DB_PASSWORD='my secret password'
        DB_CONNECTION='host=localhost port=5432'
        """
        result = FormatParser.parse_env(content)
        assert result["DB_PASSWORD"] == "my secret password"
        assert result["DB_CONNECTION"] == "host=localhost port=5432"
    
    def test_parse_env_with_export_statement(self):
        """测试解析export语句"""
        content = """
        export DB_HOST=localhost
        export DB_PORT=5432
        DB_USER=admin
        """
        result = FormatParser.parse_env(content)
        assert result == {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_USER": "admin"
        }
    
    def test_parse_env_with_equals_in_value(self):
        """测试解析值中包含等号的情况"""
        content = """
        MATH_EQUATION=1+1=2
        CONNECTION_STRING=server=localhost;user=admin
        """
        result = FormatParser.parse_env(content)
        assert result["MATH_EQUATION"] == "1+1=2"
        assert result["CONNECTION_STRING"] == "server=localhost;user=admin"
    
    def test_parse_env_with_empty_value(self):
        """测试解析空值"""
        content = """
        EMPTY_VAR=
        ANOTHER_VAR=""
        """
        result = FormatParser.parse_env(content)
        assert result["EMPTY_VAR"] == ""
        assert result["ANOTHER_VAR"] == ""
    
    def test_parse_env_with_whitespace(self):
        """测试解析包含空格的ENV"""
        content = """
        DB_HOST = localhost
          DB_PORT=5432  
        DB_USER=  admin  
        """
        result = FormatParser.parse_env(content)
        assert result["DB_HOST"] == "localhost"
        assert result["DB_PORT"] == "5432"
        assert result["DB_USER"] == "admin"
    
    def test_parse_env_with_special_characters(self):
        """测试解析包含特殊字符的值"""
        content = """
        PASSWORD=p@ssw0rd!#$%
        URL=https://example.com/path?key=value&other=123
        """
        result = FormatParser.parse_env(content)
        assert result["PASSWORD"] == "p@ssw0rd!#$%"
        assert result["URL"] == "https://example.com/path?key=value&other=123"
    
    def test_parse_env_with_unicode(self):
        """测试解析包含Unicode字符的ENV"""
        content = """
        MESSAGE=你好世界
        EMOJI=😀🎉
        """
        result = FormatParser.parse_env(content)
        assert result["MESSAGE"] == "你好世界"
        assert result["EMOJI"] == "😀🎉"
    
    def test_parse_empty_env(self):
        """测试解析空ENV文件"""
        content = ""
        result = FormatParser.parse_env(content)
        assert result == {}
    
    def test_parse_env_only_comments_and_empty_lines(self):
        """测试解析只包含注释和空行的ENV"""
        content = """
        # Comment 1
        
        # Comment 2
        
        """
        result = FormatParser.parse_env(content)
        assert result == {}
    
    def test_parse_env_missing_equals_sign(self):
        """测试解析缺少等号的行"""
        content = """
        DB_HOST=localhost
        INVALID_LINE
        DB_PORT=5432
        """
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_env(content)
        assert "ENV解析失败" in str(exc_info.value)
        assert "行3" in str(exc_info.value)  # 第一行是空行，所以INVALID_LINE在第3行
        assert "缺少'='分隔符" in str(exc_info.value)
        assert "INVALID_LINE" in str(exc_info.value)
    
    def test_parse_env_empty_key(self):
        """测试解析空键名"""
        content = """
        DB_HOST=localhost
        =some_value
        """
        with pytest.raises(ParseError) as exc_info:
            FormatParser.parse_env(content)
        assert "ENV解析失败" in str(exc_info.value)
        assert "行3" in str(exc_info.value)  # 第一行是空行，所以=some_value在第3行
        assert "键名为空" in str(exc_info.value)
    
    def test_parse_env_with_quoted_value_containing_quotes(self):
        """测试解析引号包裹的值中包含引号的情况"""
        content = """
        MESSAGE="She said 'hello'"
        COMMAND='echo "test"'
        """
        result = FormatParser.parse_env(content)
        # 只移除外层引号
        assert result["MESSAGE"] == "She said 'hello'"
        assert result["COMMAND"] == 'echo "test"'
    
    def test_parse_env_partial_quotes(self):
        """测试解析不完整引号的值"""
        content = """
        PARTIAL_QUOTE="incomplete
        ANOTHER_VAR=normal_value
        """
        # 不完整的引号被当作普通字符处理
        result = FormatParser.parse_env(content)
        assert result["PARTIAL_QUOTE"] == '"incomplete'
        assert result["ANOTHER_VAR"] == "normal_value"
    
    def test_parse_env_mixed_export_and_normal(self):
        """测试解析混合export和普通格式"""
        content = """
        export VAR1=value1
        VAR2=value2
        export VAR3=value3
        """
        result = FormatParser.parse_env(content)
        assert result == {
            "VAR1": "value1",
            "VAR2": "value2",
            "VAR3": "value3"
        }


class TestEdgeCases:
    """测试边界情况和异常场景"""
    
    def test_parse_json_very_large_object(self):
        """测试解析大型JSON对象"""
        # 创建包含1000个键值对的JSON
        data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        import json as json_lib
        content = json_lib.dumps(data)
        result = FormatParser.parse_json(content)
        assert len(result) == 1000
        assert result["key_500"] == "value_500"
    
    def test_parse_yaml_very_large_object(self):
        """测试解析大型YAML对象"""
        lines = [f"key_{i}: value_{i}" for i in range(1000)]
        content = "\n".join(lines)
        result = FormatParser.parse_yaml(content)
        assert len(result) == 1000
        assert result["key_500"] == "value_500"
    
    def test_parse_env_very_large_file(self):
        """测试解析大型ENV文件"""
        lines = [f"KEY_{i}=value_{i}" for i in range(1000)]
        content = "\n".join(lines)
        result = FormatParser.parse_env(content)
        assert len(result) == 1000
        assert result["KEY_500"] == "value_500"
    
    def test_parse_json_deeply_nested(self):
        """测试解析深度嵌套的JSON"""
        content = '{"a": {"b": {"c": {"d": {"e": "deep_value"}}}}}'
        result = FormatParser.parse_json(content)
        assert result["a"]["b"]["c"]["d"]["e"] == "deep_value"
    
    def test_parse_yaml_deeply_nested(self):
        """测试解析深度嵌套的YAML"""
        content = """
        a:
          b:
            c:
              d:
                e: deep_value
        """
        result = FormatParser.parse_yaml(content)
        assert result["a"]["b"]["c"]["d"]["e"] == "deep_value"
    
    def test_parse_env_very_long_value(self):
        """测试解析很长的值"""
        long_value = "x" * 10000
        content = f"LONG_VAR={long_value}"
        result = FormatParser.parse_env(content)
        assert result["LONG_VAR"] == long_value
        assert len(result["LONG_VAR"]) == 10000
