安聯台灣科技基金 - 淨值回測系統
程式架構說明與維護手冊
版本： 2.0 (Pro)
更新日期： 2026-02-11
開發者：jasanlin177-hub
________________________________________
1. 專案概述 (Project Overview)
本專案是一個全自動化的金融數據視覺化系統。旨在每日自動抓取「安聯台灣科技基金」的最新淨值，並透過網頁介面提供歷史走勢圖、回撤風險分析（水下圖），以及單筆/定期定額的投資試算功能。
核心技術棧
•	數據抓取 (Crawler): Python 3 (Requests, BeautifulSoup, Re)
•	前端介面 (Frontend): HTML5, Tailwind CSS (樣式), Chart.js (圖表)
•	自動化運維 (DevOps): GitHub Actions (排程執行), GitHub Pages (靜態託管)
•	資料庫 (Database): JSON 檔案 (輕量化儲存)
________________________________________
2. 系統運作流程 (System Architecture)
系統採用 Serverless (無伺服器) 架構，完全依賴 GitHub 提供的免費資源運作。
程式碼片段
graph TD
    A[安聯投信官網] -->|每日爬蟲| B(Python 腳本 update_data.py)
    B -->|讀取與寫入| C[(data.json)]
    D[GitHub Actions] -->|排程觸發 (每日 19:00)| B
    C -->|Git Commit & Push| E[GitHub Repository]
    E -->|自動部署| F[GitHub Pages 伺服器]
    G[使用者瀏覽器] -->|Fetch API| F
    F -->|回傳 JSON 數據| G
    G -->|JavaScript 渲染| H[互動式儀表板]
________________________________________
3. 檔案結構說明 (File Structure)
檔案/路徑	類型	說明	重要性
.github/workflows/daily_update.yml	YAML	自動化心臟。設定排程時間、安裝 Python 套件、賦予寫入權限。	⭐⭐⭐⭐⭐
update_data.py	Python	爬蟲大腦。負責連線官網、解析 HTML、更新 JSON 檔。	⭐⭐⭐⭐⭐
index.html	HTML	網站本體。包含 UI 介面、圖表繪製邏輯、試算核心算法。	⭐⭐⭐⭐⭐
data.json	JSON	資料庫。儲存從 2001 年至今的所有日期與淨值數據。	⭐⭐⭐⭐
init_data.py	Python	初始化工具。用於第一次將 Excel/CSV 轉檔為 JSON (平常不會用到)。	⭐⭐
________________________________________
4. 核心模組詳細邏輯
A. 資料抓取模組 (update_data.py)
採用 「定位標題法 (Label Positioning Strategy)」，而非傳統的 CSS Selector，以對抗網頁改版。
1.	搜尋關鍵字： 在 HTML 中搜尋 h3 標籤含有「淨值日期」與「最新淨值」的區塊。
2.	相對定位： 找到標題後，抓取其緊鄰的下一個 <p> 標籤內容。
3.	數據清洗： 使用正規表達式 (Regex) 移除「新臺幣」、逗號與空白，僅保留純數字與日期格式 (YYYY-MM-DD)。
4.	增量更新： 比對 data.json 最後一筆日期，只有當官網日期 大於 資料庫日期時才寫入，避免重複。
B. 自動化模組 (daily_update.yml)
1.	觸發時機： 設定為 cron: '0 11 * * *' (UTC 時間 11:00，即台灣時間 19:00)。
2.	權限設定： permissions: contents: write，確保機器人有權限將更新後的 JSON 檔存回儲存庫。
3.	環境建置： 每次執行都會開啟一台 Ubuntu 虛擬機，安裝 requests, beautifulsoup4, pandas。
C. 前端視覺化模組 (index.html)
1.	雙拉桿滑桿 (Dual-Thumb Slider)：
o	使用 CSS pointer-events 技巧，解決兩個滑桿重疊時無法點擊的問題。
o	使用 Debounce (防抖) 技術，拖曳時只更新視覺，停止動作 50ms 後才進行繁重的圖表運算，確保手機操作流暢。
2.	回撤風險圖 (Drawdown Chart)：
o	算法：(當日淨值 - 歷史至今最高淨值) / 歷史至今最高淨值 * 100%。
o	用途：顯示資產在最壞情況下的縮水幅度。
3.	RWD 響應式設計：
o	導航欄在手機版自動轉為垂直排列。
o	圖表高度在手機版自動調整，避免超出螢幕。
________________________________________
5. 維護與故障排除 (Troubleshooting)
Q1: 網頁上的數據沒有更新？
1.	檢查 GitHub Actions： 進入 GitHub -> Actions 頁面。
o	如果是 紅色叉叉：點進去查看 Log 報錯原因。
o	如果是 綠色勾勾：代表抓取成功，請進行下一步。
2.	強制重新整理： 在瀏覽器按 Ctrl + F5 (Windows) 或 Cmd + Shift + R (Mac) 清除快取。
3.	檢查部署狀態： 檢查 Actions 中的 pages-build-deployment 任務是否也顯示綠燈。
Q2: GitHub Actions 報錯 "403 Forbidden"？
•	原因： 機器人沒有寫入權限。
•	解法： 檢查 .github/workflows/daily_update.yml 是否包含以下代碼：
YAML
permissions:
  contents: write
或是到 Settings -> Actions -> General -> Workflow permissions 確認已勾選 "Read and write permissions"。
Q3: GitHub Actions 報錯 "AttributeError: 'NoneType' object has no attribute..."？
•	原因： 安聯官網改版了，導致爬蟲抓不到標題。
•	解法：
1.	用瀏覽器打開安聯官網，按 F12 觀察「淨值日期」與「淨值」的 HTML 結構。
2.	修改 update_data.py 中的 BeautifulSoup 搜尋邏輯 (例如修改標籤名 h3 或搜尋關鍵字)。
Q4: 網頁顯示 404 Not Found？
•	原因： index.html 被誤刪，或 GitHub Pages 設定跑掉。
•	解法：
1.	確認 GitHub 檔案列表中有 index.html 和 data.json。
2.	到 Settings -> Pages，確認 Branch 是 main，Folder 是 /(root)。
3.	隨便修改一下 index.html (加個空行) 並 Commit，強迫觸發重新部署。
________________________________________
6. 未來擴充建議
如果您未來想升級此系統，可以考慮：
1.	多基金比較： 修改 data.json 結構，加入第二支基金的數據，並在圖表中增加線條比較。
2.	匯率轉換： 如果加入美元計價基金，需串接匯率 API 進行換算。
3.	通膨調整： 加入 CPI 數據，計算實質報酬率。
________________________________________
備註： 本系統僅供個人研究與回測參考，不代表投資建議。數據來源為安聯投信官網，如有落差以官網為準。

