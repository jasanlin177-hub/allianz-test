# update_data.py
from core.engine import IndexEngine
from datetime import datetime

def daily_job():
    engine = IndexEngine()
    today_str = datetime.now().strftime("%Y%m%d")
    print(f"開始執行每日更新: {today_str}")
    
    # 調用你原本在管理後台寫的批次更新邏輯
    # 注意：這裡不傳入進度條回調函數
    res = engine.run_batch_update(today_str)
    print(f"更新結果: {res}")

if __name__ == "__main__":
    daily_job()
