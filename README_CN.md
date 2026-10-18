# OfficeX

[![CI](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**面向 AI Agent 和人类的文档操作基础设施。** 确定性执行，三条验证轨道，通过 Profile 扩展。

[English Documentation](README.md)

---

## OfficeX 是什么？

OfficeX 是一个**文档操作平台**：AI Agent 和人类调用它来构建、修改、验证和审计 Word 文档的可靠执行层。

它**不是**聊天机器人，也**不**试图变得智能。它负责在"智能的部分"思考完之后，确保文档是正确的。

**核心契约：**
- 给 OfficeX 一条结构化指令 → 它确定性地执行
- 给 OfficeX 一份文档 → 它从结构、语义、视觉三个方面报告问题
- 给 OfficeX 一个 Profile → 它按该纸张尺寸、字体和样式体系构建并检查

**解决的问题：** AI 通过代码生成大型文档时，常出现排版漂移、样式损坏、分页错乱、幽灵引用、图文错位。其中很多问题在文本/XML 层面看不出来。OfficeX 从三个方向检查文档（见[三条验证轨道](#三条验证轨道)）。

## 一分钟上手（无需 API Key）

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock.txt && pip install -e .

# 1. 从 manifest 构建内置示例文档（确定性，不调用 AI）
officex task run-docx-mvp --sandbox-root sandboxes --run-id demo
DOC=sandboxes/demo/candidate/minimal_writer_demo.docx

# 2. 结构 + 语义检查（不需要 LibreOffice）
officex validate --docx "$DOC"

# 3. 视觉检查：把每一页渲染成 PNG（需要 LibreOffice）
officex audit visual --candidate-docx "$DOC" --output-dir sandboxes/demo/visual

# 4. 两个版本逐页视觉对比（需要 LibreOffice）
officex diff --a "$DOC" --b "$DOC" --output-dir sandboxes/demo/diff
```

以上任一命令加 `--as-json` 即可输出机器可读结果。示例文档只有一页短内容，所以第 3 步会对它报一个 `large-white-gap` 警告。`sandboxes/` 已在 .gitignore 中。

## 使用方式

### AI Agent 调用（主要场景）

Agent 通过 CLI 或 MCP 调用 OfficeX，并读取 JSON 结果：

```bash
officex validate --docx report.docx --as-json                               # 结构 + 语义
officex audit visual --candidate-docx report.docx --output-dir /tmp/audit --as-json
officex diff --a v1.docx --b v2.docx --output-dir /tmp/diff --as-json
officex task apply-patch-bundle --patch-bundle patch.json \
  --candidate-docx report.docx --anchor-snapshot anchors.json --as-json     # 默认 dry-run
```

`validate`、`audit visual`、`diff` 的退出码有明确含义：`0` 无问题，`1` 发现错误（`diff` 表示有页面不同），`2` 参数错误或缺少 LibreOffice。

**MCP**（Claude Desktop、Cursor 等任意 MCP 客户端）。请使用虚拟环境中 `officex` 的绝对路径，因为 MCP 客户端不会替你激活虚拟环境（`which officex` 可查看路径）：

```json
{
  "mcpServers": {
    "officex": {
      "command": "/absolute/path/to/OfficeX-an-AI-agents-for-doc/.venv/bin/officex",
      "args": ["serve"]
    }
  }
}
```

MCP 工具：`officex_validate`、`officex_audit_visual`、`officex_diff`、`officex_profile_list`、`officex_doctor`，以及依赖 AI 的 `officex_generate`、`officex_generate_long`、`officex_edit`。

### 人类独立使用（需要 API Key）

```bash
officex generate --prompt "写一份项目提案" --model qwen-plus
officex generate-long --outline my_outline.yml --model qwen-plus
officex edit --docx report.docx --instruction "扩写第 3 节" --model qwen-plus
```

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Interface Layer                          │
│                                                                 │
│  CLI (officex commands)     --as-json for machine consumption   │
│  MCP Server (officex serve) tools for Claude Desktop / Cursor   │
│  Skill doc (skills/)        integration guide for AI agents     │
├─────────────────────────────────────────────────────────────────┤
│                       Contract Layer                            │
│                                                                 │
│  Manifests    baseline, sections, figures, build source         │
│  Contracts    write_contract, layout_contract, template_profile │
│  Profiles     switchable paper/font/style configurations        │
│  Constitution 27 articles governing platform behavior           │
├─────────────────────────────────────────────────────────────────┤
│                      Execution Layer                            │
│                                                                 │
│  Writer       paragraphs, images, tables, AI code blocks        │
│  Patch Engine bounded paragraph-level mutations with anchors    │
│  Editor       AI proposes replace/insert/delete operations,     │
│               applied to a copy, then verified                  │
│  Assembler    manifest → block assembly → writer                │
│  Long Gen     outline → section-by-section with interleaved     │
│               review and prior-section context                  │
├─────────────────────────────────────────────────────────────────┤
│                    Verification Layer                           │
│                                                                 │
│  Structural   page geometry, style contract, image fit,         │
│               direct-formatting overrides                       │
│  Semantic     citation ↔ bibliography, figure/table numbering,  │
│               appendix and section cross-references, figure     │
│               placement, terminology consistency                │
│  Visual       LibreOffice headless → PNG → blank pages,         │
│               aspect ratio, white gaps                          │
├─────────────────────────────────────────────────────────────────┤
│                        Trace Layer                              │
│                                                                 │
│  run-docx-mvp writes a task packet, event log and stage history │
│  per run; review ledgers and checkpoints are separate commands  │
└─────────────────────────────────────────────────────────────────┘
```

## 三条验证轨道

| 轨道 | 检查内容 | 方式 | 由哪些命令执行 |
|------|---------|------|---------------|
| **结构** | 页面几何、样式合约、图片适配、直接格式覆盖 | 按当前 Profile 做 python-docx / OOXML 检查 | `validate`、`generate`、`edit`、`task run-docx-mvp` |
| **语义** | 引用与参考文献对应、图表编号、附录与章节交叉引用、图片位置、术语一致性 | 对文档文本做模式匹配 | `validate` |
| **视觉** | 空白页、宽高比、大块空白 | LibreOffice → PDF → PNG → Pillow | `audit visual`、`diff`、`generate`、`edit` |

要完整检查一份文档，请运行 `officex validate` 和 `officex audit visual`。每条轨道都声明自己的检查范围：结构检查从不声称视觉正确；语义检查基于模式匹配，给出的是警告，不代表内容一定正确。

## 命令参考

| 命令 | 说明 | 依赖 |
|------|------|------|
| `officex` | 启动横幅 + 环境扫描 | |
| `officex validate` | 对任意 docx 做结构 + 语义检查 | |
| `officex audit visual` | 渲染为 PNG + 视觉 QA | LibreOffice |
| `officex diff` | 两个 docx 逐页视觉对比 | LibreOffice |
| `officex task run-docx-mvp` | 在沙箱中从 manifest 构建内置示例 docx | |
| `officex task apply-patch-bundle` | 通过锚点应用段落级补丁（默认 dry-run） | |
| `officex profile list/use/create/validate` | 管理文档 Profile | |
| `officex serve` | 启动 MCP 服务（stdio） | |
| `officex doctor` | 环境就绪检查 | |
| `officex init` | 创建带示例大纲的工作目录 | |
| `officex generate` | prompt → AI → docx → 结构 + 视觉检查 | API Key |
| `officex generate-long` | 大纲 → 逐节 AI 生成 → docx → 检查 | API Key |
| `officex edit` | 用 AI 编辑已有 docx → 检查 | API Key |
| `officex provider list`、`officex agent list` | 查看 provider 与 agent 目录 | |
| `officex trace checkpoint --title "..."` | 写入一个追踪检查点 | |

每个命令都有 `--help`。产生报告的命令支持 `--as-json`。除非传入 `--sandbox-root` / `--output-dir`，运行结果写入仓库的 `sandboxes/` 目录（已被 git 忽略）。

## Profile

Profile 是可切换的文档配置（纸张、页边距、字体、样式）：

```bash
officex profile list                                   # 查看 Profile，* 标记当前生效的
officex validate --docx report.docx --profile letter_business   # 按某个 Profile 检查，不切换
officex profile use letter_business                    # 切换到 US Letter + Arial
officex profile create my_custom \
  --page-width 515.9 --page-height 728.5 \
  --font "Yu Gothic" --font-size 10.5                  # 运行时新建
```

`officex profile use` 会把该 Profile 的合约复制覆盖到当前仓库的 `manifests/*.yml`，因此会影响之后的所有命令（用 `officex profile use a4_academic` 切回）。各 Profile 定义自己的段落角色：内置的 `run-docx-mvp` 示例源是为 `a4_academic` 编写的。

## AI Provider

AI 命令可使用任何 OpenAI 兼容端点，通过环境变量配置。默认模型 id 为 `qwen-plus`，使用其他提供商时请传 `--model`。

| 提供商 | 配置 |
|--------|------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...`，再加 `--model gpt-4o`（或其他 OpenAI 模型） |
| 阿里百炼 DashScope | `OFFICEX_PROVIDER_API_KEY=sk-...` `OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 本地/自托管 | `OFFICEX_PROVIDER_API_KEY=...` `OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1`，再加 `--model <你的模型>` |

## 系统要求

| 组件 | 要求 |
|------|------|
| **操作系统** | macOS 或 Linux（CI 在 `macos-latest` 和 `ubuntu-latest` 上运行）。Windows 未测试 |
| **Python** | 3.11 或 3.12（CI 均有测试） |
| **LibreOffice** | 可选。`audit visual`、`diff` 以及 `generate`/`edit` 的视觉步骤需要 |
| **API Key** | 可选。仅 `generate`、`generate-long`、`edit` 需要 |

请按上面的方式从克隆的仓库用 `pip install -e .` 安装。目前尚未发布 PyPI 包；普通（非 editable）安装不包含 manifest 和 Profile。

## 宪法

OfficeX 的行为由 [CONSTITUTION.md](CONSTITUTION.md) 治理：8 个领域，27 条。

1. **权威**：Manifest 是法律。层级不向上越权。
2. **执行**：变更前先沙箱隔离。声称前先验证。降级而不阻断。
3. **记忆**：四层分层。检索只提供参考，不做决定。
4. **交互**：任务分量决定对话方式。不捏造关键输入。
5. **安全**：内容不越界。密钥不落盘。
6. **扩展**：配置是动态的。Skill 是自包含的。
7. **规划**：计划粒度匹配任务复杂度。文档读起来像同一个作者写的。
8. **追踪**：一切留痕。追踪可重放。

## 开发

```bash
pip install -r requirements.lock.txt && pip install -e .
pytest -q
python -m tools.report_scaffold_v3.cli check-package
```

CI 在 macOS 和 Ubuntu、Python 3.11 和 3.12 上，基于 `requirements.lock.txt` 运行测试、包完整性检查和 CLI 冒烟测试；另有每周一次针对最新允许依赖版本的运行。

| 分支 | 用途 |
|------|------|
| `main` | 稳定版；CI 必须通过 |
| `dev` | 活跃开发 |

## 许可证

MIT
