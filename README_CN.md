# OfficeX

**AI 驱动的文档操作平台。** 通过 CLI 生成、验证和审计 Word 文档，可独立运行或作为 AI Agent 的 Skill 使用。

[English Documentation](README.md)

---

## 系统要求

| 组件 | 要求 |
|------|------|
| **操作系统** | macOS 10.9+（Intel）、macOS 11+（Apple Silicon）、Linux（glibc 2.28+，x86_64/aarch64） |
| **Python** | 3.11+ |
| **LibreOffice** | 可选。视觉审计（PNG 渲染）需要 |
| **API Key** | 可选。AI 驱动的 `generate` 命令需要。支持任何 OpenAI 兼容端点 |

> 当前不支持 Windows。所有原生依赖（pymupdf、lxml、numpy、Pillow）均提供 macOS 和 Linux 的预编译 wheel。

## OfficeX 是什么？

OfficeX 是一个 **AI Agent 平台**，当前的第一个垂直领域是文档操作。它解决的核心问题是：当 AI 直接通过 Python 生成大型文档时，会出现排版错位、样式漂移、分页异常、表格溢出等问题——这些问题靠文本/XML 检查根本发现不了。

OfficeX 的设计原则：
- **AI** 负责生成内容（文本、结构、审查意见）
- **确定性程序代码** 拥有文档结构（样式、排版、编号、页面几何）
- **双轨验证**（结构 + 视觉）证明输出正确

平台通过 **Skill** 扩展来覆盖不同的文档场景。当前 MVP 使用学术文档生成作为验证测试用例。

## 工作流程

```
                    ┌─────────────────────┐
                    │   用户 / Agent       │
                    │   提供 prompt        │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   AI Provider        │
                    │   生成结构化 JSON    │
                    │   内容               │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Build Source       │
                    │   manifest 驱动     │
                    │   块组装             │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   Writer             │
                    │   确定性 docx       │
                    │   生成               │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │                               │
    ┌─────────▼─────────┐          ┌──────────▼──────────┐
    │  结构验证          │          │  视觉审计            │
    │  - 页面几何        │          │  - LibreOffice 渲染  │
    │  - 样式合约        │          │  - 空白页检测        │
    │  - 图片适配        │          │  - 宽高比验证        │
    │  - 覆盖检测        │          │  - 空白间隙检测      │
    └─────────┬─────────┘          └──────────┬──────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                    ┌─────────▼───────────┐
                    │   双轨都通过？       │
                    │   → 验证通过的 .docx │
                    │   + 页面 PNG 截图    │
                    └─────────────────────┘
```

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│  表面层                                                      │
│  CLI (officex 命令)  |  Skill 接口 (--as-json)              │
├─────────────────────────────────────────────────────────────┤
│  合约层                                                      │
│  manifests/ (基线、写入合约、模板配置、布局合约、              │
│             provider 目录、agent 目录)                       │
│  所有行为由声明式 manifest 驱动，无硬编码                     │
├─────────────────────────────────────────────────────────────┤
│  执行层                                                      │
│  manifest_loader → section_assembler → writer → docx         │
│  AI 生成内容；程序代码拥有结构                                │
├─────────────────────────────────────────────────────────────┤
│  验证层                                                      │
│  结构验证: validation/ (page_setup, style, image, override)  │
│  视觉验证: LibreOffice headless → PNG → Pillow 检查          │
├─────────────────────────────────────────────────────────────┤
│  运行时层                                                    │
│  provider_adapter (OpenAI 兼容调度)                          │
│  prompt_runtime (角色组合 + 认知层)                           │
│  agent_runtime (编排器、写入器、验证工程师...)                │
├─────────────────────────────────────────────────────────────┤
│  追踪层                                                      │
│  检查点、阶段历史、事件日志、审查账本                          │
│  Agent 操作的平台级记忆                                      │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 安装

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e .
```

### 2. 检查环境

```bash
officex
```

自动扫描 Python、LibreOffice、依赖包和 API Key 状态。

### 3. （可选）安装 LibreOffice 用于视觉审计

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt install libreoffice
```

### 4. 生成文档

```bash
export OFFICEX_PROVIDER_API_KEY="你的 API Key"
export OFFICEX_PROVIDER_BASE_URL="https://你的提供商/v1"

officex generate \
  --prompt "写一份关于移动端学习日程管理 APP 的项目提案" \
  --model qwen-plus \
  --output-dir ./my-proposal
```

输出：
```
Generated: ./my-proposal/gen-20260501-221650.docx
Model: qwen-plus | Tokens: {'prompt_tokens': 1019, 'completion_tokens': 658, 'total_tokens': 1677}
Validation: 0 error(s), 0 warning(s)
Visual: 1 page(s), 0 finding(s)
```

输出目录包含：
- `*.docx` — 最终 Word 文档
- `ai_response.txt` — AI 原始输出
- `build_source.json` — 解析后的文档结构
- `validation.json` — 结构验证报告
- `visual/page-*.png` — 渲染后的页面图片

## 作为 AI Agent 的 Skill 使用

OfficeX 设计为可被其他 AI Agent（Codex、Claude Code、Hermes 等）调用的文档操作工具。

**Skill 文档：** 参见 [`skills/SKILL.md`](skills/SKILL.md)

所有命令支持 `--as-json` 机器可读输出：

```bash
# Agent 调用 OfficeX
officex generate --prompt "..." --model qwen-plus --output-dir /tmp/task-123 --as-json

# 解析 JSON 结果
# {
#   "status": "success",
#   "output_docx": "/tmp/task-123/gen-xxx.docx",
#   "page_count": 3,
#   "validation_errors": 0
# }
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `officex` | 品牌界面 + 环境扫描 |
| `officex generate --prompt "..."` | Prompt → AI → docx → 验证 → 视觉QA |
| `officex doctor` | 完整环境就绪检查 |
| `officex audit visual --candidate-docx f.docx` | 渲染为 PNG + 视觉QA |
| `officex task run-docx-mvp` | 从 manifest 确定性生成 docx |
| `officex task apply-patch-bundle` | 应用确定性补丁 |
| `officex provider list` | 列出已配置的 AI 提供商 |
| `officex prompt show --role orchestrator` | 显示组合后的角色提示词 |
| `officex agent list` | 列出已注册的 Agent 角色 |
| `officex trace checkpoint` | 创建追踪检查点 |

## 支持的 Provider

任何 OpenAI 兼容接口均可使用：

| 提供商 | 配置 |
|--------|------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...` |
| 阿里百炼 | `OFFICEX_PROVIDER_API_KEY=sk-... OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 本地/自托管 | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1` |

## 开发

```bash
.venv/bin/pytest -q          # 183 个测试
officex doctor --as-json     # 环境检查
```

## 许可证

MIT
