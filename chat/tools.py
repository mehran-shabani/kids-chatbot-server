import datetime


def calculator(expression: str) -> str:
    try:
        # Very basic safe eval: digits and operators only
        if not all(ch in "0123456789+-*/(). " for ch in expression):
            return "Unsupported expression"
        return str(eval(expression))
    except Exception:
        return "Error"


def time_now() -> str:
    return datetime.datetime.now().isoformat()


