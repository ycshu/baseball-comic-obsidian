import json
from pathlib import Path
from datetime import datetime
import sys

# 設定你的 Vault 資料夾名稱
# 如果此 script 放在 vault 資料夾裡面，請改成 Path(".")
# 如果此 script 放在 vault 資料夾外面 (上一層)，請保持 Path("vault")
VAULT_DIR = Path("vault") 
OUT_FILE = Path("index.json")

def die(msg):
    print(f"[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def load_md_files(folder):
    # 檢查資料夾是否存在，不存在就回傳空列表，避免報錯
    if not folder.exists():
        print(f"⚠️  警告：找不到資料夾 {folder}，將跳過。")
        return []
    
    items = []
    # 讀取該資料夾下所有的 .md 檔案
    for p in folder.glob("*.md"):
        try:
            items.append({
                "id": p.stem,    # 檔名作為 ID (不含副檔名)
                "title": p.stem, # 檔名作為標題
                "content": p.read_text(encoding="utf-8").strip() # 檔案內容
            })
        except Exception as e:
            print(f"❌ 讀取檔案 {p.name} 失敗: {e}")
            
    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到 {VAULT_DIR} 資料夾，請確認位置是否正確。")

    print(f"正在掃描資料夾: {VAULT_DIR.resolve()} ...")

    # --- 這裡是最主要的修改 ---
    # 左邊的 Key (如 "characters") 是 JSON 裡的欄位名稱
    # 右邊的 VAULT_DIR / "人物" 對應你圖片中實際的資料夾名稱
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "license_ok": True
        },
        # 對應圖片中的 'metadata' 資料夾
        "metadata": load_md_files(VAULT_DIR / "metadata"),
        
        # 對應圖片中的 '人物' 資料夾 (建議 JSON key 用英文，如 characters)
        "characters": load_md_files(VAULT_DIR / "人物"),
        
        # 對應圖片中的 '對戰' 資料夾
        "battles": load_md_files(VAULT_DIR / "對戰"),
        
        # 對應圖片中的 '日期' 資料夾
        "dates": load_md_files(VAULT_DIR / "日期"),
        
        # 對應圖片中的 '漫畫集數' 資料夾
        "episodes": load_md_files(VAULT_DIR / "漫畫集數")
    }

    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"✔ 成功產生 {OUT_FILE}，包含 {len(data)} 個分類。")
    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()