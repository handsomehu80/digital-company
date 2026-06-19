# 🏢 Digital Company - 数字公司系统

> 1人CEO + N个数字员工，基于 Microsoft Agent Framework 构建

## 系统概述

这是一个模拟真实公司运作的数字员工协作系统。CEO（你）通过自然语言向系统下达指令，数字员工自动协作完成任务。

### 核心架构

```
CEO (你)
    ↓ 自然语言指令
数字公司管理层 (任务路由)
    ↓
┌─────────────────────────────────────────────┐
│               数字员工团队                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 市场部  │ │ 技术部  │ │ 运营部  │       │
│  │Researcher│ │ Engineer│ │ Analyst │       │
│  │ Strategist│ │ DevOps  │ │    PM   │       │
│  │ Copywriter│ │   QA    │ │ Support │       │
│  └─────────┘ └─────────┘ └─────────┘       │
└─────────────────────────────────────────────┘
    ↓
  产出结果 → CEO 审核
```

## 技术栈

- **框架**: Microsoft Agent Framework 1.0
- **语言**: Python 3.10+
- **模型支持**: Ollama (免费) / Azure OpenAI / OpenAI / Anthropic
- **工具生态**: MCP (Model Context Protocol)
- **可观测性**: OpenTelemetry

## 快速开始

### 1. 安装依赖

```bash
pip install agent-framework

# 可选：安装所有集成包
pip install agent-framework-core agent-framework-foundry

# Ollama 支持（免费本地模型）
pip install ollama
```

### 2. 配置模型

创建 `~/.digital-company/config.yaml`:

```yaml
# 默认使用 Ollama 免费模型
default_provider: ollama

providers:
  ollama:
    endpoint: "http://localhost:11434"
    default_model: "llama3.2"
    
  azure_openai:
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    api_key: "${AZURE_OPENAI_KEY}"
    default_model: "gpt-4o-mini"

# 数字员工配置
agents:
  default_model: "llama3.2"
  max_tool_iterations: 10
  memory_enabled: true
```

### 3. 启动数字公司

```bash
cd digital-company
python -m src.main
```

## 数字员工矩阵

### 市场部 (Marketing)

| 角色 | 职责 | 工具 |
|------|------|------|
| 市场调研员 | 数据收集、竞品分析 | web_search, file_write |
| 品牌策略师 | 品牌定位、营销策略 | doc_writer, ppt_generator |
| 内容创作者 | 文案撰写、内容策划 | writing_tool |

### 技术部 (Engineering)

| 角色 | 职责 | 工具 |
|------|------|------|
| 前端工程师 | React/Vue 开发 | code_editor, git, testing |
| 后端工程师 | API/数据库开发 | code_editor, docker, git |
| DevOps 工程师 | CI/CD、部署、监控 | docker, k8s, monitoring |
| QA 工程师 | 测试、代码审查 | testing, code_review |

### 运营部 (Operations)

| 角色 | 职责 | 工具 |
|------|------|------|
| 项目经理 | 任务分解、进度跟踪 | task_board, calendar |
| 数据分析师 | 数据处理、可视化 | python_code, chart_generator |
| 客服专员 | 用户支持、问题处理 | email, chat |

## 工作流示例

### 市场调研工作流

```python
from src.workflows import MarketResearchWorkflow

workflow = MarketResearchWorkflow()
result = await workflow.run(
    task="调研2025年AI教育市场的机会"
)
```

### 产品开发工作流

```python
from src.workflows import ProductDevWorkflow

workflow = ProductDevWorkflow()
result = await workflow.run(
    task="为game-for-my-children添加多人对战功能"
)
```

## 当前项目

### game-for-my-children 🎮

**儿童教育冒险游戏**：海上探险 + 知识答题战斗

- 仓库: https://github.com/handsomehu80/game-for-my-children
- 技术栈: React 18 + Vite + React-Three-Fiber + Zustand
- 数字公司正在帮助完善功能开发

### 待完成任务

- [ ] 多人联机对战系统
- [ ] 题库扩充系统
- [ ] 存档同步服务
- [ ] 家长控制面板
- [ ] 成就系统

## 开发指南

### 添加新的数字员工

1. 在 `src/agents/roles/` 创建角色定义
2. 定义 `instructions`, `tools`, `skills`
3. 在 `src/workflows/` 创建对应工作流
4. 注册到 `src/company.py`

### 运行测试

```bash
pytest tests/
```

## 文档

- [架构设计](./docs/architecture.md)
- [工作流设计](./docs/workflows.md)
- [数字员工手册](./docs/agent-handbook.md)
- [API 参考](./docs/api.md)

## License

MIT
