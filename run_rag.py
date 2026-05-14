import time

from openai import OpenAI

from credentials import OPENAI_KEY


# question = "台灣高鐵通車時間"
question = "宇宙戰艦高雄號的啟用時間"

######################################################

def get_article_instructions(question: str) -> str:

    # 實際上這裡是到資料庫/搜尋引擎去撈資料
    # 這裡為了測試方便，直接寫死一些文章內容
    articles = [
        {
            "title": "台灣高鐵介紹",
            "content": "台灣高速鐵路於 2007 年 1 月 5 日通車，全長約 350 公里，連接台北至高雄左營，最高時速可達 300 公里。",
        },
        {
            "title": "台北捷運簡介",
            "content": "台北捷運於 1996 年 3 月 28 日開始營運，目前共有 6 條主線，是台灣第一個都會區大眾捷運系統。",
        },
        {
            "title": "高雄捷運簡介",
            "content": "高雄捷運於 2008 年 3 月 9 日通車，是台灣第二個都會區捷運系統，目前有紅線與橘線兩條主要路線。",
        },
        {
            "title": "屏東宇宙港拆除計劃",
            "content": "屏東宇宙港原定於 2025 年啟用，但由於預算問題與環保抗議，計劃已經被迫取消，並將進行拆除作業。",
        },
    ]

    article_template = """\
<文章>
標題：{title}
內文：{content}
</文章>"""

    article_instructions = "\n".join(
        [article_template.format(title=article['title'], content=article['content']) for article in articles]
    )

    return article_instructions


def get_memory_instructions() -> str:

    # 實際上這裡是到記憶庫去撈資料
    # 這裡為了測試方便，直接寫死一些記憶內容
    recent_questions = [
        "台灣高鐵的票價是多少？",
        "為什麼火箭很難做？",
        "我好可憐，快安慰我一下！",
        "為什麼天空是黃色的？"
    ]

    user_defined_instructions = [
        "請盡量用華麗、浮誇、虛華、做作、中二的文筆回答問題，越誇張越好",
        "每句話最後，你都要用「然後是馬桶蓋」做結尾",
    ]

    notable_things = [
        "使用者對台灣高鐵很感興趣，之前問過相關問題很多次",
        "曾經非常排斥我稱呼他為「使用者」，最好用親暱一點的稱呼",
    ]

    memory_instruction_template = """\
<記憶>
使用者的近期提問：
{recent_questions}

其他值得注意的事情：
{notable_things}

使用者的額外要求：
{user_defined_instructions}
</記憶>"""

    memory_instruction = memory_instruction_template.format(
        recent_questions="\n".join([f"- {q}" for q in recent_questions]),
        notable_things="\n".join([f"- {thing}" for thing in notable_things]),
        user_defined_instructions="\n".join([f"- {instr}" for instr in user_defined_instructions]),
    )

    return memory_instruction

######################################################

client = OpenAI(api_key=OPENAI_KEY)

################################
# 從資料庫拉資料 (Retrieval)
################################
article_instructions = get_article_instructions(question)
memory_instructions = get_memory_instructions()

################################
# 組合指令文字 (Augmentation)
# 並呼叫模型產生答案 (Generation)
################################

prompt = f"""\
你是一個問答助手。

請根據以下提供的文章內容回答使用者問題。
若文章跟使用者的問題都無關聯，請回答「我不知道」，但講的更委婉。

{article_instructions}

{memory_instructions}

<使用者問題>{question}</使用者問題>"""

print("=== 指令文字 ===")
print(prompt)

print()
print("=== 答案文字 ===")
start_time = time.time()
response = client.responses.create(
    model="gpt-5.4-mini",
    input=prompt,
    reasoning={
        "effort": "none",
        "summary": None,
    },
)
print(response.output_text)

print()
print("=== 其他資訊 ===")
end_time = time.time()
print(f"LLM call + 網路傳輸耗時: {end_time - start_time:.2f} 秒")
