"""
Workshop 第二關：圖書館借閱資料分析 agent

borrowing.csv 是一份 500 筆的圖書館借閱紀錄。
你的任務：透過 tools_csv 提供的工具，讓 agent 自己探索 schema 並回答下列問題。

題目（任挑一題開始，做完換下一題）：
1. 2026 年 4 月，哪個分類的借閱次數最多？前三名是？
2. 目前還沒還、且逾期超過 7 天的人有誰？最久的逾期幾天？
3. 過去半年（2025-11-13 之後）借最多書的使用者是誰？他最愛哪個分類？

觀察重點：
- 模型有沒有先探索 schema 再下手？
- 一次撈太多會發生什麼事？
- 模型會不會幻覺出不存在的欄位 / 運算子？
- 你會怎麼改 system_prompt 或工具描述，讓 agent 表現更好？

------------------------------------------------------------
你的任務：完成下方 system_prompt 的工具描述

打開 tools_csv.py，把裡面提供的工具用「模型看得懂的文字」
寫進下方 system_prompt 的 TODO 區塊。

跑跑看 → 觀察 agent 在哪一步失敗 → 回頭改描述 → 再跑
這個迭代過程就是 agent 開發的日常。
------------------------------------------------------------
"""

import json
import time

from openai import OpenAI

from credentials import OPENAI_KEY
import tools_csv as tools


client = OpenAI(api_key=OPENAI_KEY)


user_input = "目前還沒還、且逾期超過 7 天的人有誰？最久的逾期幾天"


system_prompt = """\
你是個資料分析助手，幫助使用者從 CSV 資料庫中查詢資訊。你可以使用以下工具：

# === TODO：描述工具 ===
# 打開 tools_csv.py，把裡面的每個函式寫成模型看得懂的文字描述。
# 建議格式（你可以自己換）：
#   - 工具名(參數: 型別) -> 回傳型別
#       一句話說明它做什麼、何時該用、有什麼注意事項
#
# 範例（送你第一個，剩下自己補）：

- today() -> str
    回傳今天的日期，格式 YYYY-MM-DD。要算逾期、近期等時間相關問題時會用到。

# (其他工具請寫在這裡)


# === TODO：補充規則 ===
# 想想模型容易踩什麼雷，要怎麼提前提醒它？
# （第一次跑完、看到它哪裡卡住，再回來補會更清楚要寫什麼）
- 當你已經有足夠資訊回答問題時，請直接回答，不再呼叫工具

輸出格式（必須是合法 JSON）：
- 還需要呼叫工具時：
  {"answer": null, "tool_calls": [{"tool_name": "...", "arguments": {...}}]}
- 已經有答案時：
  {"answer": "完整的回答句子", "tool_calls": []}
"""

input_data = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

print("=== 系統指令 ===")
print(system_prompt)

print()
print("=== 使用者問題 ===")
print(user_input)

MAX_TURNS = 8
start_time = time.time()
answer = None

for turn in range(1, MAX_TURNS + 1):
    print()
    print(f"=== 第 {turn} 回合 ===")

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=input_data,
        reasoning={"effort": "none", "summary": None},
    )
    raw_output = response.output_text
    print("模型輸出：")
    print(raw_output)

    output_data = json.loads(raw_output)
    answer = output_data.get("answer")
    tool_calls = output_data.get("tool_calls", [])

    input_data.append({"role": "assistant", "content": raw_output})

    if answer is not None and not tool_calls:
        break

    tool_results = []
    for call in tool_calls:
        tool_name = call["tool_name"]
        arguments = call["arguments"]
        tool_func = getattr(tools, tool_name, None)
        if tool_func is None:
            result = f"ERROR: 不存在的工具 {tool_name}"
        else:
            try:
                result = tool_func(**arguments)
            except Exception as e:
                result = f"ERROR: {type(e).__name__}: {e}"
        # 預覽長度截斷，避免 console 被洗版
        preview = str(result)
        if len(preview) > 200:
            preview = preview[:200] + "..."
        print(f"執行 {tool_name}({arguments}) -> {preview}")
        tool_results.append({
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
        })

    input_data.append({
        "role": "user",
        "content": "工具執行結果，請根據結果繼續：\n"
                   + json.dumps(tool_results, ensure_ascii=False, default=str),
    })
else:
    print(f"\n已達最大回合數 {MAX_TURNS}，仍未得到最終答案")
    answer = None

end_time = time.time()

print()
print("=== 最終答案 ===")
print(answer)

print()
print(f"耗時: {end_time - start_time:.2f} 秒")
