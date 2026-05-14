import json
import time

from openai import OpenAI

from credentials import OPENAI_KEY


client = OpenAI(api_key=OPENAI_KEY)


# 注意，這邊是為了方便理解土炮做法
# 實務上各個 SDK 會希望用獨立的參數把 tool calls 的資訊傳過去
# 而不是把 tool calls 的資訊塞在 prompt 裡面
# 雖然語言模型本身還是只能理解純文字（實際上是 token stream）
# 但是透過 input data 的資料結構，他們可以用特定 token 作為分隔
# 讓模型更好理解輸入的內容

# user_input = "天為什麼是藍的？"
user_input = "高雄今天的天氣是？"

system_prompt = """\
你是個有用的助手，幫助使用者回答問題。你可以使用以下工具來獲取資訊：

- get_weather(city: str) -> str: 回傳天氣說明
- get_articles(query: str) -> list[str]: 回傳文章標題列表

規則：
- 當你沒有資訊來回答使用者的問題，但有工具可以幫助你獲取資訊時，你應該使用工具來獲取資訊
- 當你有足夠的資訊來回答使用者的問題時，你應該直接回答，不需要使用工具
- 如果你沒有足夠的資訊來回答使用者的問題，也沒有適合的工具，你應該委婉的表達不知道

輸出：
你的輸出應該是一個 JSON 物件，包含以下欄位：
- answer: 你對使用者問題的回答，必須是完整的句子。或是 null，如果你還沒有決定好答案。
- tool_calls: 你使用的工具呼叫列表，每個工具呼叫是一個物件，包含以下欄位：
    - tool_name: 工具名稱
    - arguments: 工具參數物件，包含工具呼叫所需的參數


要求呼叫工具的輸出範例：
```
{"answer": null,"tool_calls": [{"tool_name": "{tool name}", "arguments": {....}}]}
```

回答答案的範例：
```
{"answer": "{answer text}", "tool_calls": []}
```
"""

input_data = [
    {
        "role": "system",
        "content": system_prompt,
    },
    {
        "role": "user",
        "content": user_input,
    }
]

print("=== 系統指令 ===")
print(system_prompt)

print()
print("=== 輸入文字 ===")
print(user_input)

print()
print("=== 答案文字 ===")
start_time = time.time()
response = client.responses.create(
    model="gpt-5.4-mini",
    input=input_data,
    reasoning={
        "effort": "none",
        "summary": None,
    },
)

print(response.output_text)
# try:
#     output_data = json.loads(response.output_text)
#     pretty_output = json.dumps(output_data, indent=2, ensure_ascii=False)
#     print(pretty_output)
# except json.JSONDecodeError:
#     print(response.output_text)

print()
print("=== 其他資訊 ===")
end_time = time.time()
print(f"LLM call + 網路傳輸耗時: {end_time - start_time:.2f} 秒")
