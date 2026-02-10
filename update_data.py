import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

def update_from_allianz():
    url = "https://tw.allianzgi.com/zh-tw/products-solutions/taiwan-onshore/allianz-global-investors-taiwan-technology-fund?nav=overview"
    file_path = 'data.json'
    
    # 模擬瀏覽器 Header，避免被擋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"正在連線至安聯官網...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"連線失敗: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- 解析邏輯 (針對您提供的 HTML 結構) ---
    # 策略：尋找包含「新臺幣」單位的區塊，這通常是淨值，而它的前一個同級元素通常是日期
    
    nav_value = None
    nav_date = None

    # 1. 抓取淨值
    # 尋找 <span class="c-fund-summary-banner__currency">新臺幣</span>
    currency_span = soup.find('span', class_='c-fund-summary-banner__currency')
    
    if currency_span:
        # 淨值通常在 span 的父層 <p> 文字中
        nav_p = currency_span.find_parent('p')
        if nav_p:
            # 取出文字 "459.82 新臺幣"，移除單位與空白
            raw_text = nav_p.get_text(strip=True)
            nav_str = raw_text.replace('新臺幣', '').replace(',', '').strip()
            try:
                nav_value = float(nav_str)
            except ValueError:
                print("解析淨值數值失敗")

            # 2. 抓取日期
            # 日期通常是淨值 <p> 的「前一個兄弟元素」
            # 尋找前一個 <p>
            date_p = nav_p.find_previous_sibling('p')
            if date_p:
                raw_date = date_p.get_text(strip=True)
                # 格式通常為 2026/02/10，轉換為 2026-02-10
                nav_date = raw_date.replace('/', '-')

    if not nav_value or not nav_date:
        print("無法在頁面上解析出日期或淨值，網頁結構可能已變更。")
        return

    print(f"官網最新數據: 日期={nav_date}, 淨值={nav_value}")

    # --- 更新 JSON 檔案 ---
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    else:
        full_data = []

    last_date = full_data[-1][0] if full_data else "1900-01-01"

    if nav_date > last_date:
        full_data.append([nav_date, nav_value])
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False)
        print(f"更新成功！已寫入 {nav_date} 的淨值。")
    elif nav_date == last_date:
        print("資料已是最新，無需更新。")
    else:
        print(f"異常：官網日期 ({nav_date}) 舊於資料庫日期 ({last_date})。")

if __name__ == "__main__":
    update_from_allianz()
