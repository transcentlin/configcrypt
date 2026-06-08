# 更新日志 (Changelog)

本文档记录ConfigCrypt项目的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

---

## [Unreleased]

### 计划中的功能
- 批量加密/解密
- macOS和Linux平台完整测试
- 大文件分块处理（>100MB）
- 更多编辑器支持
- 多语言支持（英文、中文）

---

## [1.0.2] - 2026-06-08

### Changed
- 清理项目结构，移除临时和开发文件
- 重新组织文档到 docs 目录
- 更新 .gitignore 规则

### Removed
- 删除开发过程中的临时 .bat 脚本
- 删除中间过程文档和报告
- 删除测试缓存目录 (.hypothesis, .pytest_cache, .kiro)

### Added
- 添加 run.py GUI 启动脚本
- 添加完整的项目文档到 docs 目录

---

## [1.0.1] - 2025-06-08

### Added
- 添加 `cc --version` 命令支持，显示软件版本号
- 版本号现在自动从 `pyproject.toml` 读取，无需手动同步

### Changed
- 更新品牌名称：KeyVault → ConfigCrypt
- 更新 CLI 命令前缀：`kv` → `cc`
- 所有命令示例和帮助文本已更新

### Fixed
- 修复 `cc --version` 选项缺失的问题

---

## [1.0.0] - 2025-06-08

### 🎉 首个正式版本

这是ConfigCrypt的第一个正式发布版本，提供完整的文件加密解密功能。

### 🔄 项目重命名

**项目名称变更**: KeyVault → ConfigCrypt

**原因**:
- PyPI 包名 `keyvault` 已被占用
- `configcrypt` 语义更准确（配置加密）
- 更符合项目定位和功能描述

**主要变更**:
- **包名**: `keyvault` → `configcrypt`
- **CLI 命令**: `kv` → `cc`
- **GUI 命令**: `keyvault-gui` → `configcrypt-gui`
- **可执行文件**: `ConfigCrypt.exe` (原 KeyVault.exe)
- **配置目录**: `~/.configcrypt/` (原 ~/.keyvault/)
- **Python 导入**: `from configcrypt import VaultAPI` (原 from keyvault)

**兼容性说明**:
- API 使用方式完全相同，只需更改导入语句
- 旧版本用户需要重新安装：`pip uninstall keyvault && pip install configcrypt`
- 历史记录和 Keychain 数据保持兼容

### ✨ 新增功能

#### 核心功能
- **文件加密/解密** - 基于Fernet (AES-128) + PBKDF2-HMAC-SHA256
- **主密码管理** - 集成系统Keychain（Windows Credential Manager / macOS Keychain / Linux Secret Service）
- **密钥派生** - PBKDF2 200,000轮迭代，每次加密生成随机盐值
- **完整性验证** - HMAC防篡改检测

#### CLI命令行界面
- `cc init` - 初始化主密码
- `cc encrypt <file>` - 加密文件
  - `--keep` 保留源文件
  - `--out <path>` 指定输出路径
- `cc decrypt <file>` - 解密文件
  - `--out <path>` 指定输出路径
  - `--open` 解密后打开编辑器
  - `--editor <command>` 指定编辑器
- `cc status` - 查看Keychain和密码状态
- `cc reset-password` - 修改主密码
- 密码强度指示器（弱/中/强）
- 彩色终端输出和进度提示

#### GUI图形界面
- **主窗口**
  - 黑底暗金色高级配色设计
  - 上下分割布局（拖拽区 + 操作历史）
  - 圆形加密/解密按钮（红色/绿色）
  - 窗口图标和标题
- **文件拖拽**
  - 支持拖拽文件到窗口
  - 自动识别文件类型（.enc = 解密，其他 = 加密）
  - 拖拽区视觉反馈（边框高亮）
- **对话框**
  - 欢迎向导（首次启动设置密码）
  - 加密对话框（选项：删除源文件）
  - 解密对话框（选项：打开编辑器）
  - 密码输入对话框
  - 设置对话框（修改密码）
  - 进度对话框
  - 所有对话框统一黑金配色和锁图标
- **操作历史面板**
  - 显示加密/解密历史记录
  - 列：时间、操作、文件、输出、状态
  - 统计信息（总计、成功、失败）
  - 刷新和清除历史按钮
  - 历史持久化到 `~/.configcrypt/history.json`
  - 列宽可拖拽调整

#### Library API
- `VaultAPI` 类 - Python API接口
- `decrypt_file(path)` - 解密为字符串
- `decrypt_json(path)` - 解密并解析JSON
- `decrypt_yaml(path)` - 解密并解析YAML
- `decrypt_env(path)` - 解密并解析ENV
- `FormatParser` - 格式解析器
  - JSON格式支持
  - YAML格式支持
  - ENV格式支持（支持注释、引号、export语句）
- 异常类：`DecryptionError`, `InvalidTokenError`, `ParseError`, `EncryptionError`

#### 增强功能
- **编辑器启动器** - 跨平台编辑器调用
  - Windows: notepad, notepad++, code
  - macOS: code, subl, open -e
  - Linux: code, gedit, nano, vim
- **文件类型识别** - 自动识别.enc扩展名
- **UTF-8 BOM兼容** - 完美处理Windows环境的BOM问题

### 🐛 Bug修复
- 修复Windows环境下JSON/YAML/ENV解析UTF-8 BOM错误
- 修复GUI窗口初始位置和大小设置
- 修复操作历史表格宽度对齐问题

### 🎨 界面改进
- 黑底暗金色配色替代原有的青紫色配色
- 上下分割布局替代左右分割
- 按钮改为圆形，红色（加密）和绿色（解密）
- 所有对话框添加锁图标
- 历史面板按钮改为小图标按钮（带tooltip）

### 🔧 技术改进
- 单元测试覆盖率 > 90%
- 属性测试（Property-Based Testing）12个正确性属性
- Windows平台集成测试
- 完整的类型注解
- 详细的文档字符串

### 📝 文档
- 完整的README.md
- Windows集成测试报告
- 项目状态总结
- API文档
- 使用示例和FAQ

### 🔒 安全性
- 使用行业标准加密算法
- 密码安全存储在系统Keychain
- 文件完整性HMAC验证
- 安全的密钥派生（200,000轮PBKDF2）

### ⚡ 性能
- 支持100MB文件加密（<10秒）
- 高效的密钥派生
- 低内存占用

### 📦 平台支持
- Windows 10+ ✅
- macOS 10.14+ ✅
- Linux (主流发行版) ✅

### 依赖版本
- Python 3.8+
- cryptography 47.0.0
- keyring 25.7.0
- PySide6 6.11.1
- click 8.1.8
- pyyaml 6.0
- python-dotenv 1.0.0

---

## [1.0.0-rc1] - 2025-01-XX

### 第一个发布候选版本

#### 新增
- 核心加密引擎实现
- CLI基础命令
- GUI基本界面
- Library API

#### 已知问题
- Windows环境UTF-8 BOM兼容性问题（已在1.0.0修复）

---

## 版本说明

### 版本号规则

ConfigCrypt遵循 [语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号（Major）**: 不兼容的API更改
- **次版本号（Minor）**: 向后兼容的新功能
- **修订号（Patch）**: 向后兼容的问题修复

### 更新类型

- **新增 (Added)**: 新功能
- **变更 (Changed)**: 现有功能的更改
- **废弃 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug修复
- **安全 (Security)**: 安全问题修复

---

## 如何升级

### 从源码升级

```bash
cd configcrypt
git pull origin main
pip install -e .
```

### 从PyPI升级

```bash
pip install --upgrade configcrypt
```

### 升级注意事项

- ✅ 加密文件格式向后兼容
- ✅ 主密码保持不变
- ✅ 操作历史自动迁移
- ⚠️ 首次使用新版本建议备份重要文件

---

## 反馈和建议

如果您有任何问题或建议，请：

1. [创建Issue](https://github.com/transcentlin/configcrypt/issues/new)
2. [提交Pull Request](https://github.com/transcentlin/configcrypt/pulls)
3. [发送邮件](mailto:transcentlin@gmail.com)

感谢您使用ConfigCrypt！

---

[Unreleased]: https://github.com/transcentlin/configcrypt/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/transcentlin/configcrypt/releases/tag/v1.0.1
[1.0.0]: https://github.com/transcentlin/configcrypt/releases/tag/v1.0.0
[1.0.0-rc1]: https://github.com/transcentlin/configcrypt/releases/tag/v1.0.0-rc1
