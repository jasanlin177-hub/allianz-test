import json
import requests
from bs4 import BeautifulSoup
import os
import re

def update_from_allianz():
    url = "https://tw.allianzgi.com/zh-tw/products-solutions/taiwan-onshore/allianz-global-investors-taiwan-technology-fund?nav=overview"
    file_path = 'data.json'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    print(f"正在連線至安聯官網...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    nav_date = None
    nav_value = None

    # --- 策略：定位標題 (Label) 再找內容 (Value) ---
    
    try:
        # 1. 抓取日期
        # 尋找含有 "淨值日期" 的標題 (h3)
        date_label = soup.find('h3', string=re.compile("淨值日期"))
        if date_label:
            # 往後找下一個 <p> 標籤，日期就在裡面
            date_p = date_label.find_next('p')
            if date_p:
                raw_date_text = date_p.get_text(strip=True)
                # 預期格式 2026/02/10
                if re.match(r'\d{4}/\d{2}/\d{2}', raw_date_text):
                    nav_date = raw_date_text.replace('/', '-')

        # 2. 抓取淨值
        # 尋找含有 "最新淨值" 的標題 (h3)
        nav_label = soup.find('h3', string=re.compile("最新淨值"))
        if nav_label:
            # 往後找下一個 <p> 標籤，數值就在裡面
            # 結構是: <p>459.82 <span>新臺幣</span></p>
            nav_p = nav_label.find_next('p')
            if nav_p:
                # get_text() 會拿到 "459.82 新臺幣"
                raw_nav_text = nav_p.get_text(strip=True)
                # 移除中文、逗號與空白
                clean_nav = re.sub(r'[^\d.]', '', raw_nav_text)
                try:
                    nav_value = float(clean_nav)
                except ValueError:
                    print(f"數值轉換失敗: {raw_nav_text}")

    except Exception as e:
        print(f"⚠️ 解析過程發生錯誤: {e}")

    # --- 檢查結果 ---
    if not nav_date or not nav_value:
        print("❌ 解析失敗！")
        print(f"   找到的日期: {nav_date}")
        print(f"   找到的淨值: {nav_value}")
        return

    print(f"✅ 抓取成功！官網數據: 日期={nav_date}, 淨值={nav_value}")

    # --- 更新 JSON 檔案 ---
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
        except:
            full_data = []
    else:
        full_data = []

    # 取得最後一筆日期
    last_date = full_data[-1][0] if full_data else "1900-01-01"

    # 比對日期
    if nav_date > last_date:
        full_data.append([nav_date, nav_value])
        # 寫入檔案
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False)
        print(f"🎉 資料庫更新完成！已寫入 {nav_date} (淨值: {nav_value})。")
    elif nav_date == last_date:
        print(f"👌 資料已是最新 ({nav_date})，無需更新。")
    else:
        print(f"⚠️ 異常：官網日期 ({nav_date}) 舊於資料庫 ({last_date})。")

if __name__ == "__main__":
    update_from_allianz()
