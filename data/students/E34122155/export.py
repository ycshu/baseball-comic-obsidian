import json
from pathlib import Path
from datetime import datetime
import sys

VAULT_DIR = Path("Baseball")
OUT_FILE = Path("index.json")

def die(msg):
    print(f"[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def load_md_files(folder):
    if not folder.exists():
        return []
    items = []
    for p in folder.glob("*.md"):
        items.append({
            "id": p.stem,
            "title": p.stem,
            "content": p.read_text(encoding="utf-8").strip()
        })
    return items

def main():
    if not VAULT_DIR.exists():
        die("找不到 Baseball/ 資料夾，請確認你已把 Obsidian Baseball 放在正確位置")

    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "license_ok": True
        },
        "模板": load_md_files(VAULT_DIR / "模板"),
        "人物": load_md_files(VAULT_DIR / "人物"),
        "資訊": load_md_files(VAULT_DIR / "資訊"),
        "插入圖片": load_md_files(VAULT_DIR / "插入圖片"),
        "棒球大聯盟閱讀心得": load_md_files(VAULT_DIR / "棒球大聯盟閱讀心得"),
        "每日筆記": load_md_files(VAULT_DIR / "每日筆記"),
        "附件": load_md_files(VAULT_DIR / "附件"),
    }

    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("✔ 成功產生 index.json")
    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
