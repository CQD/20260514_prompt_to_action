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

- today() -> str
    回傳今天的日期，格式 YYYY-MM-DD。要算逾期、近期等時間相關問題時會用到。

- list_columns() -> list[str]
    回傳 CSV 的所有欄位名稱。

- sample_rows(n: int) -> list[dict]
    回傳前 n 筆資料，用來理解欄位內容。建議 n <= 5。

- query(filters: list[dict], limit: int) -> list[dict]
    依條件查詢資料。filters 是條件列表，每個條件是：
      {"col": 欄位名, "op": 運算子, "value": 比對值}
    支援的 op：eq, ne, startswith, gt, lt, is_null, is_not_null
    多個條件之間是 AND 關係。limit 建議設 50 以內。

- count_by(group_by: str, filters: list[dict]) -> dict
    依 group_by 欄位分組計數（可選擇先用 filters 過濾）。
    例：count_by("category", [{"col": "borrowed_at", "op": "startswith", "value": "2026-04"}])

備註：
- 借閱期限是 14 天，超過視為逾期。「逾期 N 天」= 今天（或還書日）- 借出日 - 14
- CSV 不會直接給你「逾期天數」這個欄位，你需要自己算

規則：
- 一開始你不知道 CSV 有哪些欄位，請先用 list_columns 與 sample_rows 探索
- 不要試圖一次 query 全部資料，會塞爆你的記憶
- 當你已經有足夠資訊回答問題時，請直接回答，不再呼叫工具
- 你一次只能輸出一個完整 JSON 物件，不能輸出多個

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
