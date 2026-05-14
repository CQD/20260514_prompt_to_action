import time
from openai import OpenAI
from credentials import OPENAI_KEY

client = OpenAI(api_key=OPENAI_KEY)

start_time = time.time()

prompt = "你是誰"

prompt = """\
你是一個親切的問答助手

請回答使用者問題
若你沒有足夠的資訊回答，請回答「我不知道」，但講的更委婉
你回答的語氣，必須要浮誇、虛華、矯揉做作

<使用者問題>高雄宇宙港啟用時間</使用者問題>
"""


print("=== 系統指令 ===")
print(prompt)

response = client.responses.create(
   model="gpt-5.4-mini",
   input=prompt,
   reasoning={"effort": "none"},
)

end_time = time.time()

print()
print("=== 答案文字 ===")
print(response.output_text)

print()
print("=== 其他資訊 ===")
print(f"LLM call + 網路傳輸耗時: {end_time - start_time:.2f} 秒")
