import json
import yfinance as yf
from datetime import datetime

def update_fund_data():
    file_path = 'data.json'
    
    # 1. 讀取舊數據
    with open(file_path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
    
    last_date_str = full_data[-1][0]
    
    # 2. 抓取新數據 (安聯台灣科技基金)
    fund = yf.Ticker("TW000T3604Y3.TW") # 請確認 Yahoo Finance 上的正確代碼
    hist = fund.history(period="5d") # 抓取最近5天確保不漏掉週五
    
    # 3. 合併數據
    updated = False
    for date, row in hist.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        price = round(float(row['Close']), 2)
        
        if date_str > last_date_str:
            full_data.append([date_str, price])
            updated = True
            
    # 4. 存回檔案
    if updated:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False)
        print(f"成功更新至 {full_data[-1][0]}")
    else:
        print("數據已是最新，無需更新")

if __name__ == "__main__":
    update_fund_data()
