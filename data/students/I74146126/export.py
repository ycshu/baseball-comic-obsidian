import json
import re
from pathlib import Path
from datetime import datetime
import sys

# 設定路徑
VAULT_DIR = Path("vault")
OUT_FILE = Path("index.json")

def die(msg):
    print(f" \033[91m[ERROR]\033[0m {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def parse_md_content(content):
    """
    解析 Markdown 內容，分離 YAML Frontmatter 與真正的內文
    """
    # 匹配 YAML 前言的正規表示式 (--- 內容 ---)
    yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = yaml_pattern.match(content)
    
    frontmatter = {}
    body = content
    
    if match:
        # 這裡簡單處理 YAML (如果需要複雜處理，建議安裝 PyYAML)
        yaml_text = match.group(1)
        body = content[match.end():].strip()
        # 簡單的 Key: Value 解析
        for line in yaml_text.split('\n'):
            if ":" in line:
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip()
                
    return frontmatter, body

def load_md_files(folder_name):
    folder = VAULT_DIR / folder_name
    if not folder.exists():
        print(f" [WARN] 找不到資料夾: {folder_name}，跳過中...")
        return []
    
    items = []
    # 使用 rglob 支援子資料夾中的 .md 檔案
    for p in folder.rglob("*.md"):
        try:
            raw_text = p.read_text(encoding="utf-8").strip()
            metadata, content = parse_md_content(raw_text)
            
            items.append({
                "id": p.stem,
                "title": metadata.get("title", p.stem), # 優先使用 YAML 中的標題
                "category": folder_name,
                "path": str(p.relative_to(VAULT_DIR)),
                "last_modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                "metadata": metadata,
                "content": content
            })
            print(f"  - 已讀取: {p.name}")
        except Exception as e:
            print(f"  - [跳過] 讀取 {p.name} 時發生錯誤: {e}")
            
    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到 '{VAULT_DIR}' 資料夾，請確認它與此腳本放在同一個目錄下。")

    print(f"🚀 開始處理 Vault: {VAULT_DIR.absolute()}")

    # 定義你想抓取的子目錄
    target_folders = ["players", "events", "glossary"]
    data = {
        "meta": {
            "version": "1.1",
            "exported_at": datetime.now().isoformat(),
            "source": str(VAULT_DIR)
        }
    }

    # 動態抓取資料
    for folder in target_folders:
        print(f"🔎 正在掃描 {folder}...")
        data[folder] = load_md_files(folder)

    # 寫入 JSON
    try:
        OUT_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print("-" * 30)
        print(f"🎉 成功！檔案已產生於: {OUT_FILE.absolute()}")
    except Exception as e:
        die(f"寫入檔案失敗: {e}")

    input("\n按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
