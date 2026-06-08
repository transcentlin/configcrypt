# 🔐 ConfigCrypt - 文件加密工具

<div align="center">

**安全 · 简洁 · 高效**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com)

一个简单、安全、跨平台的文件加密工具，支持命令行、图形界面和Python API三种使用方式。

[快速开始](#快速开始) · [功能特性](#功能特性) · [安装](#安装) · [使用文档](#使用文档) · [API文档](#library-api)

</div>

---

## 📖 简介

ConfigCrypt 是一个基于 **Fernet** (对称加密) 和 **PBKDF2** (密钥派生) 的文件加密工具。它可以帮助您安全地加密配置文件、密钥、凭证等敏感数据，并提供直观的图形界面和强大的命令行工具。

### 为什么选择 ConfigCrypt？

- 🔒 **安全可靠** - 使用行业标准的加密算法（Fernet + PBKDF2-HMAC-SHA256）
- 🎨 **界面美观** - 黑底暗金色高级UI设计
- 🖥️ **跨平台** - 完美支持 Windows、macOS、Linux
- 🔑 **Keychain集成** - 主密码安全存储在系统密钥链
- 📦 **多种接口** - CLI命令行、GUI图形界面、Python Library API
- 📄 **格式支持** - 原生支持 JSON、YAML、ENV 格式解析
- 🚀 **零配置** - 开箱即用，无需复杂设置

---

## ✨ 功能特性

### 🎯 核心功能

- **文件加密/解密** - 支持任意文件类型加密
- **主密码管理** - 基于系统Keychain的安全密码存储
- **格式解析** - 解密后自动解析 JSON/YAML/ENV 格式
- **操作历史** - 记录所有加密/解密操作
- **文件拖拽** - GUI支持拖拽文件加密
- **编辑器集成** - 解密后直接打开编辑器

### 🎨 界面特点

- **黑底暗金色配色** - 低调奢华的视觉体验
- **上下分割布局** - 拖拽区 + 操作历史
- **智能文件识别** - 自动识别 .enc 加密文件
- **实时反馈** - 密码强度、操作进度实时显示

---

## 🚀 快速开始

### 1. 安装

```bash
pip install configcrypt
```

### 2. 初始化（设置主密码）

```bash
cc init
```

### 3. 加密文件

```bash
# 加密文件（会删除原文件）
cc encrypt config.json

# 保留原文件
cc encrypt config.json --keep

# 指定输出路径
cc encrypt config.json --out encrypted_config.enc
```

### 4. 解密文件

```bash
# 解密文件
cc decrypt config.json.enc

# 解密并打开编辑器
cc decrypt config.json.enc --open

# 指定编辑器
cc decrypt config.json.enc --open --editor notepad
```

### 5. 使用GUI

```bash
# 启动图形界面（推荐方式）
python run.py

# 或者双击 Windows 启动文件
🔐 启动ConfigCrypt.bat
```

---

## 📦 安装

### 方式一：通过 pip 安装（推荐）

```bash
pip install configcrypt
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/configcrypt.git
cd configcrypt

# 安装依赖
pip install -e .
```

### 系统要求

- **Python:** 3.8 或更高版本
- **操作系统:** Windows 10+, macOS 10.14+, Linux (主流发行版)

### 依赖包

- `cryptography` - 加密引擎
- `keyring` - 系统Keychain集成
- `click` - CLI命令行框架
- `PySide6` - GUI图形界面
- `pyyaml` - YAML格式支持
- `python-dotenv` - ENV格式支持

---

## 📚 使用文档

### CLI 命令行

#### 初始化主密码

```bash
cc init
```

首次使用时需要设置主密码。密码要求：
- 至少8个字符
- 支持任意字符组合
- 系统会显示密码强度（弱/中/强）

#### 加密文件

```bash
# 基本用法
cc encrypt <文件路径>

# 常用选项
cc encrypt config.json              # 加密文件（删除原文件）
cc encrypt config.json --keep       # 保留原文件
cc encrypt config.json --out secret.enc  # 指定输出路径
```

**加密后的文件：**
- 文件名：`原文件名.enc`
- 格式：`[16字节盐值] + [Fernet加密数据]`
- 扩展名：`.enc`

#### 解密文件

```bash
# 基本用法
cc decrypt <加密文件路径>

# 常用选项
cc decrypt config.json.enc                    # 解密文件
cc decrypt config.json.enc --out config.json  # 指定输出路径
cc decrypt config.json.enc --open             # 解密后打开编辑器
cc decrypt config.json.enc --open --editor code  # 指定编辑器(VS Code)
```

**支持的编辑器：**
- Windows: `notepad`, `notepad++`, `code`
- macOS: `code`, `subl`, `open -e`
- Linux: `code`, `gedit`, `nano`, `vim`

#### 查看状态

```bash
cc status
```

显示信息：
- Keychain状态（可用/不可用）
- 主密码状态（已设置/未设置）
- 密码强度

#### 修改主密码

```bash
cc reset-password
```

需要：
1. 验证当前密码
2. 输入新密码
3. 确认新密码

---

### GUI 图形界面

#### 启动GUI

**Windows:**
```bash
# 方式1：双击启动文件
🔐 启动ConfigCrypt.bat

# 方式2：命令行启动
python run.py
```

**macOS / Linux:**
```bash
python run.py
```

#### 主界面功能

**上半部分 - 拖拽区：**
- 拖拽文件到此处进行加密/解密
- 左侧红色按钮：加密
- 右侧绿色按钮：解密
- 中间锁图标：视觉标识

**下半部分 - 操作历史：**
- 显示所有加密/解密操作记录
- 列：时间、操作、文件、输出、状态
- 刷新按钮：🔄 刷新历史
- 清除按钮：🗑️ 清除所有历史

#### 首次启动

首次启动会弹出"欢迎向导"，引导您设置主密码。

#### 加密流程

1. 点击"加密"按钮或拖拽明文文件
2. 选择文件
3. 在对话框中选择是否删除原文件
4. 选择输出位置
5. 等待加密完成

#### 解密流程

1. 点击"解密"按钮或拖拽 .enc 文件
2. 输入主密码验证
3. 选择是否打开编辑器
4. 选择输出位置
5. 等待解密完成

#### 菜单功能

- **文件菜单**
  - 打开文件 (Ctrl+O)
  - 退出 (Ctrl+Q)

- **查看菜单**
  - 显示/隐藏历史面板

- **设置菜单**
  - 首选项（修改主密码）

- **帮助菜单**
  - 关于

---

### Library API

ConfigCrypt 也可以作为Python库在其他项目中使用。

#### 基本用法

```python
from configcrypt import VaultAPI

# 创建API实例
api = VaultAPI()

# 解密文件为字符串
content = api.decrypt_file("config.json.enc")
print(content)

# 解密JSON文件
config = api.decrypt_json("config.json.enc")
print(config["api_key"])

# 解密YAML文件
settings = api.decrypt_yaml("settings.yaml.enc")
print(settings["database"]["host"])

# 解密ENV文件
env_vars = api.decrypt_env(".env.enc")
print(env_vars["API_KEY"])
```

#### 使用自定义密码

```python
from configcrypt import VaultAPI

# 使用自定义密码（不从Keychain读取）
api = VaultAPI(password="your_password_here")

data = api.decrypt_json("config.json.enc")
```

#### API方法

##### `decrypt_file(file_path: str | Path) -> str`

解密文件并返回字符串内容。

```python
content = api.decrypt_file("secret.txt.enc")
```

##### `decrypt_json(file_path: str | Path) -> dict`

解密JSON文件并返回字典。

```python
data = api.decrypt_json("config.json.enc")
print(data["key"])
```

##### `decrypt_yaml(file_path: str | Path) -> dict`

解密YAML文件并返回字典。

```python
config = api.decrypt_yaml("settings.yaml.enc")
print(config["database"])
```

##### `decrypt_env(file_path: str | Path) -> dict`

解密ENV文件并返回键值对字典。

```python
env = api.decrypt_env(".env.enc")
print(env["DATABASE_URL"])
```

#### 异常处理

```python
from configcrypt import VaultAPI
from configcrypt.core.exceptions import (
    DecryptionError,
    InvalidTokenError,
    ParseError,
)

api = VaultAPI()

try:
    data = api.decrypt_json("config.json.enc")
except DecryptionError:
    print("密码错误或文件损坏")
except InvalidTokenError:
    print("文件已被篡改")
except ParseError as e:
    print(f"JSON解析失败: {e}")
except FileNotFoundError:
    print("文件不存在")
```

---

## 🔒 安全性

### 加密算法

- **对称加密:** Fernet (AES-128-CBC + HMAC-SHA256)
- **密钥派生:** PBKDF2-HMAC-SHA256（200,000轮迭代）
- **盐值:** 每次加密生成16字节随机盐值
- **完整性:** HMAC验证，防止篡改

### 主密码存储

- **Windows:** Windows Credential Manager
- **macOS:** macOS Keychain
- **Linux:** Secret Service (如 GNOME Keyring)

### 安全建议

1. ✅ **使用强密码** - 至少8个字符，包含大小写字母、数字、符号
2. ✅ **定期更换密码** - 建议每3-6个月更换一次
3. ✅ **备份加密文件** - 加密文件丢失无法恢复
4. ✅ **保护主密码** - 忘记主密码无法解密文件
5. ⚠️ **不要共享密码** - 主密码仅自己知道

---

## 📁 支持的文件格式

ConfigCrypt 支持加密任何文件，但对以下格式提供原生解析支持：

| 格式 | 扩展名 | Library API | 说明 |
|------|--------|-------------|------|
| **JSON** | `.json` | `decrypt_json()` | 自动解析为Python字典 |
| **YAML** | `.yaml`, `.yml` | `decrypt_yaml()` | 自动解析为Python字典 |
| **ENV** | `.env` | `decrypt_env()` | 自动解析为键值对字典 |
| **文本** | `.txt`, `.md`, 等 | `decrypt_file()` | 返回字符串内容 |
| **其他** | 任意格式 | `decrypt_file()` | 返回原始字节内容 |

---

## 🎯 使用场景

### 1. 配置文件加密

```bash
# 加密API密钥配置
cc encrypt config.json --keep

# 提交到Git（只提交.enc文件）
git add config.json.enc
git commit -m "Add encrypted config"
```

### 2. 环境变量保护

```bash
# 加密.env文件
cc encrypt .env

# 在应用中使用
python
>>> from configcrypt import VaultAPI
>>> api = VaultAPI()
>>> env = api.decrypt_env(".env.enc")
>>> import os
>>> os.environ.update(env)
```

### 3. 数据库凭证

```yaml
# database.yaml
database:
  host: localhost
  port: 5432
  username: admin
  password: secret_password_123
```

```bash
cc encrypt database.yaml
```

```python
from configcrypt import VaultAPI

api = VaultAPI()
db_config = api.decrypt_yaml("database.yaml.enc")

# 使用数据库配置
conn = psycopg2.connect(
    host=db_config["database"]["host"],
    port=db_config["database"]["port"],
    user=db_config["database"]["username"],
    password=db_config["database"]["password"]
)
```

### 4. 私钥保护

```bash
# 加密SSH私钥
cc encrypt ~/.ssh/id_rsa --out ~/.ssh/id_rsa.enc

# 解密使用
cc decrypt ~/.ssh/id_rsa.enc --out ~/.ssh/id_rsa_temp
ssh -i ~/.ssh/id_rsa_temp user@server
rm ~/.ssh/id_rsa_temp
```

---

## ❓ 常见问题 (FAQ)

### Q1: 忘记主密码怎么办？

**A:** 很遗憾，主密码忘记后无法恢复。ConfigCrypt不存储主密码的任何形式，只存储在系统Keychain中。如果忘记密码，已加密的文件将无法解密。

**建议：**
- 设置一个您能记住的强密码
- 将密码记录在安全的地方（如密码管理器）
- 定期备份未加密的文件

### Q2: 可以在多台电脑上使用吗？

**A:** 可以，但需要在每台电脑上使用**相同的主密码**。ConfigCrypt的主密码存储在本地系统Keychain中，不同电脑的Keychain是独立的。

**建议：**
- 在所有电脑上设置相同的主密码
- 或者使用 Library API 时手动指定密码

### Q3: 加密文件可以分享给他人吗？

**A:** 可以，但对方需要：
1. 安装ConfigCrypt
2. 知道您的主密码
3. 在他们的系统上设置相同的主密码

**更安全的方式：**
- 使用非对称加密（如GPG）进行文件共享
- ConfigCrypt主要用于个人敏感文件保护

### Q4: 加密文件可以移动或重命名吗？

**A:** 可以！加密文件可以随意移动、重命名、复制。只要文件内容没有被修改，就可以正常解密。

### Q5: GUI和CLI可以混用吗？

**A:** 完全可以！GUI和CLI使用相同的加密引擎和主密码（从Keychain读取）。您可以用CLI加密，用GUI解密，反之亦然。

### Q6: 支持批量加密吗？

**A:** 当前版本不支持批量加密。您可以使用脚本循环调用CLI命令：

```bash
for file in *.json; do
    cc encrypt "$file" --keep
done
```

### Q7: 如何卸载ConfigCrypt？

```bash
pip uninstall configcrypt
```

**清理数据：**
- 删除 `~/.configcrypt/` 目录（操作历史）
- 从系统Keychain中删除ConfigCrypt条目

### Q8: 加密文件占用多大空间？

加密文件大小 ≈ 原文件大小 + 60字节（盐值16字节 + Fernet开销）

---

## 🛠️ 开发与测试

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd configcrypt

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行属性测试（基于 Hypothesis）
pytest tests/unit/test_properties.py

# 查看测试覆盖率
pytest --cov=configcrypt --cov-report=html
open htmlcov/index.html  # 查看覆盖率报告
```

### 手动测试

```bash
# CLI测试
python -c "from configcrypt.cli import main; main()" -- init
python -c "from configcrypt.cli import main; main()" -- encrypt test.txt

# GUI测试
python run.py

# API测试
python tests/integration/test_api_integration.py
```

### 项目结构

```
configcrypt/
├── .github/                              # GitHub 配置
│   └── workflows/
│       ├── README.md                     # CI/CD 工作流说明
│       └── test.yml                      # GitHub Actions 测试工作流
│
├── src/                                  # 源代码目录
│   └── configcrypt/                      # 主包
│       ├── __init__.py                   # 包初始化（导出 VaultAPI）
│       │
│       ├── cli/                          # 命令行界面模块
│       │   ├── __init__.py               # CLI 入口
│       │   └── commands.py               # CLI 命令实现 (init, encrypt, decrypt, status, reset-password)
│       │
│       ├── core/                         # 核心功能模块
│       │   ├── __init__.py               # 核心模块初始化
│       │   ├── editor_launcher.py        # 编辑器启动器
│       │   ├── exceptions.py             # 自定义异常类 (DecryptionError, InvalidTokenError, etc.)
│       │   ├── format_parser.py          # 格式解析器 (JSON/YAML/ENV)
│       │   ├── keychain_store.py         # 系统 Keychain 存储 (Windows/macOS/Linux)
│       │   └── vault.py                  # 加密/解密核心逻辑 (Vault, VaultAPI)
│       │
│       ├── gui/                          # 图形界面模块
│       │   ├── __init__.py               # GUI 模块初始化
│       │   ├── app.py                    # GUI 应用主入口
│       │   ├── dialogs.py                # 对话框组件 (密码输入、确认、进度等)
│       │   ├── history.py                # 操作历史记录管理
│       │   ├── history_panel.py          # 历史面板 UI
│       │   └── main_window.py            # 主窗口 UI (拖拽区 + 历史记录)
│       │
│       └── utils/                        # 工具模块
│           ├── __init__.py               # 工具模块初始化
│           └── password_strength.py      # 密码强度计算
│
├── tests/                                # 测试目录
│   ├── __init__.py                       # 测试包初始化
│   │
│   ├── cli/                              # CLI 测试
│   │   ├── __init__.py
│   │   ├── test_cli_commands.py          # CLI 命令测试
│   │   └── test_cli_extended_commands.py # CLI 扩展命令测试
│   │
│   ├── gui/                              # GUI 测试
│   │   ├── __init__.py
│   │   ├── test_dialogs.py               # 对话框测试
│   │   ├── test_drop_zone_widget.py      # 拖放组件测试
│   │   ├── test_dropzone_ui.py           # 拖放UI测试
│   │   ├── test_file_type_recognition.py # 文件类型识别测试
│   │   └── test_main_window.py           # 主窗口测试
│   │
│   ├── integration/                      # 集成测试
│   │   ├── __init__.py
│   │   └── test_api_integration.py       # API 集成测试
│   │
│   └── unit/                             # 单元测试
│       ├── __init__.py
│       ├── test_editor_launcher.py       # 编辑器启动器测试
│       ├── test_format_parser.py         # 格式解析器测试
│       ├── test_keychain_acceptance.py   # Keychain 验收测试
│       ├── test_keychain_store.py        # Keychain 存储测试
│       ├── test_properties.py            # 属性测试 (Hypothesis PBT - 12个正确性属性)
│       ├── test_vault.py                 # Vault 核心测试
│       ├── test_vault_api.py             # Vault API 测试
│       ├── test_vault_file_operations.py # 文件操作测试
│       └── test_vault_format.py          # 格式测试
│
├── .gitignore                            # Git 忽略规则
├── build_executable.py                   # PyInstaller 构建脚本
├── CHANGELOG.md                          # 变更日志
├── DISTRIBUTION_GUIDE.md                 # 分发指南
├── GITHUB_RELEASE_GUIDE.md               # GitHub 发布指南
├── LICENSE                               # MIT 许可证
├── PYPI_RELEASE_GUIDE.md                 # PyPI 发布指南
├── pyproject.toml                        # 项目配置 (PEP 518)
├── README.md                             # 项目说明文档
└── TESTING_EXPLAINED.md                  # 测试说明文档
```

**文件统计：**
- 源代码：17个 Python 文件
- 测试文件：18个测试文件
- 文档文件：6个 Markdown 文档
- 配置文件：3个 (pyproject.toml, .gitignore, test.yml)
- 脚本文件：1个 (build_executable.py)
- **总计：45个文件**

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🤝 贡献

欢迎贡献代码、报告问题、提出建议！

### 报告问题

如果您发现 bug 或有功能建议，请创建 Issue 并提供：
- 详细的问题描述
- 复现步骤
- 您的系统环境（操作系统、Python 版本）
- 错误信息或截图

### 开发贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 编写代码和测试
4. 确保所有测试通过 (`pytest`)
5. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 风格指南
- 添加适当的类型注解
- 为新功能编写测试
- 更新相关文档

---

## 📞 联系方式

- **项目:** ConfigCrypt File Encryption Tool
- **版本:** v1.0.0
- **许可证:** MIT License

---

## 🙏 致谢

感谢以下开源项目：

- [cryptography](https://cryptography.io/) - 加密库
- [keyring](https://github.com/jaraco/keyring) - Keychain集成
- [PySide6](https://www.qt.io/qt-for-python) - GUI框架
- [click](https://click.palletsprojects.com/) - CLI框架

---

## ⭐ 功能特色

- ✅ **测试覆盖率 90%+** - 包含单元测试、CLI测试、GUI测试、集成测试
- ✅ **属性测试** - 使用 Hypothesis 进行基于属性的测试
- ✅ **CI/CD** - GitHub Actions 自动化测试（Windows/macOS/Linux）
- ✅ **类型注解** - 完整的类型提示，支持 IDE 智能提示
- ✅ **文档完善** - 详细的 README、API 文档、测试报告

---

<div align="center">

**ConfigCrypt** - 让文件加密变得简单安全

Made with ❤️ using Python

</div>
