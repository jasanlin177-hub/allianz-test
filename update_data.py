import json
import requests
from bs4 import BeautifulSoup
import os
import re

def update_from_allianz():
    # 安聯台灣科技基金 - 概覽頁面
    url = "https://tw.allianzgi.com/zh-tw/products-solutions/taiwan-onshore/allianz-global-investors-taiwan-technology-fund?nav=overview"
    file_path = 'data.json'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    print(f"正在連線至安聯官網...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ 連線失敗: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Debug: 顯示網頁標題，確認沒有跑到錯誤頁面
    print(f"網頁標題: {soup.title.string.strip() if soup.title else '無標題'}")

    nav_date = None
    nav_value = None

    # --- 策略 A: 關鍵字定位法 (比 class 更穩定) ---
    # 尋找含有「淨值日期」文字的標籤
    try:
        # 1. 抓日期
        # 方法：找到所有文字，用正規表達式抓 YYYY/MM/DD
        text_content = soup.get_text()
        date_match = re.search(r'(\d{4}/\d{2}/\d{2})', text_content)
        if date_match:
            raw_date = date_match.group(1)
            # 簡單驗證一下日期是否合理 (例如是 2024, 2025, 2026 年)
            if raw_date.startswith(('2024', '2025', '2026')):
                nav_date = raw_date.replace('/', '-')
        
        # 2. 抓淨值
        # 方法：找到「新臺幣」前面的數字
        # 網頁結構通常是: "459.82 新臺幣"
        # 我們搜尋包含 "新臺幣" 的元素
        currency_tags = soup.find_all(string=re.compile("新臺幣"))
        for tag in currency_tags:
            parent_text = tag.parent.get_text(strip=True) # 取得完整字串 "459.82 新臺幣"
            # 嘗試提取前面的數字
            # 移除逗號與文字
            clean_text = parent_text.replace('新臺幣', '').replace(',', '').strip()
            # 檢查是否為純數字 (浮點數)
            if re.match(r'^\d+(\.\d+)?$', clean_text):
                potential_val = float(clean_text)
                # 過濾掉不合理的數字 (例如 0 或太小的數字)
                if potential_val > 10: 
                    nav_value = potential_val
                    break # 找到就停止

    except Exception as e:
        print(f"⚠️ 解析過程發生錯誤: {e}")

    # --- 檢查結果 ---
    if not nav_date or not nav_value:
        print("❌ 解析失敗！")
        print("   找到的日期:", nav_date)
        print("   找到的淨值:", nav_value)
        # 如果還是失敗，可以考慮把 response.text 印出來的一小部分看看到底抓到什麼
        return

    print(f"✅ 抓取成功！官網數據: 日期={nav_date}, 淨值={nav_value}")

    # --- 更新 JSON 檔案 ---
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️ data.json 格式損毀，將重新建立")
            full_data = []
    else:
        full_data = []

    last_date = full_data[-1][0] if full_data else "1900-01-01"

    if nav_date > last_date:
        full_data.append([nav_date, nav_value])
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False)
        print(f"🎉 資料庫更新完成！已寫入 {nav_date}。")
    elif nav_date == last_date:
        print(f"👌 資料已是最新 ({nav_date})，無需更新。")
    else:
        print(f"⚠️ 異常：官網日期 ({nav_date}) 舊於資料庫日期 ({last_date})，不執行寫入。")

if __name__ == "__main__":
    update_from_allianz()
