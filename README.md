# ShopPilot · 电商运营分析智能体

> 基于 LangChain create_agent + LangGraph 构建的 ReAct 智能体，面向电商运营场景提供知识问答、经营预警分析、交易异常诊断与经营报告生成能力。

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1.4-orange.svg)](https://www.langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Chroma](https://img.shields.io/badge/Chroma-Latest-green.svg)](https://www.trychroma.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io)

---

## ✨ 核心亮点

### 1. ReAct 主循环 + 9 个业务工具全链路覆盖

基于 LangChain `create_agent` 构建 ReAct 主循环，9 个工具覆盖店铺 / 时段 / 预警 / 指标 / 交易 / 供应链全链路诊断：

| 工具 | 职责 |
|---|---|
| `rag_summarize` | RAG 知识库检索与 SOP 摘要生成 |
| `get_target_shop` | 店铺识别与标准化 |
| `get_time_range` | 时间范围解析 |
| `fetch_operation_alerts` | 经营预警数据 |
| `fetch_sales_metrics` | 销售指标查询 |
| `fetch_transaction_summary` | 交易异常诊断 |
| `fetch_supply_chain_topology` | 供应链拓扑与状态 |
| `fetch_report_data` | 报告模式专用数据集 |
| `fill_context_for_report` | 标记报告模式切换 |

工具层通过 mock 数据 + 接口抽象设计，真实业务系统（生意参谋 / 订单中台 / 物流平台）可无缝替换，零侵入。

### 2. Agent 中间件扩展能力，零侵入双模式切换

| 中间件 | 装饰器 | 能力 |
|---|---|---|
| `monitor_tool` | `@wrap_tool_call` | 工具调用全链路日志 + 异常捕获 |
| `log_before_model` | `@before_model` | 模型调用前监控上下文规模 |
| `report_prompt_switch` | `@dynamic_prompt` | 依据 `runtime.context` 动态切换系统提示词 |

**双模式切换原理**：当工具 `fill_context_for_report` 被调用时，`monitor_tool` 将 `runtime.context["report"]` 置为 `True`；下一轮模型调用前，`report_prompt_switch` 自动把 system prompt 从"问答模式"替换为"报告模式"，无需改代码、无需重启 Agent。

```
fill_context_for_report 执行
        ↓
monitor_tool: context["report"] = True
        ↓
下一轮 @dynamic_prompt
        ↓
report_prompt_switch: context["report"] → load_report_prompts()
```

### 3. 自建 RAG 知识库

- **持久化向量库**：Chroma，`persist_directory` 本地落盘
- **分片策略**：`RecursiveCharacterTextSplitter`，`chunk_size=200`，`overlap=20`，中文分隔符 `["\n\n", "\n", ".", "。", ...]`
- **文件级 MD5 去重**：`md5.text` 记录已索引文件指纹，重复运行跳过 → **增量索引**
- **领域重构**：按"预警现象 → 排查步骤 → 处理方案"重写 7 篇业务 SOP，使检索结果与 Agent 工具调用路径对齐

---

## 🛠 技术栈

| 层 | 技术 |
|---|---|
| Agent 框架 | LangChain `create_agent` + LangGraph |
| 模型 | 通义千问 `qwen-max` + `text-embedding-v4` |
| 向量库 | Chroma（持久化） |
| 前端 | Streamlit 1.66 |
| 配置 | YAML + `ConfigHandler` 单例 |
| 日志 | Python `logging` + `LoggerHandler` |

---

## 📂 项目结构

```
Agent_Project/
├── app.py                          # Streamlit 前端入口
├── agent/
│   ├── react_agent.py              # ReactAgent 主循环封装
│   └── tools/
│       ├── agent_tools.py          # 9 个业务工具（@tool 装饰）
│       └── middleware.py           # 3 个 Agent 中间件
├── rag/
│   ├── vector_store.py             # 向量库 + MD5 去重 + 增量索引
│   └── rag_service.py              # RAG 检索封装
├── model/
│   └── factory.py                  # ChatTongyi / Embedding 工厂
├── utils/
│   ├── config_handler.py           # YAML 配置加载
│   ├── logger_handler.py           # 日志单例
│   ├── path_tool.py                # 项目根路径解析
│   ├── prompt_loader.py            # 提示词文件加载
│   └── file_handler.py             # MD5 计算 / 文件列表
├── config/                         # YAML 配置文件
├── prompts/                        # system / report / rag 提示词
├── data/                           # SOP 知识库 txt 文件
├── chroma_db/                      # Chroma 持久化向量库（.gitignore）
├── logs/                           # 运行日志（.gitignore）
└── .gitignore
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Anaconda 虚拟环境（推荐）

### 安装依赖

```powershell
# 创建虚拟环境
conda create -n ShopPilot python=3.12
conda activate ShopPilot

# 安装核心依赖
pip install "langchain>=1.0" langgraph langchain-chroma langchain-tongyi
pip install streamlit pyyaml
```

### 配置

编辑 `config/rag.yaml` 选择模型：

```yaml
chat_model_name: qwen-max
embedding_model_name: text-embedding-v4
```

`config/chroma.yaml` 控制向量库参数：

```yaml
collection_name: agent
persist_directory: chroma_db
chunk_size: 200
chunk_overlap: 20
k: 3
```

### 初始化知识库

首次运行会自动加载 `data/` 下所有 txt 文件到 Chroma，之后重复运行会跳过已索引文件（MD5 去重）：

```powershell
python -m rag.vector_store
```

### 启动应用

```powershell
streamlit run app.py
```

浏览器访问 Streamlit 提示的地址（默认 http://localhost:8501）。

---

## 🎯 支持的场景

| 场景 | 示例提问 |
|---|---|
| 经营异常诊断 | "分析一下潮流服饰旗舰店最近1小时的经营异常情况" |
| 预警查询 | "数码家电专营店今天有哪些主要预警" |
| 报告生成 | "生成食品生鲜专营店本月经营报告" |
| 知识问答 | "转化率突然下降一般怎么排查" |

---

## 🔑 关键设计决策

**1. `create_agent(model=chat_model)` 传实例而非工厂**

`model/factory.py` 里 `chat_model` 已经是 `ChatTongyi` 实例，不需要再 `chat_model()`。LangChain 模型对象不可调用，加括号会抛 `TypeError: 'ChatTongyi' object is not callable`。

**2. `runtime.context` 作为中间件通信机制**

Agent 的三个中间件之间靠 `runtime.context`（共享可变 dict）传递状态，不进消息历史、不占 token：

```python
context={"report": False}    # stream 入口传入
monitor_tool 改它            # context["report"] = True
dynamic_prompt 读它          # 决定换哪个 system prompt
```

**3. ReAct 流式输出用 `stream_mode="values"`**

每个 chunk 是**累积 state 快照**而非增量，所以 `chunk["messages"][-1]` 取本轮新增消息；同时要注意 `AIMessage.content` 可能为空（模型只返回 `tool_calls`），需要过滤。

---

## 📄 License

MIT
