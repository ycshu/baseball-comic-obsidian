import json
from pathlib import Path
from datetime import datetime
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import sys

# 建議安裝 PyYAML 以精準解析 YAML：pip install PyYAML
# 如果不想安裝，這裡使用簡易的正規表達式解析
try:
    import yaml
except ImportError:
    yaml = None

# 設定你的 Obsidian 庫路徑 (根據你上傳的檔案結構，改為 Min)
VAULT_DIR = Path("Min")
OUT_FILE = Path("search_index.json")

def parse_md_file(p):
    """解析 Markdown 檔案，提取 Frontmatter 與內容"""
    text = p.read_text(encoding="utf-8").strip()
    
    # 預設資料結構
    data = {
        "id": p.stem,
        "filename": p.name,
        "metadata": {},
        "content": "",
        "tags": [],
        "links": []
    }

    # 1. 提取 YAML Frontmatter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if yaml_match:
        yaml_block = yaml_match.group(1)
        content_block = yaml_match.group(2)
        
        if yaml:
            data["metadata"] = yaml.safe_load(yaml_block)
        else:
            # 簡易解析：逐行抓取 key: value
            for line in yaml_block.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    data["metadata"][k.strip()] = v.strip()
        
        data["content"] = content_block.strip()
    else:
        data["content"] = text

    # 2. 提取標籤 (例如 #漫畫)
    tags = re.findall(r'#([^\s#]+)', data["content"])
    # 加上 YAML 裡的 tags (如果有的話)
    yaml_tags = data["metadata"].get("tags", [])
    if isinstance(yaml_tags, list):
        data["tags"] = list(set(tags + yaml_tags))
    
    # 3. 提取內部連結 [[Link]]
    links = re.findall(r'\[\[(.*?)\]\]', data["content"])
    data["links"] = links

    return data

def main():
    if not VAULT_DIR.exists():
        print(f"[ERROR] 找不到 {VAULT_DIR} 資料夾")
        return

    # 搜尋所有 .md 檔案
    all_files = list(VAULT_DIR.rglob("*.md"))
    database = []

    for p in all_files:
        # 跳過模板檔案 (例如：閱讀模板.md)
        if "模板" in p.name:
            continue
            
        try:
            doc_data = parse_md_file(p)
            database.append(doc_data)
        except Exception as e:
            print(f"解析 {p.name} 失敗: {e}")

    # 輸出成便於查詢的格式
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_count": len(database),
        "documents": database
    }

    OUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"✔ 成功產生 {OUT_FILE}，共處理 {len(database)} 份文件")

if __name__ == "__main__":
    main()


VAULT_DIR = Path("vault")
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
