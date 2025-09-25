from collections.abc import Callable
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.base import BaseStore

from .prompts import MAIN_SYSTEM_PROMPT


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def create_main_graph(
    checkpointer: BaseCheckpointSaver,
    store: BaseStore,
    llm: BaseChatModel,
    tools: list[Callable],
):
    llm_with_tools = llm.bind_tools(tools)

    async def call_llm(state: State):
        messages = state["messages"]
        input: list[AnyMessage] = [SystemMessage(MAIN_SYSTEM_PROMPT)] + messages
        response = await llm_with_tools.ainvoke(input=input)
        return {"messages": [response]}

    graph = StateGraph(State)

    graph.add_node("call_llm", call_llm)
    graph.add_node(
        "tools",
        ToolNode(tools),
    )

    graph.add_edge(START, "call_llm")
    graph.add_conditional_edges(
        "call_llm",
        tools_condition,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph.add_edge("tools", "call_llm")
    graph.add_edge("call_llm", END)

    compile_graph = graph.compile(
        checkpointer=checkpointer,
        store=store,
    )

    return compile_graph
