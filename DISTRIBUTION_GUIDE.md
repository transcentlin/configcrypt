# 📦 ConfigCrypt 分发文件完整指南

## ❓ 您的问题解答

### 问题：dist 目录下应该上传哪些文件到 PyPI？

**答案**: 上传 `.whl` 和 `.tar.gz` 文件，**不要上传 .exe 文件**！

---

## 📂 dist 目录文件说明

您的 `dist` 目录现在应该包含 3 个文件：

```
dist/
├── configcrypt-1.0.0-py3-none-any.whl    ✅ 上传到 PyPI
├── configcrypt-1.0.0.tar.gz              ✅ 上传到 PyPI
└── ConfigCrypt.exe                       ❌ 不上传到 PyPI（用于 GitHub Release）
```

### 1️⃣ `configcrypt-1.0.0-py3-none-any.whl` (约 44 KB)

**格式**: Wheel 文件（Python 预编译包）

**用途**: 
- ✅ **上传到 PyPI**
- 用户通过 `pip install configcrypt` 安装时下载的主要文件
- 安装速度快（预编译好的）

**包含内容**:
- 所有 Python 源代码（`src/configcrypt/` 下的所有 .py 文件）
- 依赖声明
- 命令行入口点配置
- LICENSE 文件

**不包含**:
- 测试代码
- 文档（除了 README）
- .exe 可执行文件

---

### 2️⃣ `configcrypt-1.0.0.tar.gz` (约 45 KB)

**格式**: 源码分发包（Source Distribution）

**用途**:
- ✅ **上传到 PyPI**
- 备用安装方式（当 wheel 不可用时）
- 用户可以查看源代码

**包含内容**:
- 所有 Python 源代码
- `pyproject.toml` 配置文件
- `README.md`
- `LICENSE`

---

### 3️⃣ `ConfigCrypt.exe` (约 51 MB)

**格式**: Windows 可执行文件（PyInstaller 打包）

**用途**:
- ❌ **不上传到 PyPI**（PyPI 不接受 .exe 文件）
- ✅ **上传到 GitHub Release**
- 用于不懂 Python 的最终用户

**包含内容**:
- 完整的 Python 运行时
- 所有 Python 源代码
- 所有依赖库
- GUI 资源

**为什么不上传到 PyPI？**
- PyPI 只接受 Python 包（.whl 和 .tar.gz）
- .exe 文件太大（51MB vs 44KB）
- 只能在 Windows 上运行（不跨平台）
- PyPI 的目的是分发 Python 包，不是可执行文件

---

## 🎯 上传到 PyPI 的正确命令

### 上传到测试环境（可选）
```bash
twine upload --repository testpypi dist/*.whl dist/*.tar.gz
```

或者只指定这两个文件：
```bash
twine upload --repository testpypi dist/configcrypt-1.0.0-py3-none-any.whl dist/configcrypt-1.0.0.tar.gz
```

### 上传到生产环境
```bash
twine upload dist/*.whl dist/*.tar.gz
```

或者：
```bash
twine upload dist/configcrypt-1.0.0-py3-none-any.whl dist/configcrypt-1.0.0.tar.gz
```

### ⚠️ 不要使用 `dist/*`

**错误命令**（会尝试上传 .exe）:
```bash
twine upload dist/*    ❌ 会包含 ConfigCrypt.exe
```

**正确命令**:
```bash
twine upload dist/*.whl dist/*.tar.gz    ✅ 只上传 Python 包
```

---

## 📊 三种分发方式对比

| 方式 | 文件 | 平台 | 目标用户 | 大小 |
|------|------|------|----------|------|
| **PyPI** | .whl + .tar.gz | PyPI 官网 | Python 开发者 | 44 KB |
| **GitHub Release** | .whl + .tar.gz + .exe + 源码 | GitHub | 所有用户 | 全部 |
| **可执行文件** | .exe | 本地/网盘 | Windows 最终用户 | 51 MB |

### PyPI 发布（Python 包）

**目标**: Python 开发者和命令行用户

**用户安装方式**:
```bash
pip install configcrypt
```

**用户使用方式**:
```bash
# CLI
cc init
cc encrypt file.txt

# Python API
from configcrypt import VaultAPI
api = VaultAPI()
```

**上传文件**:
- `configcrypt-1.0.0-py3-none-any.whl`
- `configcrypt-1.0.0.tar.gz`

---

### GitHub Release 发布（全套）

**目标**: 所有类型的用户

**包含文件**:
- 源代码压缩包（自动生成）
- `configcrypt-1.0.0-py3-none-any.whl`
- `configcrypt-1.0.0.tar.gz`
- `ConfigCrypt.exe`

**用户下载方式**:
- Python 用户下载 .whl 或 .tar.gz
- Windows 用户下载 .exe
- 开发者下载源码

---

### 可执行文件分发（独立）

**目标**: 不懂技术的 Windows 用户

**分发方式**:
- 百度网盘
- 阿里云盘
- 个人网站下载
- U盘拷贝

**优点**:
- 双击就能用
- 不需要安装 Python
- 不需要命令行

---

## 🔍 用户视角：不同安装方式

### 方式 1: 通过 PyPI 安装（开发者）

```bash
# 安装
pip install configcrypt

# 使用 CLI
cc encrypt config.json

# 使用 Python API
python
>>> from configcrypt import VaultAPI
>>> api = VaultAPI()
```

**来源**: PyPI 下载的是 `.whl` 文件

---

### 方式 2: 下载可执行文件（最终用户）

```bash
# 1. 下载 ConfigCrypt.exe
# 2. 双击运行
# 3. 使用 GUI 界面
```

**来源**: GitHub Release 或网盘下载的是 `.exe` 文件

---

## 📝 上传步骤总结

### PyPI 上传（只上传 Python 包）

```bash
# 1. 确保包已构建
python -m build

# 2. 检查文件
ls dist/
# 应该看到:
#   configcrypt-1.0.0-py3-none-any.whl
#   configcrypt-1.0.0.tar.gz
#   ConfigCrypt.exe

# 3. 上传到 PyPI（只上传前两个）
twine upload dist/*.whl dist/*.tar.gz

# 4. 验证
pip install configcrypt
cc --version
```

---

### GitHub Release 上传（上传全部）

1. 在 GitHub 创建 Release v1.0.0
2. 上传所有文件:
   - `ConfigCrypt.exe` (51 MB) - Windows 用户
   - `configcrypt-1.0.0-py3-none-any.whl` (44 KB) - Python 用户
   - `configcrypt-1.0.0.tar.gz` (44 KB) - 源码查看
3. 源代码自动打包（GitHub 自动生成 zip 和 tar.gz）

---

## ✅ 检查清单

### 上传到 PyPI 之前

- [ ] 已构建 Python 包 (`python -m build`)
- [ ] dist 目录包含 `.whl` 和 `.tar.gz` 文件
- [ ] 已配置 `.pypirc` 文件
- [ ] 已测试包 (`twine check dist/*.whl dist/*.tar.gz`)
- [ ] 版本号正确 (1.0.0)
- [ ] README 和 LICENSE 包含在包中

### 上传命令

```bash
# ✅ 正确：只上传 Python 包
twine upload dist/*.whl dist/*.tar.gz

# ❌ 错误：会尝试上传 .exe
twine upload dist/*
```

---

## 💡 最佳实践

### 1. 分离构建

**Python 包构建**:
```bash
python -m build
# 生成: .whl 和 .tar.gz
```

**可执行文件构建**:
```bash
python build_executable.py
# 生成: ConfigCrypt.exe
```

### 2. 使用不同分发渠道

- **PyPI**: 只放 Python 包（.whl + .tar.gz）
- **GitHub Release**: 放所有文件（.whl + .tar.gz + .exe）
- **个人网盘**: 只放 .exe（方便国内用户）

### 3. 清理 dist 目录

如果想重新构建，先清理：
```bash
# Windows PowerShell
Remove-Item dist\* -Force

# 重新构建
python -m build
python build_executable.py
```

---

## 🎉 总结

**您的问题**: dist 目录下只有 .exe 文件，是否只上传它？

**答案**:
1. ❌ **不要**只上传 .exe 到 PyPI（PyPI 不接受）
2. ✅ **需要**先构建 Python 包（已完成）
3. ✅ **上传** `.whl` 和 `.tar.gz` 到 PyPI
4. ✅ **保留** `.exe` 文件用于 GitHub Release

**现在您的 dist 目录正确包含**:
- `configcrypt-1.0.0-py3-none-any.whl` → PyPI
- `configcrypt-1.0.0.tar.gz` → PyPI
- `ConfigCrypt.exe` → GitHub Release

**上传到 PyPI 的命令**:
```bash
twine upload dist/*.whl dist/*.tar.gz
```

---

**文档生成时间**: 2025-06-08  
**适用版本**: ConfigCrypt v1.0.0

