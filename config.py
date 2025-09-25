import os


def get_env(name: str, *, default: str | None = None) -> str:
    value = os.getenv(name)
    if not value:
        if not default:
            raise ValueError(f"{name} is not set")
        return default
    return value
