from collections.abc import Callable
from langchain_core.language_models import BaseChatModel
from llm.tools import create_sql_tool, run_shell_command
from config import get_env
from psycopg.connection_async import AsyncConnection
from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore
from typing import Annotated
from fastapi import Depends
from langgraph.store.base import BaseStore
from llm.main_graph import create_main_graph


async def get_store():
    async with AsyncPostgresStore.from_conn_string(
        get_env("STORE_URL"),
    ) as store:
        await store.setup()
        yield store


async def get_checkpointer():
    async with AsyncPostgresSaver.from_conn_string(
        get_env("CHECKPOINTER_URL"),
    ) as checkpointer:
        await checkpointer.setup()
        yield checkpointer


async def get_gemini_llm():
    gemini_api_key = get_env("GEMINI_API_KEY")
    gemini_model = get_env(
        "GEMINI_MODEL",
        default="gemini-2.5-flash",
    )
    return ChatGoogleGenerativeAI(
        api_key=gemini_api_key,
        model=gemini_model,
    )


async def get_db():
    async with await AsyncConnection.connect(
        get_env("DATABASE_URL"),
    ) as db:
        yield db


async def get_main_tools(db: AsyncConnection = Depends(get_db)):
    return [create_sql_tool(db), run_shell_command]


async def get_main_graph(
    checkpointer: Annotated[
        BaseCheckpointSaver,
        Depends(get_checkpointer),
    ],
    store: Annotated[
        BaseStore,
        Depends(get_store),
    ],
    llm: Annotated[
        BaseChatModel,
        Depends(get_gemini_llm),
    ],
    tools: Annotated[
        list[Callable],
        Depends(get_main_tools),
    ],
):
    return create_main_graph(
        checkpointer=checkpointer,
        store=store,
        llm=llm,
        tools=tools,
    )
