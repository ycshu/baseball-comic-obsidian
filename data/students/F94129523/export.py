import json
from pathlib import Path
from datetime import datetime
import sys

# ================= 設定區 =================
# 設定你的 Vault 資料夾名稱
# 如果此 script 放在 vault 資料夾裡面 (跟 .obsidian 同層)，請改成 Path(".")
# 如果此 script 放在 vault 資料夾外面 (上一層)，請保持 Path("vault") 或改成你的資料夾名稱
VAULT_DIR = Path("vault") 
OUT_FILE = Path("index.json")
# =========================================

def die(msg):
    print(f"[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def load_md_files(folder):
    # 檢查資料夾是否存在
    if not folder.exists():
        print(f"⚠️  警告：找不到資料夾 {folder}，將跳過。")
        return []
    
    items = []
    # 讀取該資料夾下所有的 .md 檔案
    # 如果你也想讀取子資料夾內的檔案，可以改成 folder.rglob("*.md")
    for p in folder.glob("*.md"):
        try:
            items.append({
                "id": p.stem,    # 檔名作為 ID
                "title": p.stem, # 檔名作為標題
                "content": p.read_text(encoding="utf-8").strip() # 檔案內容
            })
        except Exception as e:
            print(f"❌ 讀取檔案 {p.name} 失敗: {e}")
            
    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到 '{VAULT_DIR}' 資料夾，請確認程式碼最上方的 VAULT_DIR 設定是否正確。")

    print(f"正在掃描資料夾: {VAULT_DIR.resolve()} ...")

    # --- 修改重點：根據圖片中的資料夾名稱對應 ---
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "license_ok": True
        },
        
        # 對應圖片中的 'MVP球員作業' 資料夾
        # JSON key 命名為 'mvp_assignments' (可自行修改)
        "mvp_assignments": load_md_files(VAULT_DIR / "MVP球員作業"),
        
        # 對應圖片中的 '閱讀心得作業' 資料夾
        # JSON key 命名為 'reading_reflections'
        "reading_reflections": load_md_files(VAULT_DIR / "閱讀心得作業"),
        
        # 對應圖片中的 'template' 資料夾 (如果有需要讀取模板的話)
        "templates": load_md_files(VAULT_DIR / "template"),

        # 圖片中的 'Photos' 通常是放圖檔，
        # 如果裡面也有筆記(.md)想讀取，可以取消下面這行的註解：
        # "photos": load_md_files(VAULT_DIR / "Photos"),
    }

    # 寫入 JSON
    try:
        OUT_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        # 計算總檔案數
        total_files = sum(len(v) for k, v in data.items() if isinstance(v, list))
        print(f"✔ 成功產生 {OUT_FILE}，包含 {len(data)-1} 個分類，共 {total_files} 個檔案。")
    except Exception as e:
        die(f"寫入 JSON 失敗: {e}")

    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()