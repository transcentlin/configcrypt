# GitHub Actions CI/CD 配置文档

本文档描述了 KeyVault 项目的 CI/CD 配置和测试策略。

## 概述

KeyVault 使用 GitHub Actions 进行持续集成和测试。我们的 CI 流水线设计为在三个主要平台上全面测试代码：

- **Ubuntu** (Linux): ubuntu-latest
- **Windows**: windows-latest  
- **macOS**: macos-latest

## 工作流文件

### test.yml

主测试工作流，包含多个并行任务：

#### 1. Test Job (测试任务)

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- Pull Request 到 `main` 或 `develop` 分支
- 每日定时运行 (UTC 00:00)

**测试矩阵:**
- 操作系统: Ubuntu, Windows, macOS
- Python 版本: 3.9, 3.10, 3.11, 3.12
- 总共 12 个测试组合

**测试步骤:**
1. **代码检出**: 使用 actions/checkout@v4
2. **Python 设置**: 配置指定版本的 Python，启用 pip 缓存
3. **系统依赖安装** (仅 Linux):
   - GUI 测试所需的 X11 库
   - Secret Service 库 (用于 Keychain)
   - Xvfb (虚拟显示服务器)
4. **Python 依赖安装**: 安装项目及开发依赖
5. **Keyring 验证**: 检查 keyring 后端可用性
6. **代码质量检查**:
   - flake8 lint 检查
   - black 格式检查
   - mypy 类型检查 (允许失败)
7. **单元测试**: 运行单元测试，生成覆盖率报告
8. **CLI 测试**: 测试命令行界面
9. **GUI 测试**:
   - Linux: 使用 xvfb-run 在虚拟显示器中运行
   - Windows/macOS: 原生运行 (允许失败)
10. **覆盖率上传**: 仅在 Ubuntu + Python 3.11 时上传到 Codecov

**超时设置:**
- 单元测试: 10 分钟
- CLI 测试: 5 分钟
- GUI 测试: 10 分钟

#### 2. Property Tests Job (属性测试任务)

**目的:** 运行基于 Hypothesis 的属性测试，验证系统的正确性属性

**测试矩阵:**
- 操作系统: Ubuntu, Windows, macOS
- Python 版本: 3.11 (单一版本以减少执行时间)

**配置:**
- Hypothesis Profile: `ci` (200 个示例)
- 超时: 30 分钟
- 启用统计信息输出

#### 3. Integration Tests Job (集成测试任务)

**依赖:** 需要主测试任务完成

**目的:** 测试系统组件集成和跨平台兼容性

**测试矩阵:**
- 操作系统: Ubuntu, Windows, macOS
- Python 版本: 3.11

**测试内容:**
- Keychain 集成 (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- 跨平台文件格式兼容性
- 超时: 10 分钟

#### 4. Performance Tests Job (性能测试任务)

**依赖:** 需要主测试任务完成

**平台:** Ubuntu (单一平台以保持一致性)

**目的:** 验证性能需求

**基准测试:**
- 1MB 文件加密 < 2 秒
- 10MB 文件加密 < 10 秒
- 100MB 文件加密 < 60 秒
- 解密时间 < 加密时间的 50%
- GUI 启动 < 3 秒

**超时:** 15 分钟

#### 5. Security Audit Job (安全审计任务)

**平台:** Ubuntu

**目的:** 检查安全漏洞

**工具:**
- **safety**: 检查依赖包的已知漏洞
- **bandit**: 静态代码安全分析

**输出:** 生成 JSON 格式的安全报告并上传为 artifact

## Hypothesis 配置

项目使用 `.hypothesis/profiles.yml` 配置多个测试 profile:

### default (默认)
- 用于本地开发
- 100 个示例
- 普通详细度

### ci (持续集成)
- 用于 GitHub Actions
- 200 个示例
- 详细输出
- 每个测试用例 5 秒超时

### dev (快速开发)
- 快速迭代
- 20 个示例
- 安静模式

### debug (调试)
- 调查失败
- 10 个示例
- 调试详细度

## Pytest 配置

在 `pyproject.toml` 中配置:

### 测试标记
- `@pytest.mark.property`: 属性测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.benchmark`: 性能基准测试

### 覆盖率配置
- 源目录: `src/`
- 忽略: 测试文件、__pycache__
- 排除行: pragma no cover, abstract methods, TYPE_CHECKING 块等

## 系统依赖

### Linux (Ubuntu)
```bash
# GUI 测试
xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 
libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 
libxcb-xinerama0 libxcb-xfixes0

# Keychain
libsecret-1-0 libdbus-1-3
```

### Windows
- Windows Credential Manager (系统内置)

### macOS
- macOS Keychain (系统内置)

## 最佳实践

### 1. 快速反馈
- 代码质量检查在前 (快速失败)
- 单元测试先于集成测试
- 使用 `fail-fast: false` 查看所有平台的结果

### 2. 超时保护
- 所有测试步骤设置合理超时
- 防止 CI 资源浪费

### 3. 平台特定处理
- Linux GUI 测试使用 Xvfb
- Windows/macOS GUI 测试允许失败 (暂时)
- 条件性安装系统依赖

### 4. 缓存优化
- 启用 pip 缓存加速依赖安装
- 减少网络 I/O

### 5. 覆盖率报告
- 仅在单一环境上传 (避免重复)
- 选择最稳定的平台 (Ubuntu + Python 3.11)

## 故障排查

### GUI 测试失败
- **Linux**: 检查 Xvfb 和 X11 库是否正确安装
- **Windows/macOS**: 当前允许失败，需要进一步调试

### Keychain 测试失败
- 检查系统依赖是否安装
- Linux: 确保 libsecret-1-0 和 D-Bus 可用
- 验证 keyring 后端输出

### 性能测试不通过
- 检查 GitHub Actions runner 规格
- 考虑调整超时或降低性能要求

### 安全审计警告
- 检查 bandit-report.json
- 评估安全建议并修复代码
- 更新有漏洞的依赖

## 本地运行

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定类型测试
```bash
# 单元测试
pytest tests/unit -v

# 属性测试
pytest -m property -v

# 集成测试
pytest -m integration -v

# 性能测试
pytest -m benchmark -v
```

### 使用特定 Hypothesis Profile
```bash
# CI profile
pytest -m property --hypothesis-profile=ci

# 快速开发
pytest -m property --hypothesis-profile=dev
```

### 检查覆盖率
```bash
pytest --cov=keyvault --cov-report=html
# 在浏览器中打开 htmlcov/index.html
```

### 代码质量检查
```bash
# Lint
flake8 src/keyvault

# 格式检查
black --check src/keyvault tests

# 格式化
black src/keyvault tests

# 类型检查
mypy src/keyvault

# 安全检查
safety check
bandit -r src/keyvault
```

## 贡献指南

在提交 Pull Request 前，请确保:

1. 所有测试通过: `pytest tests/ -v`
2. 代码已格式化: `black src/keyvault tests`
3. 无 lint 错误: `flake8 src/keyvault`
4. 覆盖率 ≥ 85%: `pytest --cov=keyvault`
5. 新功能有对应的单元测试和属性测试
6. 文档已更新

## 维护清单

### 定期任务
- [ ] 每月更新 GitHub Actions 版本
- [ ] 每季度审查依赖安全性
- [ ] 每季度评估性能基准是否需要调整
- [ ] 每半年检查 Python 版本支持策略

### 升级注意事项
- 升级 Python 版本时，更新测试矩阵
- 升级主要依赖时，运行完整测试套件
- 修改性能要求时，更新文档和测试

## 资源链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Hypothesis 文档](https://hypothesis.readthedocs.io/)
- [pytest 文档](https://docs.pytest.org/)
- [Codecov 文档](https://docs.codecov.com/)
