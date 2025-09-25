from pydantic import Field

import subprocess
from psycopg import AsyncConnection


def create_sql_tool(db: AsyncConnection):
    async def run_sql_query(
        query: str = Field(..., description="The SQL query to run"),
    ) -> str:
        """
        Run a SQL query and return the result.
        """
        async with db.cursor() as cursor:
            await cursor.execute(query)  # type: ignore
            await db.commit()
            return str(cursor.fetchall())

    return run_sql_query


def run_shell_command(
    command: str = Field(..., description="The command to run"),
) -> str:
    """
    Run a shell command and return the output.
    """
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    ).stdout
