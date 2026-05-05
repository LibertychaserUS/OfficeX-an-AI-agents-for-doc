# OfficeX

[![CI](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**面向 AI Agent 和人类的文档操作基础平台。** 确定性执行，三轨验证，通过 Profile 和 Skill 扩展。

[English Documentation](README.md)

---

## OfficeX 是什么？

OfficeX 是一个**文档操作平台**——AI Agent 和人类调用它来构建、修改、验证和审计 Word 文档的可靠执行层。

它**不是**聊天机器人。它**不会**试图变得智能。它是确保"智能的部分思考完之后，文档是正确的"那个环节。

**核心契约：**
- 给 OfficeX 一条结构化指令 → 它精确执行
- 给 OfficeX 一份文档 → 它准确告诉你哪里有问题（结构、视觉、语义）
- 给 OfficeX 一个 Profile → 它适应任何纸张、字体、样式、语言
- 给 OfficeX 一个 Skill → 它学会新的工作流，无需改代码

**解决什么问题：** AI 通过代码生成大型文档时，会出现排版漂移、样式损坏、分页异常、幽灵引用、图文错位等问题。这些问题靠文本/XML 检查完全发现不了。OfficeX 通过三轨验证捕获它们。

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         接口层                                   │
│                                                                  │
│  CLI (officex 命令)        --as-json 供机器消费                  │
│  MCP Server (officex serve) 供 Claude Desktop / Cursor 调用      │
│  Skill 文档 (skills/)      供 AI Agent 集成参考                  │
├─────────────────────────────────────────────────────────────────┤
│                        合约层                                    │
│                                                                  │
│  Manifest    baseline, sections, figures, build source            │
│  Contract    write_contract, layout_contract, template_profile   │
│  Profile     运行时可切换的纸张/字体/样式配置                     │
│  Constitution 27 条宪法，治理所有平台行为                         │
│                                                                  │
│  所有行为由 manifest 驱动。无硬编码。                             │
├─────────────────────────────────────────────────────────────────┤
│                        执行层                                    │
│                                                                  │
│  Writer       段落、图片、表格、AI 代码块                        │
│  Patch Engine 基于锚点的有界段落级变更                           │
│  Editor       AI 驱动的 编辑→补丁→验证 循环                     │
│  Assembler    manifest → 块组装 → writer                        │
│  Long Gen     大纲 → 逐章生成，含穿插审查和上下文传递             │
├─────────────────────────────────────────────────────────────────┤
│                       验证层                                     │
│                                                                  │
│  轨道 1: 结构验证  页面几何、样式合约、图片适配、覆盖检测        │
│                                                                  │
│  轨道 2: 视觉审计  LibreOffice headless → PNG 渲染 →             │
│                    空白页、宽高比、空白间隙检查                    │
│                                                                  │
│  轨道 3: 语义验证  引用↔参考文献对齐、图表编号连续性、            │
│                    附录引用、章节交叉引用、锚点邻近度、            │
│                    术语一致性                                     │
│                                                                  │
│  三条轨道都通过才算正确。每条轨道明确声明检查范围。               │
├─────────────────────────────────────────────────────────────────┤
│                       扩展层                                     │
│                                                                  │
│  Profile     officex profile create/use/list — 任意纸张、字体、  │
│              样式体系，运行时由用户或 AI 创建                     │
│  Skill       用户自定义工作流包（SKILL.md + 脚本）               │
│  Criteria    自动检查规则 + AI 判断规则，按文档定义，不硬编码     │
│  Provider    任意 OpenAI 兼容端点，环境变量配置                   │
├─────────────────────────────────────────────────────────────────┤
│                       追踪层                                     │
│                                                                  │
│  检查点、阶段历史、事件日志、审查账本                             │
│  每个操作都留下可审计的记录                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 使用方式

### AI Agent 调用（主要场景）

AI Agent 把 OfficeX 当作工具/技能调用来执行文档操作：

```bash
# Agent 让 OfficeX 从结构化输入生成文档
officex task run-docx-mvp --sandbox-root /tmp/run-1 --as-json

# Agent 让 OfficeX 验证文档
officex audit visual --candidate-docx report.docx --output-dir /tmp/audit --as-json

# Agent 让 OfficeX 对比两个版本
officex diff --a v1.docx --b v2.docx --output-dir /tmp/diff --as-json
```

通过 MCP 集成（Claude Desktop、Cursor 等）：
```json
{
  "mcpServers": {
    "officex": {
      "command": "officex",
      "args": ["serve"]
    }
  }
}
```

### 人类独立使用

```bash
# 从 prompt 生成文档（OfficeX 替你调 AI）
officex generate --prompt "写一份项目提案" --model qwen-plus

# 从大纲生成长文档
officex generate-long --outline my_outline.yml --model qwen-plus

# 编辑已有文档
officex edit --docx report.docx --instruction "扩展第三章" --model qwen-plus

# 切换文档配置
officex profile use letter_business
```

## 分支

| 分支 | 用途 |
|------|------|
| `main` | 稳定发布版。所有功能均可正常使用。 |
| `dev` | 活跃开发版。可能包含未完成的功能。 |

## 开箱即用（无需 API Key）

```bash
officex                              # 品牌界面 + 环境扫描
officex init                         # 创建工作空间
officex doctor --as-json             # 环境就绪检查
officex profile list                 # 列出文档配置
officex profile create my_profile    # 运行时创建新配置
officex task run-docx-mvp            # 从 manifest 确定性生成 docx
officex audit visual --candidate-docx file.docx  # 视觉 QA（需要 LibreOffice）
```

## AI 驱动的命令（需要 API Key）

```bash
export OFFICEX_PROVIDER_API_KEY="你的 key"
export OFFICEX_PROVIDER_BASE_URL="https://你的提供商/v1"

officex generate --prompt "..."                    # 短文档
officex generate-long --outline plan.yml           # 长文档
officex edit --docx file.docx --instruction "..."  # 编辑已有文档
```

## 系统要求

| 组件 | 要求 |
|------|------|
| **操作系统** | macOS 10.9+（Intel）、macOS 11+（Apple Silicon）、Linux（glibc 2.28+，x86_64/aarch64） |
| **Python** | 3.11+ |
| **LibreOffice** | 可选。视觉审计（PNG 渲染）需要 |
| **API Key** | 可选。AI 驱动的 generate/edit 命令需要。支持任何 OpenAI 兼容端点 |

## 快速开始

```bash
git clone https://github.com/LibertychaserUS/OfficeX-an-AI-agents-for-doc.git
cd OfficeX-an-AI-agents-for-doc

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock.txt
pip install -e .

officex                   # 查看环境状态
officex doctor --as-json  # 完整就绪检查
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `officex` | 品牌界面 + 环境扫描 |
| `officex init` | 初始化工作空间 |
| `officex generate` | 短文档：prompt → AI → docx → 验证 |
| `officex generate-long` | 长文档：大纲 → 逐章生成 → 验证 |
| `officex edit` | AI 驱动编辑已有文档 |
| `officex diff` | 两份文档视觉对比 |
| `officex serve` | 启动 MCP 服务供 AI Agent 集成 |
| `officex doctor` | 环境就绪检查 |
| `officex audit visual` | 渲染为 PNG + 视觉 QA |
| `officex profile list/use/create` | 管理文档配置 |
| `officex task run-docx-mvp` | 从 manifest 确定性生成 docx |
| `officex task apply-patch-bundle` | 应用确定性补丁 |
| `officex provider list` | 列出已配置的 AI 提供商 |
| `officex agent list` | 列出已注册的 Agent 角色 |
| `officex trace checkpoint` | 创建追踪检查点 |

所有命令支持 `--as-json` 输出机器可读格式。

## Profile 系统

Profile 是运行时可切换的文档配置（纸张、字体、样式）：

```bash
officex profile list                    # 查看可用配置
officex profile use letter_business     # 切换到 US Letter + Arial
officex profile create my_custom \
  --page-width 515.9 --page-height 728.5 \
  --font "Yu Gothic" --font-size 10.5   # 运行时创建新配置
```

没有硬编码。用户和 AI Agent 可以为任何纸张、字体或样式体系创建新 Profile。

## 三轨验证

OfficeX 通过三条独立轨道验证文档：

| 轨道 | 检查内容 | 方式 |
|------|---------|------|
| **结构验证** | 页面几何、样式合约、图片适配、覆盖检测 | python-docx 检查 |
| **视觉审计** | 空白页、宽高比、空白间隙、排版漂移 | LibreOffice → PNG → Pillow |
| **语义验证** | 引用对齐、编号连续性、附录引用、章节交叉引用、术语一致性 | 内容模式匹配 |

文档必须三条轨道都通过才算正确。每条轨道明确声明自己的检查范围——结构检查不宣称视觉正确性，反之亦然。

## 宪法

OfficeX 的行为由 [CONSTITUTION.md](CONSTITUTION.md) 治理——8 个领域 27 条：

1. **权威** — Manifest 是法律。层级不可逆。
2. **执行** — 变更前沙箱隔离。声称前先验证。降级不阻断。
3. **记忆** — 四层分层。检索只建议不决定。
4. **交互** — 重量决定对话。不捏造关键输入。
5. **安全** — 内容不越界。密钥不落盘。
6. **扩展** — 配置是动态的。Skill 是自包含的。
7. **规划** — 计划粒度匹配任务复杂度。文档读起来像一个人写的。
8. **追踪** — 一切留痕。可重放。

## 支持的 Provider

任何 OpenAI 兼容端点：

| 提供商 | 配置 |
|--------|------|
| OpenAI | `OFFICEX_PROVIDER_API_KEY=sk-...` |
| 阿里百炼 | `OFFICEX_PROVIDER_API_KEY=sk-... OFFICEX_PROVIDER_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 本地/自托管 | `OFFICEX_PROVIDER_API_KEY=... OFFICEX_PROVIDER_BASE_URL=http://localhost:8080/v1` |

## 开发

```bash
.venv/bin/pytest -q          # 运行测试
officex doctor --as-json     # 环境检查
```

## 许可证

MIT
