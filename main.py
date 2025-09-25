from typing import Annotated, Any
from langchain_core.messages import HumanMessage
from fastapi import FastAPI, Depends, HTTPException
from langgraph.graph.state import Runnable
from dependencies.graph import get_main_graph
from schemas.chat import ChatRequest, ChatResponse
from llm.main_graph import State

app = FastAPI()


@app.post("/chat/{thread_id}", response_model=ChatResponse)
async def chat(
    thread_id: str,
    request: ChatRequest,
    graph: Annotated[
        Runnable[State, Any],
        Depends(get_main_graph),
    ],
):
    response = await graph.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    if len(response["messages"]) == 0:
        raise HTTPException(status_code=500, detail="No response from graph")

    content = response["messages"][-1].content
    if isinstance(content, list):
        content = "\n".join(content)

    return ChatResponse(response=content)
