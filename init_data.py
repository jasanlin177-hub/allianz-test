import pandas as pd
import json
import os

def init_database():
    csv_file = 'history.csv' 
    json_file = 'data.json'

    if not os.path.exists(csv_file):
        print(f"❌ 錯誤：找不到 {csv_file}")
        return

    # 1. 嘗試不同的編碼讀取 (解決 Excel 匯出亂碼問題)
    encodings = ['utf-8', 'cp950', 'big5', 'utf-8-sig']
    df = None
    
    for enc in encodings:
        try:
            # 先不略過行數，把整個檔案讀進來找標題
            print(f"嘗試使用 {enc} 編碼讀取...")
            df = pd.read_csv(csv_file, encoding=enc, header=None)
            print(f"✅ 成功使用 {enc} 讀取！")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️ {enc} 讀取發生其他錯誤: {e}")

    if df is None:
        print("❌ 所有編碼嘗試皆失敗，請確認 CSV 檔案格式。")
        return

    # 2. 自動尋找「標題行」 (解決 skiprows 算錯問題)
    header_row_index = -1
    date_col_idx = -1
    nav_col_idx = -1

    # 掃描前 20 行，尋找含有 "日期" 和 "淨值" 關鍵字的行
    for i, row in df.head(20).iterrows():
        row_str = row.astype(str).str.cat(sep=',') # 將整行轉為字串方便搜尋
        if "日期" in row_str and "淨值" in row_str:
            header_row_index = i
            # 鎖定欄位索引
            for col_idx, cell_val in enumerate(row):
                cell_str = str(cell_val).strip()
                if "日期" in cell_str:
                    date_col_idx = col_idx
                elif "淨值" in cell_str:
                    nav_col_idx = col_idx
            break
    
    if header_row_index == -1:
        print("❌ 找不到含有『日期』與『淨值』的標題列。請檢查 CSV 內容。")
        # 印出前 5 行幫助除錯
        print("前 5 行內容預覽：")
        print(df.head(5))
        return

    print(f"📍 在第 {header_row_index + 1} 行找到標題。")
    print(f"   日期欄位索引: {date_col_idx}, 淨值欄位索引: {nav_col_idx}")

    # 3. 擷取有效數據
    output_data = []
    
    # 從標題行的下一行開始讀取
    for i in range(header_row_index + 1, len(df)):
        try:
            row = df.iloc[i]
            raw_date = str(row[date_col_idx]).strip()
            raw_nav = str(row[nav_col_idx]).strip()

            # 檢查是否為空行
            if raw_date == 'nan' or raw_nav == 'nan' or raw_date == '':
                continue

            # 格式化日期 (YYYY/MM/DD -> YYYY-MM-DD)
            date_str = raw_date.replace('/', '-')
            
            # 格式化淨值 (移除逗號)
            nav_val = float(raw_nav.replace(',', ''))
            
            output_data.append([date_str, nav_val])
        except Exception as e:
            # 略過解析失敗的行 (可能是頁尾註釋)
            continue

    # 4. 排序並存檔
    if output_data:
        output_data.sort(key=lambda x: x[0])
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False)
            
        print(f"🎉 成功！已產生 {json_file}，共 {len(output_data)} 筆資料。")
        print(f"   第一筆: {output_data[0]}")
        print(f"   最後筆: {output_data[-1]}")
    else:
        print("❌ 警告：沒有擷取到任何有效數據。")

if __name__ == "__main__":
    init_database()
