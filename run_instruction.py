import time
from openai import OpenAI
from credentials import OPENAI_KEY


client = OpenAI(api_key=OPENAI_KEY)

article = open("article_red_hood.txt", "r").read()
# article = open("article_eastbound.txt", "r").read()

system_prompt = """\
你要負責分析輸入的長文字，輸出規則
- 文章的摘要（五十字內）
- 文章內有哪些人物
  - 文章內沒有人物的時候，請輸出空陣列
- 適合的文章 tag（如：旅遊、科技、運動等），最多五個

輸出 ** 必須是合法 JSON **
輸出範例如下：
```
{
    "summary": "{文章摘要}",
    "characters": ["{人物1}", "{人物2}", ...],
    "tags": ["{tag1}", "{tag2}", ...]
}
```"""

# 注意照理的 input data 不是純文字，而是有資料結構的東西
# 實際上 OpenAI 的系統背後還是會把 input data 轉成類似純文字的東西
# 但是透過 input data 的資料結構，他們可以用特定 token 作為分隔
# 讓模型更好理解輸入的內容
input_data = [
    {
        "role": "system",
        "content": system_prompt,
    },
    {
        "role": "user",
        "content": article,
    }
]

print("=== 系統指令 ===")
print(system_prompt)

print()
print("=== 輸入文字 ===")
trim_size = 50
print(article[:trim_size] + "..." if len(article) > trim_size else article)

start_time = time.time()
response = client.responses.create(
    model="gpt-5.4-mini",
    input=input_data,
    reasoning={
        "effort": "none",
        "summary": None,
    },
)

print()
print("=== 答案文字 ===")
print(response.output_text)

print()
print("=== 其他資訊 ===")
end_time = time.time()
print(f"LLM call + 網路傳輸耗時: {end_time - start_time:.2f} 秒")
