import math
from datetime import datetime


def calculator(expression: str) -> str:
    try:
        # Safe eval subset
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        allowed.update({"__builtins__": {}})
        return str(eval(expression, allowed, {}))
    except Exception as e:
        return f"error: {e}"


def time_now() -> str:
    return datetime.now().isoformat()

