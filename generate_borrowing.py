"""
產生 workshop 用的 borrowing.csv（500 筆圖書館借閱紀錄）

設計要點（給講師看的）：
- 日期範圍：2025-08-01 ~ 2026-05-13（TODAY）
- 借閱期限 14 天，超過視為逾期
- 2026-04 有刻意拉高的活動量，且 "小說" 在 4 月會明顯領先（讓題目 1 有清楚答案）
- 使用者借閱量分布偏斜：少數人佔大多數借閱（讓題目 3 有清楚答案）
- 約 18% 仍未歸還（returned_at 為空）；其中部分逾期超過 7 天（題目 2）
- 故意保留的 edge case：returned_at 為空字串、同一書多次被借
- 逾期天數不存進 CSV——那是衍生狀態，應該由 agent 拿 today() 跟 borrowed_at/returned_at 自己算
"""

import csv
import random
from datetime import date, timedelta

random.seed(20260514)

TODAY = date(2026, 5, 13)
START = date(2025, 8, 1)
LOAN_DAYS = 14
TOTAL_ROWS = 500

books = {
    "小說": ["百年孤寂", "82年生的金智英", "解憂雜貨店", "活著", "房思琪的初戀樂園",
             "刺殺騎士團長", "克拉拉與太陽", "正常人", "我們最幸福", "蛤蟆先生去看心理師"],
    "散文": ["山茶花文具店", "我輩中人", "雜貨店老闆的人生諮詢", "正午時分", "我的職業是電影"],
    "詩集": ["你的姿勢與我的", "夜的命名術", "願你和這世界溫柔相擁"],
    "科普": ["人類大命運", "時間的形狀", "宇宙的故事", "基因：人類最親密的歷史", "薛丁格的小狗"],
    "歷史": ["人類大歷史", "槍炮、病菌與鋼鐵", "海洋與文明", "絲綢之路", "翻轉地中海"],
    "哲學": ["蘇菲的世界", "活出意義來", "正義：一場思辨之旅", "你的善良必須有點鋒芒"],
    "程式設計": ["Clean Code", "深入淺出設計模式", "演算法圖鑑", "重構", "程式設計師的自我修養"],
    "商業": ["從0到1", "原子習慣", "高效能人士的七個習慣", "底層邏輯", "槓桿啟動"],
    "心理": ["被討厭的勇氣", "心流", "情緒勒索", "脆弱的力量", "蛤蟆先生再次出發"],
    "旅遊": ["京都漫步", "義大利這玩藝", "西藏自助行", "走過愛琴海"],
}

book_list = [(t, cat) for cat, titles in books.items() for t in titles]
book_id_map = {(t, cat): f"B{1000 + i:04d}" for i, (t, cat) in enumerate(book_list)}

users = [
    "王小明", "陳怡君", "林志豪", "李雅婷", "張家瑋", "黃淑芬", "吳俊宏", "蔡欣怡",
    "劉柏翰", "周淑慧", "鄭文傑", "謝佩珊", "許志明", "曾雅雯", "邱建宏", "賴麗華",
    "宋宇翔", "蘇佳玲", "高雅芳", "潘建志", "簡睿哲", "盧美玲", "彭嘉怡", "顧家慶",
    "孟祥雲", "范文軒", "童思妤", "白勝文", "湯雅惠", "嚴俊宇", "夏宛庭", "藍俊偉",
    "戴佳穎", "葛子安", "馬奕辰", "傅嘉玲", "倪心妤", "畢柏翔", "卓士豪", "鄒雅筑",
]

# 借閱量分布偏斜：少數重度使用者
user_weights = [random.choices([1, 4, 12, 30], weights=[35, 30, 25, 10])[0] for _ in users]

# 每個使用者有 1-3 個偏好分類（60% 的借閱會落在偏好分類）
user_prefs = {u: random.sample(list(books.keys()), k=random.randint(1, 3)) for u in users}


def random_date():
    # 25% 的紀錄落在 2026-04，製造 4 月活動高峰
    if random.random() < 0.25:
        return date(2026, 4, random.randint(1, 30))
    days_range = (TODAY - START).days
    return START + timedelta(days=random.randint(0, days_range))


def pick_book_for(user, borrowed_at):
    if borrowed_at.year == 2026 and borrowed_at.month == 4:
        # 4 月：小說明顯領先
        cat = random.choices(
            list(books.keys()),
            weights=[40, 18, 4, 8, 12, 3, 5, 6, 8, 3],
        )[0]
    else:
        if random.random() < 0.6:
            cat = random.choice(user_prefs[user])
        else:
            cat = random.choice(list(books.keys()))
    title = random.choice(books[cat])
    return title, cat


rows = []
for _ in range(TOTAL_ROWS):
    user = random.choices(users, weights=user_weights)[0]
    borrowed_at = random_date()
    title, cat = pick_book_for(user, borrowed_at)
    book_id = book_id_map[(title, cat)]

    # 82% 已歸還
    if random.random() < 0.82:
        loan_days = random.choices(
            [3, 7, 10, 12, 14, 16, 20, 28, 40],
            weights=[10, 15, 20, 20, 15, 10, 5, 3, 2],
        )[0]
        returned_at = borrowed_at + timedelta(days=loan_days)
        if returned_at > TODAY:
            # 預定還書日還沒到 -> 視為尚未歸還
            returned_at = None
    else:
        returned_at = None

    rows.append({
        "book_id": book_id,
        "title": title,
        "category": cat,
        "user": user,
        "borrowed_at": borrowed_at.isoformat(),
        "returned_at": returned_at.isoformat() if returned_at else "",
    })

rows.sort(key=lambda r: r["borrowed_at"])

with open("borrowing.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["book_id", "title", "category", "user", "borrowed_at", "returned_at"],
    )
    writer.writeheader()
    writer.writerows(rows)

# 印一些統計，方便確認資料品質
from collections import Counter

apr_rows = [r for r in rows if r["borrowed_at"].startswith("2026-04")]
apr_cats = Counter(r["category"] for r in apr_rows)
unreturned = [r for r in rows if r["returned_at"] == ""]
# 逾期超過 7 天 == 借出超過 14+7=21 天且未還
overdue7 = [
    r for r in unreturned
    if (TODAY - date.fromisoformat(r["borrowed_at"])).days > LOAN_DAYS + 7
]
recent = [r for r in rows if r["borrowed_at"] >= "2025-11-13"]
top_users = Counter(r["user"] for r in recent).most_common(3)

print(f"總筆數: {len(rows)}")
print(f"2026-04 借閱數: {len(apr_rows)}，分類前三: {apr_cats.most_common(3)}")
print(f"尚未歸還: {len(unreturned)}，其中逾期超過 7 天: {len(overdue7)}")
print(f"近半年借閱前三名: {top_users}")
