# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Learning project for **LangChain** (1.2.x) and **LangGraph** (1.1.x) in Python, exposed as a FastAPI service (`test01.py`). Focus: agent orchestration, memory (checkpointing), tool calling, and LLM integration.

## Important: Linux → Windows

The code and `.venv/` were created on **Linux**; this machine runs **Windows 11 / PowerShell**.

- The repo's `.venv/` is a **stale Linux venv** (uv 0.7.6, `home = /home/bill/anaconda3/...`). Do **not** use it on Windows — ignore it.
- Use the conda environment **`test`** (miniconda, Python 3.11.14). Project permission settings only allow `Bash(conda run:*)`, so prefer `conda run -n test ...` for everything.
- Windows shell has no `grep`/`head`; use `findstr` / `Select-String` instead.

## Commands (PowerShell)

```powershell
# Run the FastAPI server (serves on http://0.0.0.0:8081)
conda run -n test python test01.py

# Dev server with auto-reload
conda run -n test python -m uvicorn test01:app --reload --port 8081

# Install additional packages
conda run -n test pip install <package>

# List installed LangChain/LangGraph packages (PowerShell, not grep)
conda run -n test pip list | findstr /i "langchain langgraph lang"
```

Requires the `DEEPSEEK_API_KEY` environment variable to be set (the app reads it via `os.getenv`).

## Key API Note

- `langchain.agents.create_agent` — the **current/recommended** agent factory, with middleware & checkpointer support.
- `langgraph.prebuilt.create_react_agent` — the **older/deprecated** API (use `create_agent` instead).

## Architecture

`test01.py` is the real application; `main.py` is only `uv init` boilerplate ("Hello from learning-code!") and `README.md` is empty.

**FastAPI app** (`app`) exposing `/ai/chat`:
- `GET /ai/chat?prompt=...&chatId=...` — query params, returns `PlainTextResponse`.
- `POST /ai/chat` — accepts JSON body `{prompt, chatId}` (Pydantic `ChatBody`) or the same query params; returns `PlainTextResponse`, or a `422` JSON error if neither is provided.
- The `prompt` is **URL-decoded server-side** (`urllib.parse.unquote`) before reaching the model.

**Memory**: `InMemorySaver()` checkpointer passed to `create_agent(...)`. The `chatId` maps to `config["configurable"]["thread_id"]`, giving per-conversation history. Note `InMemorySaver` resets on process restart.

**Model**: `init_chat_model("deepseek-v4-flash", ...)` with `base_url="https://api.deepseek.com"`, `api_key=os.getenv("DEEPSEEK_API_KEY")`, and `extra_body={"thinking": {"type": "disabled"}}` (valid values: `adaptive`, `enabled`, `disabled`).

**Tool example**: `get_weather(city)` is a stub returning a canned string — demonstrates tool calling only.

**Run entry**: `uvicorn.run(app, host="0.0.0.0", port=8081)` inside `if __name__ == "__main__"`.
