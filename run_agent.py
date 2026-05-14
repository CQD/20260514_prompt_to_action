import json
import time

from openai import OpenAI

from credentials import OPENAI_KEY
import tools


client = OpenAI(api_key=OPENAI_KEY)


# 跟 run_tool_calling.py 的差異：
# run_tool_calling.py 只示範模型「決定要呼叫工具」這一步
# run_agent.py 則是把流程接起來：
#   1. 問模型
#   2. 如果模型要呼叫工具，就執行工具，把結果回灌給模型
#   3. 重複，直到模型給出 answer（或達到最大回合數）

# user_input = "天為什麼是藍的？"
user_input = "高雄今天的天氣是？順便幫我找幾篇高雄旅遊的文章"

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
{"answer": null, "tool_calls": [{"tool_name": "{tool name}", "arguments": {....}}]}
```

回答答案的範例：
```
{"answer": "{answer text}", "tool_calls": []}
```
"""

# 維護一個對話歷史，每一輪會把模型輸出與工具結果都附加進去
input_data = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

print("=== 系統指令 ===")
print(system_prompt)

print()
print("=== 輸入文字 ===")
print(user_input)

MAX_TURNS = 5

for turn in range(1, MAX_TURNS + 1):
    print()
    print(f"=== 第 {turn} 回合 ===")

    start_time = time.time()
    response = client.responses.create(
        model="gpt-5.4-mini",
        input=input_data,
        reasoning={
            "effort": "none",
            "summary": None,
        },
    )
    raw_output = response.output_text
    print("模型輸出：")
    print(raw_output)

    print()
    print("=== 其他資訊 ===")
    print(f"LLM call + 網路傳輸耗時: {time.time() - start_time:.2f} 秒")

    # 解析模型輸出。實務上會用 SDK 提供的結構化 tool calling，不會土炮 JSON parse
    output_data = json.loads(raw_output)
    answer = output_data.get("answer")
    tool_calls = output_data.get("tool_calls", [])

    # 把模型這一輪的回答加進對話歷史
    input_data.append({"role": "assistant", "content": raw_output})

    # 如果模型已經給出答案，就結束
    if answer is not None and not tool_calls:
        break

    # 否則就執行模型要求的每個工具，把結果回灌
    print()
    print("=== 執行工具 ===")
    tool_results = []
    for call in tool_calls:
        tool_name = call["tool_name"]
        arguments = call["arguments"]
        tool_func = getattr(tools, tool_name)
        result = tool_func(**arguments)
        print(f"執行工具 {tool_name}({arguments}) -> {result}")
        tool_results.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
        })

    input_data.append({
        "role": "user",
        "content": "以下是工具執行結果，請根據結果繼續：\n"
                   + json.dumps(tool_results, ensure_ascii=False),
    })
else:
    print()
    print(f"已達最大回合數 {MAX_TURNS}，仍未得到最終答案")
    answer = None

print()
print("=== 答案文字 ===")
print(answer)

