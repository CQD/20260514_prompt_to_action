"""
borrowing.csv 的查詢工具，給 run_agent_workshop.py 用。

工具的設計刻意「不太貼心」：
- 沒有提供「直接給我答案」的 high-level 工具
- 模型必須自己探索 schema、組合多次呼叫
這樣 agent loop 的 3 拍子才會自然出現。
"""

import csv

CSV_PATH = "borrowing.csv"

# 工作坊用固定日期，跟 borrowing.csv 的產生日期一致，確保答案可重現
# 實務上會用 datetime.date.today().isoformat()
TODAY = "2026-05-13"


def today() -> str:
    """回傳今天的日期，格式 YYYY-MM-DD。要算逾期、近期等時間相關問題時會用到。"""
    return TODAY


def _load() -> list[dict]:
    with open(CSV_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _match(row: dict, filters: list[dict]) -> bool:
    for f in filters:
        col = f["col"]
        op = f["op"]
        val = f.get("value")
        cell = row.get(col, "")
        if op == "eq":
            if cell != str(val):
                return False
        elif op == "ne":
            if cell == str(val):
                return False
        elif op == "startswith":
            if not cell.startswith(str(val)):
                return False
        elif op == "gt":
            try:
                if not (float(cell) > float(val)):
                    return False
            except ValueError:
                if not (cell > str(val)):
                    return False
        elif op == "lt":
            try:
                if not (float(cell) < float(val)):
                    return False
            except ValueError:
                if not (cell < str(val)):
                    return False
        elif op == "is_null":
            if cell != "":
                return False
        elif op == "is_not_null":
            if cell == "":
                return False
        else:
            raise ValueError(f"不支援的 op: {op}")
    return True


def list_columns() -> list[str]:
    """回傳 CSV 的所有欄位名稱。"""
    return list(_load()[0].keys())


def sample_rows(n: int = 3) -> list[dict]:
    """回傳前 n 筆資料，用來看欄位內容長什麼樣子。建議 n <= 5。"""
    return _load()[:n]


def query(filters: list[dict], limit: int = 20) -> list[dict]:
    """
    依條件查詢資料。
    filters 是條件列表，每個條件是 {"col": 欄位名, "op": 運算子, "value": 比對值}
    支援的 op:
      - "eq" / "ne": 等於 / 不等於
      - "startswith": 字首相符（適合日期前綴，如 "2026-04"）
      - "gt" / "lt": 大於 / 小於（會嘗試以數字比較，失敗則以字串比較）
      - "is_null" / "is_not_null": 該欄位為 / 不為空字串（不需要 value）
    多個條件之間是 AND 關係。
    """
    rows = [r for r in _load() if _match(r, filters)]
    return rows[:limit]


def count_by(group_by: str, filters: list[dict] | None = None) -> dict:
    """
    根據 filters 過濾後，依 group_by 欄位分組計數。
    回傳 {分組值: 數量}。
    例：count_by("category", [{"col": "borrowed_at", "op": "startswith", "value": "2026-04"}])
    """
    rows = _load()
    if filters:
        rows = [r for r in rows if _match(r, filters)]
    counts: dict[str, int] = {}
    for r in rows:
        key = r.get(group_by, "")
        counts[key] = counts.get(key, 0) + 1
    return counts
