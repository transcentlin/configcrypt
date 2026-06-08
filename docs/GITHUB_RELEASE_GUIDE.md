# 🐙 ConfigCrypt GitHub 发布完整操作指南

## 📋 发布流程图

```mermaid
flowchart TD
    A[开始] --> B[创建 GitHub 仓库]
    B --> C[初始化本地 Git]
    C --> D[创建 .gitignore]
    D --> E[首次提交代码]
    E --> F[关联远程仓库]
    F --> G[推送代码到 GitHub]
  
    G --> H[创建 Release Tag]
    H --> I[编写 Release Notes]
    I --> J[上传发布文件<br/>ConfigCrypt.exe]
    J --> K[发布 Release]
  
    K --> L[验证 Release]
    L --> M[更新 README Badge]
    M --> N[发布完成 🎉]
  
    style A fill:#e1f5e1
    style N fill:#e1f5e1
    style B fill:#d1ecf1
    style H fill:#fff3cd
    style K fill:#28a745
```

---

## 📝 详细操作步骤

### Step 1: 创建 GitHub 仓库

#### 1.1 登录 GitHub

访问: https://github.com
登录您的账号

#### 1.2 创建新仓库

1. 点击右上角 **+** → **New repository**
2. 填写仓库信息:

   - **Repository name**: `configcrypt` 或 `configcrypt-cli`
   - **Description**: `🔐 A simple, secure, cross-platform file encryption tool with CLI, GUI, and Python API`
   - **Public** ✅ （开源项目）或 **Private** （私有项目）
   - **不要勾选** "Initialize this repository with:"
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license
   - （我们本地已有这些文件）
3. 点击 **Create repository**

#### 1.3 记录仓库地址

创建后会显示仓库 URL，例如:

```
https://github.com/transcentlin/configcrypt.git
```

#### 1.4 生成 Personal Access Token（重要！）

**为什么需要 Token？**

- GitHub 已不再支持使用密码进行 Git 推送
- 需要使用 Personal Access Token (PAT) 作为密码
- 建议在创建仓库后立即生成，后续推送代码时需要使用

**生成步骤：**

1. 访问 GitHub → 右上角头像 → **Settings**
2. 左侧菜单 → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. 点击 **Generate new token** → **Generate new token (classic)**
4. 填写表单：
   - **Note**: `ConfigCrypt Repo Access`（Token 用途说明）
   - **Expiration**: `90 days` 或 `Custom`（有效期）
   - **Select scopes**: 勾选 `repo`（完整仓库访问权限）✅
5. 点击页面底部的 **Generate token** 按钮
6. **⚠️ 立即复制 Token！**（只显示一次，刷新页面后无法再看到）

**保存 Token：**

- 将 Token 复制到安全的地方（如密码管理器）
- 后续推送代码时会用到
- 格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`（40个字符）

**⚠️ 重要提示：**

- Token 等同于密码，不要泄露给他人
- 不要提交到 Git 仓库
- 如果泄露，立即在 GitHub 删除该 Token 并重新生成

---

### Step 2: 准备本地 Git 仓库

**⚠️ 重要：以下所有命令都必须在项目根目录下执行！**

```bash
# Windows PowerShell 示例
cd "D:\同步盘\BaiduSyncdisk\Antigravity\ProjectAsset\核心配置文件加密 260605"

# 或使用相对路径进入项目目录
cd path\to\your\configcrypt\project
```

#### 2.1 检查 Git 是否已初始化

```bash
# 检查是否已有 .git 目录
dir /a .git
```

**如果已存在 .git 目录**，跳到 Step 2.3

**如果不存在**，继续执行 2.2

#### 2.2 初始化 Git 仓库

```bash
# 初始化 Git
git init

# 配置用户信息（如果未配置）
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### 2.3 创建 .gitignore 文件

```bash
# 创建 .gitignore
type nul > .gitignore
```

**编辑 `.gitignore` 内容**:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.hypothesis/

# PyInstaller
*.spec
build/

# Distribution
dist/
*.whl
*.tar.gz

# Temporary files
*.log
*.tmp
temp/
tmp/

# OS
.DS_Store
Thumbs.db
desktop.ini

# ConfigCrypt specific
.configcrypt/
*.enc

# Sensitive files
.pypirc
.env
credentials.json
```

---

### Step 3: 首次提交代码

#### 3.1 查看文件状态

```bash
git status
```

#### 3.2 添加所有文件

```bash
# 添加所有文件到暂存区
git add .

# 检查将要提交的文件
git status
```

#### 3.3 首次提交

```bash
git commit -m "Initial commit: ConfigCrypt v1.0.0

- 实现文件加密/解密核心功能
- 添加 CLI 命令行工具 (kv)
- 实现 GUI 图形界面
- 提供 Library API
- 支持 JSON/YAML/ENV 格式解析
- 集成系统 Keychain 密码管理
- 完整测试覆盖 (90%+)
- Windows/macOS/Linux 跨平台支持"
```

---

### Step 4: 关联远程仓库并推送

#### 4.1 添加远程仓库

```bash
# 替换为您的仓库地址
git remote add origin https://github.com/transcentlin/configcrypt.git
```

#### 4.2 创建主分支

```bash
# 确保主分支名称为 main
git branch -M main
```

#### 4.3 首次推送

```bash
# 推送代码到 GitHub
git push -u origin main
```

**首次推送可能需要输入 GitHub 凭据**:

- Username: 您的 GitHub 用户名
- Password: **Personal Access Token**（不是账号密码）

**如何生成 Personal Access Token**:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 填写:
   - Note: `ConfigCrypt Repo Access`
   - Expiration: 90 days 或 Custom
   - 勾选 scopes: `repo` (完整仓库访问)
4. 点击 **Generate token**
5. **立即复制 token**（只显示一次）

#### 4.4 验证推送

访问 GitHub 仓库页面，应该能看到所有文件已上传。

---

### Step 5: 创建 Release Tag

#### 5.1 创建本地 Tag

```bash
# 创建 v1.0.0 标签
git tag -a v1.0.0 -m "Release version 1.0.0

ConfigCrypt - 文件加密工具首次正式版本

主要特性:
- 安全的文件加密/解密 (Fernet + PBKDF2)
- 命令行工具 (CLI)
- 图形用户界面 (GUI)
- Python Library API
- 跨平台支持 (Windows/macOS/Linux)
- 系统 Keychain 集成

完整功能列表请查看 README.md"
```

#### 5.2 推送 Tag 到 GitHub

```bash
git push origin v1.0.0
```

#### 5.3 验证 Tag

```bash
# 查看本地所有标签
git tag

# 查看标签详情
git show v1.0.0
```

---

### Step 6: 在 GitHub 创建 Release

#### 6.1 访问 Release 页面

1. 打开 GitHub 仓库页面
2. 点击右侧 **Releases** → **Create a new release**

#### 6.2 选择 Tag

- **Choose a tag**: 选择 `v1.0.0`（刚刚推送的）
- 或者点击 "Create new tag on publish" 输入 `v1.0.0`

#### 6.3 填写 Release 标题

```
🔐 ConfigCrypt v1.0.0 - 首次正式发布
```

#### 6.4 编写 Release Notes

**复制以下内容到描述框**:

```markdown
# 🎉 ConfigCrypt v1.0.0 首次正式发布

ConfigCrypt 是一个简单、安全、跨平台的文件加密工具，提供 CLI、GUI 和 Python API 三种使用方式。

---

## ✨ 主要特性

### 🔒 核心功能
- **文件加密/解密** - 基于 Fernet (AES-128-CBC) + PBKDF2-HMAC-SHA256
- **主密码管理** - 安全存储在系统 Keychain (Windows/macOS/Linux)
- **格式解析** - 原生支持 JSON、YAML、ENV 格式
- **操作历史** - 记录所有加密/解密操作

### 🎨 用户界面
- **CLI 命令行** - `cc init/encrypt/decrypt/status/reset-password`
- **GUI 图形界面** - 黑底暗金色高级 UI，支持文件拖拽
- **Library API** - `VaultAPI` 类，方便集成到其他 Python 项目

### 🖥️ 跨平台支持
- ✅ Windows 10+
- ✅ macOS 10.14+
- ✅ Linux (主流发行版)

---

## 📦 安装方式

### 方式一：通过 PyPI 安装
```bash
pip install configcrypt-cli
```

### 方式二：下载独立可执行文件

- **Windows**: 下载 `ConfigCrypt.exe` (本页面下方 Assets)
- 双击运行，无需安装 Python

### 方式三：从源码安装

```bash
git clone https://github.com/transcentlin/configcrypt.git
cd configcrypt
pip install -e .
```

---

## 🚀 快速开始

### CLI 使用

```bash
# 初始化主密码
cc init

# 加密文件
cc encrypt secret.json

# 解密文件
cc decrypt secret.json.enc
```

### GUI 使用

```bash
# Windows
python run.py

# 或双击
🔐 启动ConfigCrypt.bat
```

### Library API 使用

```python
from configcrypt import VaultAPI

api = VaultAPI()
config = api.decrypt_json("config.json.enc")
```

---

## 📋 完整功能列表

### CLI 命令

- `cc init` - 设置主密码
- `cc encrypt <file>` - 加密文件
- `cc decrypt <file>` - 解密文件
- `cc status` - 查看状态
- `cc reset-password` - 修改主密码

### GUI 功能

- 文件拖拽加密/解密
- 欢迎向导（首次启动）
- 操作历史记录
- 密码强度显示
- 编辑器集成

### API 方法

- `decrypt_file()` - 解密为字符串
- `decrypt_json()` - 解密 JSON
- `decrypt_yaml()` - 解密 YAML
- `decrypt_env()` - 解密 ENV

---

## 🛡️ 安全性

- **加密算法**: Fernet (AES-128-CBC + HMAC-SHA256)
- **密钥派生**: PBKDF2-HMAC-SHA256 (200,000 轮)
- **完整性验证**: HMAC 防篡改
- **密码存储**: 系统 Keychain 安全存储

---

## 📊 测试覆盖

- ✅ 单元测试覆盖率: **90%+**
- ✅ 属性测试 (Hypothesis): **12 个正确性属性**
- ✅ CLI 测试: 完整
- ✅ GUI 测试: 手动验证通过
- ✅ 集成测试: Windows 平台完整测试

---

## 📚 文档

- [完整文档](https://github.com/transcentlin/configcrypt#readme)
- [安装指南](https://github.com/transcentlin/configcrypt#installation)
- [使用示例](https://github.com/transcentlin/configcrypt#usage)
- [API 文档](https://github.com/transcentlin/configcrypt#library-api)
- [FAQ](https://github.com/transcentlin/configcrypt#faq)

---

## 🐛 已知问题

- Linux 平台 Keychain 支持依赖 Secret Service (GNOME Keyring)
- macOS 首次使用需要授权 Keychain 访问

---

## 🔜 下一版本计划 (v1.1.0)

- [ ] 批量加密/解密
- [ ] macOS 平台完整测试
- [ ] Linux 平台完整测试
- [ ] 性能优化（大文件处理）
- [ ] 多语言界面支持

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**贡献指南**:

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

感谢以下开源项目:

- [cryptography](https://cryptography.io/)
- [keyring](https://github.com/jaraco/keyring)
- [PySide6](https://www.qt.io/qt-for-python)
- [click](https://click.palletsprojects.com/)

---

## 📞 联系方式

- **Issues**: https://github.com/transcentlin/configcrypt/issues
- **Discussions**: https://github.com/transcentlin/configcrypt/discussions

---

**完整更新日志**: [CHANGELOG.md](https://github.com/transcentlin/configcrypt/blob/main/CHANGELOG.md)

```

---

### Step 7: 上传发布文件

#### 7.1 准备发布文件

**文件清单**:
- `ConfigCrypt.exe` - Windows 独立可执行文件 (51.32 MB)
- `configcrypt-1.0.0-py3-none-any.whl` - Python Wheel 包
- `configcrypt-1.0.0.tar.gz` - 源码包

**可选文件**:
- `CHANGELOG.md` - 更新日志
- `README.pdf` - 文档 PDF 版本

#### 7.2 上传到 Release

在 Release 编辑页面:

1. 滚动到底部 **Attach binaries** 部分
2. 拖拽或点击上传以下文件:
```

   ✅ dist/ConfigCrypt.exe
   ✅ dist/configcrypt_cli-1.0.0-py3-none-any.whl  (如果改了包名)
   ✅ dist/configcrypt_cli-1.0.0.tar.gz

```

3. 等待上传完成（可能需要几分钟）

#### 7.3 设置为 Latest Release

- ✅ 勾选 **Set as the latest release**
- ❌ 不勾选 "Set as a pre-release"（这不是预发布版）

#### 7.4 发布 Release

点击 **Publish release** 按钮

---

### Step 8: 验证 Release

#### 8.1 检查 Release 页面

访问: `https://github.com/transcentlin/configcrypt/releases/tag/v1.0.0`

**验证内容**:
- ✅ Release 标题正确
- ✅ Release Notes 完整
- ✅ Tag 版本正确 (v1.0.0)
- ✅ 文件已上传 (Assets 部分)
- ✅ 文件大小正确
- ✅ 标记为 Latest Release

#### 8.2 测试下载

1. 点击 `ConfigCrypt.exe` 下载
2. 验证文件大小和完整性
3. 双击运行测试

---

### Step 9: 更新 README.md

#### 9.1 添加 Badges

在 README.md 顶部添加:

```markdown
[![GitHub release](https://img.shields.io/github/v/release/transcentlin/configcrypt)](https://github.com/transcentlin/configcrypt/releases/latest)
[![PyPI version](https://badge.fury.io/py/configcrypt-cli.svg)](https://badge.fury.io/py/configcrypt-cli)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/transcentlin/configcrypt)
```

#### 9.2 更新 GitHub URL

将所有占位符 URL 替换为实际仓库地址:

**查找替换**:

- `https://github.com/transcentlin/configcrypt` → 实际 URL（已完成）
- `transcentlin` → 您的 GitHub 用户名（已完成）

#### 9.3 提交更新

```bash
git add README.md
git commit -m "docs: add release badges and update URLs"
git push origin main
```

---

### Step 10: 设置仓库配置（可选）

#### 10.1 添加 Topics (标签)

在仓库主页:

1. 点击 **About** 旁边的 ⚙️ (设置图标)
2. 添加 Topics:
   ```
   encryption, security, cli, gui, python, cryptography, 
   file-encryption, password-manager, keychain, cross-platform
   ```

#### 10.2 设置仓库描述

```
🔐 A simple, secure, cross-platform file encryption tool with CLI, GUI, and Python API
```

#### 10.3 设置主页链接

- Website: `https://pypi.org/project/configcrypt-cli/`

#### 10.4 启用 Issues 和 Discussions

- ✅ Issues (bug 报告和功能请求)
- ✅ Discussions (社区讨论)

---

## 🔄 后续版本发布流程

### 发布新版本 (例如 v1.1.0)

```bash
# 1. 更新版本号
# 编辑 pyproject.toml: version = "1.1.0"

# 2. 更新 CHANGELOG.md
# 添加新版本的更新内容

# 3. 提交更改
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.1.0"
git push origin main

# 4. 创建新 Tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 5. 重新构建
python -m build
python build_executable.py

# 6. 上传到 PyPI
twine upload dist/*

# 7. 在 GitHub 创建新 Release
# (重复 Step 6-9)
```

---

## 📋 发布检查清单

### 准备阶段

- [ ] 代码已充分测试
- [ ] README.md 完整
- [ ] CHANGELOG.md 已更新
- [ ] LICENSE 文件存在
- [ ] 版本号正确

### Git 操作

- [ ] Git 仓库已初始化
- [ ] .gitignore 已配置
- [ ] 远程仓库已关联
- [ ] 代码已推送到 GitHub
- [ ] Tag 已创建并推送

### GitHub Release

- [ ] Release 已创建
- [ ] Release Notes 完整
- [ ] 文件已上传 (ConfigCrypt.exe 等)
- [ ] 标记为 Latest Release
- [ ] 下载链接可用

### 文档更新

- [ ] README.md badges 已添加
- [ ] GitHub URLs 已更新
- [ ] 仓库描述已设置
- [ ] Topics 已添加

### 验证

- [ ] Release 页面可访问
- [ ] 文件可正常下载
- [ ] 可执行文件可运行
- [ ] PyPI 包可安装

---

## 🎯 发布后推广（可选）

### 社区分享

- [ ] Reddit - r/Python, r/opensource
- [ ] Hacker News - Show HN
- [ ] 掘金/知乎/CSDN - 中文社区
- [ ] Twitter/X - #Python #OpenSource

### 项目推广

- [ ] Product Hunt
- [ ] AlternativeTo
- [ ] Awesome Python Lists

### 文档网站

- [ ] GitHub Pages
- [ ] Read the Docs

---

## 🆘 常见问题排查

### Q1: push 被拒绝 "remote contains work that you do not have"

**解决**:

```bash
git pull origin main --rebase
git push origin main
```

### Q2: 无法推送大文件 (>100MB)

**原因**: GitHub 限制单文件最大 100MB

**解决**:

1. 使用 Git LFS (Large File Storage)
2. 或将大文件放在 Release Assets（不放入 Git）

### Q3: Personal Access Token 失效

**解决**:

1. 生成新 Token
2. 更新本地凭据:
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/transcentlin/configcrypt.git
   ```

### Q4: Release 编辑后无法保存

**原因**: Markdown 格式错误

**解决**:

1. 检查 Markdown 语法
2. 使用 Preview 预览

---

## 📞 需要帮助？

- GitHub Docs: https://docs.github.com/
- Git 教程: https://git-scm.com/book/zh/v2
- Markdown 指南: https://guides.github.com/features/mastering-markdown/

---

**文档生成时间**: 2025-06-08
**适用版本**: ConfigCrypt v1.0.0
