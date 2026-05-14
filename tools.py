def get_weather(city: str) -> str:
    return f"{city}天氣晴朗，氣溫25度。"


def get_articles(query: str) -> list[str]:
    return [
        f"{query}的文章1",
        f"{query}的文章2",
        f"{query}的文章3",
    ]