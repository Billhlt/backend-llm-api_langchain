import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
import urllib.parse
from fastapi.responses import PlainTextResponse

# 创建 FastAPI 应用
app = FastAPI(title="AI Chat API", description="有记忆的LLM对话接口")

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


model = init_chat_model(
    "deepseek-v4-flash",
    temperature=0.5,
    # timeout=120,
    # max_token=25000
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    extra_body={"thinking": {"type": "disabled"}} # DeepSeek API 的 thinking.type 参数只接受三个有效值： adaptive 、 enabled 、 disabled
)

# 初始化记忆存储 - 用于保存对话历史
checkpoint = InMemorySaver()

# 创建带有记忆的 agent
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
    checkpointer=checkpoint,  # 添加记忆支持
)

class ChatBody(BaseModel):
    prompt: str
    chatId: str


def _handle_chat(prompt: str, chatId: str) -> str:
    decoded_prompt = urllib.parse.unquote(prompt)
    config = {"configurable": {"thread_id": chatId}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": decoded_prompt}]},
        config=config
    )
    return result["messages"][-1].content

@app.get("/ai/chat")
async def chat_get(
    prompt: str = Query(...),
    chatId: str = Query(...),
):
    ai_response = _handle_chat(prompt, chatId)
    return PlainTextResponse(ai_response)


@app.post("/ai/chat")
async def chat_post(
    data: ChatBody = None,
    prompt: str = Query(None),
    chatId: str = Query(None),
):
    if data is not None:
        p, c = data.prompt, data.chatId
    elif prompt and chatId:
        p, c = prompt, chatId
    else:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "请提供 prompt 和 chatId"}, status_code=422)
    ai_response = _handle_chat(p, c)
    return PlainTextResponse(ai_response)
#    return result
#    return {"response": ai_response, "chatId": chatId}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
