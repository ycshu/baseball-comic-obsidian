# baseball-comic-obsidian（課程協作 Repo）

本 Repo 用於『愛（AI）看野球番：以生成式AI打造「棒球漫畫」互動導覽』五日課程的資料協作。課程moodle: https://moodle.ncku.edu.tw/course/view.php?id=55256
每位同學會在自己的筆電上使用 Obsidian 整理資料，並透過 GitHub Desktop 提交到本 Repo，最後由課程網站（GitHub Pages）https://ycshu.github.io/baseball-comic-obsidian/ 讀取 `data/` 內資料，協助產生可餵給 ChatGPT / Gemini 的漫畫故事腳本。

---

## Day 2 你要完成什麼？

這是一個每個人都有的作業，老師會依完成度來評分，**不是有完成就滿分**，會看你提供的資料量，完整度，也包含你在上傳時commit的註解，是否有違反協作的規定等等(如修改到其他同學的資料)。

1. 用 GitHub Desktop **Clone** 本 Repo https://github.com/ycshu/baseball-comic-obsidian.git 到你的電腦
2. 建立你的個人分支（branch）：`data-你的學號`
3. 在你的電腦上，該repo的 `data/students/<9碼學號>/` 建立你的資料夾與 vault
4. 把你原本的 Obsidian vault **搬到上述資料夾中的位置**
5. 透過 export.py (可以自行與生成式AI協作，整理你的資料) 產生 `index.json` 
6. Commit + Push
7. 建立 Pull Request（PR）

老師合併 PR 後，你的學號/名字會出現在課程網站底部「資料提供者」清單。

---

## 事前準備：必裝軟體

請確認你已安裝下列軟體（Day 2 會用到）：

必需要有的：
1. Git: https://git-scm.com/install/windows
2. GitHub Desktop: https://desktop.github.com/download/ 

可自行選擇的:
3. Visual Studio Code: https://code.visualstudio.com/Download
4. Python: https://www.python.org/ftp/python/3.14.2/python-3.14.2-amd64.exe
5. antigravity: https://antigravity.google/

---

## GitHub 帳號（沒有一定要先註冊）

若你沒有 GitHub 帳號，請先完成：
1. 到 GitHub 註冊：https://github.com
2. 建立帳號並登入（請用未來會持續使用的帳號）
3. 在 GitHub Desktop 內登入同一個帳號

---

## Day 2 操作指南（GitHub Desktop 版）

### Step 1｜Clone 課程 Repo

1. 打開 GitHub Desktop
2. File → Clone repository...
3. 選 URL，貼上：
   `https://github.com/ycshu/baseball-comic-obsidian`
4. 選你找得到的位置（建議 Documents），按 Clone

你會得到本機資料夾：`baseball-comic-obsidian/`

---

### Step 2｜建立你的分支（Branch）

1. 在 GitHub Desktop 上方點 Current branch
2. New branch
3. Branch 名稱請用：
   `data-你的學號`

例：`data-A12345678`

---

### Step 3｜建立你的資料夾結構（嚴格遵守）

請在 repo 內建立：

data/students/你的學號/
├─ vault/  (你在 obsidian 中所建立的資料夾就是選擇放這裡)
├─ export.py (可從tools/export/中複製)
├─ run_export.bat (Windows) (可從tools/export/中複製)
├─ run_export.command (macOS) (可從tools/export/中複製)
└─ sources.md (資料來源與授權說明)


重要規範（必讀）：
- `你的學號` 必須是 **9 碼英數字**
- 你的資料必須放在 `data/students/你的學號/` 底下
- 每人只改自己的資料夾，避免衝突

---

### Step 4｜把你原本的 Obsidian vault 搬到指定位置（關鍵）

很多同學的 vault 可能在桌面、OneDrive、Downloads 或其他位置。  
請將你原本的 vault（整個資料夾）搬到：

`data/students/你的學號/vault/`

之後用 Obsidian：
- Open folder as vault
- 指到新的 `vault/`

---

### Step 5｜產生 index.json（不用打指令）

在 `data/students/你的學號/` 內執行：

- Windows：雙擊 `run_export.bat`
- macOS：雙擊 `run_export.command`

成功標誌：
- 出現 `index.json`

你需要與生成式AI討論怎麼修改 export.py ，來將你在obsidian中所整理的資料，匯整成將來可以被查詢的樣態

---

### Step 6｜Commit + Push + Pull Request(PR)

1. 回到 GitHub Desktop
2. Summary 輸入：`Add dataset for 你的學號`
3. Commit to `data-你的學號`
4. Push origin (Ctrl+P)
5. Create Pull Request（PR）

---

## 如何確認你已完成（PR 是否成功）

老師合併 PR 後：
- 打開課程網站
- 頁面最下方「資料提供者」清單出現你的學號/名字  
代表你的資料已進入 main，可被網站讀取。

---

## 給同學的提醒（常見錯誤）

- 遇到問題先看：debug/README.md
- 學號不是 9 碼英數字 → 網頁掃不到
- 資料夾放錯層級（不在 `data/students/你的學號`）→ 網頁掃不到
- 沒有產生 index.json → PR 合併後也無法被網站讀取
- 不要改別人的資料夾或系統檔案（只改自己的學號資料夾）

---

## Export 工具位置（老師提供）

Repo 內提供標準版匯出工具（請複製到你的學號資料夾使用）：

`tools/export/`
- export.py
- run_export.bat（Windows）
- run_export.command（macOS）
- source.md (範例)

