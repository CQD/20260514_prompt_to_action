from datetime import datetime


def get_weather(city: str) -> str:
    return f"{city}天氣晴朗，氣溫25度。"


def get_articles(query: str) -> list[str]:
    return [
        f"{query}的文章1",
        f"{query}的文章2",
        f"{query}的文章3",
    ]


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    # 教學用簡化版：直接 eval。實務上要用安全的算式 parser
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"