import json
from pathlib import Path
from datetime import datetime
import sys

# 設定路徑
VAULT_DIR = Path("vault")
OUT_FILE = Path("index.json")

def die(msg):
    print(f"\n[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def load_md_files(folder):
    """讀取指定資料夾下的所有 Markdown 檔案"""
    if not folder.exists():
        print(f"[提示] 找不到資料夾：{folder.name}，已跳過。")
        return []
    
    items = []
    # 使用 rglob 可以抓到子資料夾內的 .md 檔
    for p in folder.rglob("*.md"):
        try:
            items.append({
                "id": p.stem,
                "title": p.stem,
                "category": folder.name, # 紀錄它屬於哪個分類
                "content": p.read_text(encoding="utf-8").strip()
            })
            print(f"  已讀取：{p.name}")
        except Exception as e:
            print(f"  [錯誤] 無法讀取 {p.name}: {e}")
            
    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到 '{VAULT_DIR}' 資料夾。請確認該資料夾與此程式放在同一個地方。")

    print(f"🚀 開始掃描資料夾：{VAULT_DIR.absolute()}")

    # 根據你的圖片，對應實際的資料夾名稱
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "description": "Obsidian Vault Export"
        },
        # 修改這裡的名稱以符合你的圖片
        "ai_homework": load_md_files(VAULT_DIR / "AI課程作業"),
        "class_practice": load_md_files(VAULT_DIR / "上課操作"),
        "mvp_players": load_md_files(VAULT_DIR / "我的MVP球員"),
        "others": load_md_files(VAULT_DIR / "l74146126") 
    }

    # 寫入 JSON 檔案
    try:
        OUT_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print("\n" + "="*30)
        print(f"✔ 成功產生 {OUT_FILE}")
        print(f"✔ 總共匯出 {len(data['ai_homework']) + len(data['class_practice']) + len(data['mvp_players'])} 個檔案")
        print("="*30)
    except Exception as e:
        die(f"寫入 JSON 時發生錯誤: {e}")

    input("\n按 Enter 鍵結束...")

if __name__ == "__main__":
    main()