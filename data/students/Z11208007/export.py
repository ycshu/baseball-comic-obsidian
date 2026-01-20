import json
from pathlib import Path
from datetime import datetime
import sys

VAULT_DIR = Path("棒球")
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
        die("找不到 vault/ 資料夾，請確認你已把 Obsidian vault 放在正確位置")

    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "license_ok": True
        },
        "players": load_md_files(VAULT_DIR / "players"),
        "events": load_md_files(VAULT_DIR / "events"),
        "glossary": load_md_files(VAULT_DIR / "glossary")
    }

    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("✔ 成功產生 index.json")
    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
