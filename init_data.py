import pandas as pd
import json
import os

def init_database():
    csv_file = 'history.csv' 
    json_file = 'data.json'

    if not os.path.exists(csv_file):
        print(f"找不到 {csv_file}")
        return

    print("正在讀取 CSV 檔案...")
    
    try:
        # 根據您的檔案結構，標題在第 7 行 (所以跳過前 6 行)
        df = pd.read_csv(csv_file, skiprows=6)
        
        # 重新命名欄位以確保程式讀取正確 (強制指定前兩欄為 Date 與 NAV)
        # 這樣就算 CSV 標題寫 "日期" 或 "Date" 都能通
        df.columns.values[0] = 'Date'
        df.columns.values[1] = 'NAV'
        
        # 只取前兩欄
        df = df[['Date', 'NAV']]
        
        # 移除空值
        df.dropna(inplace=True)

        # 格式化資料
        output_data = []
        for index, row in df.iterrows():
            raw_date = str(row['Date']).strip()
            # 將 YYYY/MM/DD 轉為 YYYY-MM-DD
            date_str = raw_date.replace('/', '-')
            
            try:
                # 移除數字中的逗號 (例如 1,234.56 -> 1234.56)
                nav_val = float(str(row['NAV']).replace(',', ''))
                output_data.append([date_str, nav_val])
            except ValueError:
                continue

        # 依照日期排序
        output_data.sort(key=lambda x: x[0])

        # 產出 data.json
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
            
        print(f"成功！已產生 {json_file}，共 {len(output_data)} 筆資料。")

    except Exception as e:
        print(f"轉換失敗: {e}")

if __name__ == "__main__":
    init_database()
