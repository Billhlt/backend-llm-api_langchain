 # LangChain LLM Chat API

  基于 **LangChain + LangGraph + FastAPI** 的 LLM 对话接口服务，演示**带记忆的 Agent 编排**：通过 `create_agent`
  构建支持工具调用的 Agent，并用 `InMemorySaver` 检查点实现**按会话（chatId）隔离的对话记忆**。

  ## 功能特性

  - 🤖 基于 `langchain.agents.create_agent`（v1 推荐 API）构建 Agent，支持工具调用
  - 🧠 对话记忆：按 `chatId` 隔离会话历史，多轮上下文不串扰
  - 🛠 内置 `get_weather` 工具桩，演示工具调用
  - 🔌 兼容 GET / POST 两种调用方式
  - 🚀 接入 DeepSeek 大模型（`deepseek-v4-flash`）

  ## 技术栈

  | 组件 | 说明 |
  | --- | --- |
  | FastAPI + Uvicorn | HTTP 服务层 |
  | LangChain 1.2.x | Agent 编排、模型统一入口（`init_chat_model`） |
  | LangGraph 1.1.x | 状态图、记忆检查点（`InMemorySaver`） |
  | DeepSeek API | 大模型推理 |

  > 说明：`langgraph.prebuilt.create_react_agent` 为旧版/弃用 API，本项目使用 `create_agent`。

  ## 使用步骤

  ### 1. 安装依赖

  ```powershell
  # conda 环境（推荐）
  conda run -n test pip install -r requirements.txt
  ```

  ### 2. 配置 API Key（必填，否则服务无法调用模型）

  代码从环境变量 `DEEPSEEK_API_KEY` 读取密钥，请先前往 [DeepSeek 开放平台](https://platform.deepseek.com) 获取你自己的
  API Key。

  **Windows PowerShell：**

  ```powershell
  $env:DEEPSEEK_API_KEY = "sk-你的key"
  ```

  **Linux / macOS：**

  ```bash
  export DEEPSEEK_API_KEY="sk-你的key"
  ```

  ### 3. 启动服务（默认端口 8081）

  ```powershell
  conda run -n test python test01.py
  ```

  ### 4. 调用接口

  **GET 方式：**

  ```http
  GET /ai/chat?prompt=%E4%BD%A0%E5%A5%BD&chatId=session-001
  ```

  **POST 方式（JSON）：**

  ```json
  POST /ai/chat
  {
    "prompt": "帮我查一下北京天气",
    "chatId": "session-001"
  }
  ```

  POST 也兼容 query 参数调用（`/ai/chat?prompt=...&chatId=...`）。

  **返回**：纯文本（`text/plain`），即模型回复。

  | 参数 | 类型 | 必填 | 说明 |
  | --- | --- | --- | --- |
  | `prompt` | string | ✅ | 用户输入，服务端自动做 URL 解码 |
  | `chatId` | string | ✅ | 会话 ID，用于隔离各自对话记忆 |

  ## 注意事项

  - 记忆基于 `InMemorySaver`，**进程重启后会话历史丢失**，适合学习/演示，生产可换持久化存储。
  - 代码在 Windows / Linux 均可运行，但配置密钥的命令按平台不同（Windows 用 PowerShell 的 `$env:`，Linux 用 `export`）。
  - 模型可通过 `init_chat_model` 的 `base_url` 换成其他 OpenAI 兼容接口。
