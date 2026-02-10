import pandas as pd
import json
import os

def init_database():
    csv_file = 'history.csv' # 請確認您的檔案名稱
    json_file = 'data.json'

    if not os.path.exists(csv_file):
        print(f"找不到 {csv_file}，請先將歷史淨值 CSV 檔案放入資料夾。")
        return

    print("正在讀取 CSV 檔案...")
    
    # 讀取 CSV，跳過前 6 行 (根據您提供的檔案資訊)
    # 假設欄位名稱在第 7 行，分別為 "日期" 和 "淨值"
    try:
        df = pd.read_csv(csv_file, skiprows=6)
        
        # 重新命名欄位以防萬一 (依據常見格式)
        # 如果您的 CSV 欄位名稱不同，請在此調整
        df.columns = ['Date', 'NAV'] + list(df.columns[2:]) 
        
        # 只取前兩欄：日期與淨值
        df = df[['Date', 'NAV']]
        
        # 移除空值
        df.dropna(inplace=True)

        # 格式化資料
        output_data = []
        for index, row in df.iterrows():
            # 處理日期格式 YYYY/MM/DD -> YYYY-MM-DD
            raw_date = str(row['Date']).strip()
            date_str = raw_date.replace('/', '-')
            
            # 處理淨值 (移除可能存在的逗號)
            try:
                nav_val = float(str(row['NAV']).replace(',', ''))
                output_data.append([date_str, nav_val])
            except ValueError:
                continue

        # 依照日期排序 (舊 -> 新)
        output_data.sort(key=lambda x: x[0])

        # 寫入 JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
            
        print(f"轉換完成！共 {len(output_data)} 筆資料，已儲存為 {json_file}")
        print(f"最新一筆資料為: {output_data[-1]}")

    except Exception as e:
        print(f"轉換失敗: {e}")

if __name__ == "__main__":
    init_database()
