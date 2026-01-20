import json
from pathlib import Path
from datetime import datetime
import sys

VAULT_DIR = Path("vault")
OUT_FILE = Path("index.json")

import json
import re
from pathlib import Path
from datetime import datetime
import sys

# 設定你的 Vault 路徑
VAULT_DIR = Path("vault")
OUT_FILE = Path("index.json")

def parse_frontmatter(content):
    """
    簡單解析 Markdown 檔案開頭的 YAML Frontmatter。
    回傳 (metadata_dict, content_body)
    """
    # 檢查是否以 --- 開頭
    if not content.startswith("---"):
        return {}, content

    # 嘗試分割 YAML 區塊與內文
    # split 參數設為 2，只切分前兩個 '---'
    parts = content.split("---", 2)
    
    # 確保格式正確 (開頭空字串, YAML內容, 內文)
    if len(parts) < 3:
        return {}, content

    yaml_text = parts[1].strip()
    body = parts[2].strip()
    
    metadata = {}
    
    # 簡易解析每一行 YAML (不依賴 PyYAML 函式庫以保持輕量)
    for line in yaml_text.split('\n'):
        line = line.strip()
        if not line or line.startswith("#"): 
            continue
        
        # 處理 "key: value"
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # 處理簡單的列表格式 (如 tags)
            if value.startswith("[") and value.endswith("]"):
                # 簡易處理，去除括號
                value = value[1:-1]
            
            # 移除字串引號
            value = value.strip('"').strip("'")
            
            # 處理布林值
            if value.lower() == 'true': value = True
            elif value.lower() == 'false': value = False
            
            metadata[key] = value

    return metadata, body

def extract_links(content):
    """
    使用正則表達式抓取所有的 [[WikiLink]]
    """
    # 抓取 [[連結]] 或 [[連結|顯示文字]]
    pattern = r"\[\[(.*?)(?:\|.*?)?\]\]"
    return re.findall(pattern, content)

def load_all_md_files(root_dir):
    """
    遞迴搜尋所有 .md 檔案並解析
    """
    if not root_dir.exists():
        return []
        
    items = []
    # rglob("*") 會搜尋所有子資料夾
    for p in root_dir.rglob("*.md"):
        raw_content = p.read_text(encoding="utf-8").strip()
        
        # 1. 解析 Metadata
        meta, body = parse_frontmatter(raw_content)
        
        # 2. 抓取連結 (用於建立關聯圖)
        links = extract_links(body)
        
        item = {
            "id": p.stem,              # 檔名作為 ID
            "path": str(p.relative_to(root_dir)), # 相對路徑
            "metadata": meta,          # YAML 資料
            "links": links,            # 連結到的其他筆記
            "content": body,           # 主要內文
            "modified_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        }
        items.append(item)
        
    return items

def main():
    if not VAULT_DIR.exists():
        print(f"[ERROR] 找不到 {VAULT_DIR} 資料夾。")
        input("按 Enter 鍵結束...")
        sys.exit(1)

    print(f"正在掃描 {VAULT_DIR} 下的所有筆記...")
    
    notes = load_all_md_files(VAULT_DIR)
    
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "total_files": len(notes),
            "description": "Obsidian Vault Export with Metadata"
        },
        "documents": notes
    }

    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"✔ 成功匯出 {len(notes)} 個檔案至 {OUT_FILE}")
    
    # 顯示前幾個檔案的標題供確認
    if len(notes) > 0:
        print("範例資料:")
        print(json.dumps(notes[0], ensure_ascii=False, indent=2))

    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
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
