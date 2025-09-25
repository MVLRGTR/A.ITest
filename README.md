### Project requirements

- [Uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker

### Setup

1. Run database

```bash
docker compose up -d
```

2. Run the API in dev mode

```bash
uv run fastapi dev
```

### Interacting with the API

Send messages to the service through the `/chat/{thread_id}` endpoint.
Example:

```bash
curl --location 'http://localhost:8000/chat/1000' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Hello, world!"
}'
```

Or use your preferred http client.

### Features

In the current state, the service supports:

- Thread specific chat history management
- Thread specific short term and long term memory management
- Tool calling (2 tools available: run bash commands and run sql queries)

### Suggestions

1. Implement similarity search tools (<https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/#read-long-term>)
2. Implement authentication
3. Add a separate endpoint for streaming responses
