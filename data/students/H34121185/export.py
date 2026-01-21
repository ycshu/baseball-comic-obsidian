import json
from pathlib import Path
from datetime import datetime
import sys
import re

# 修改後的路徑：指向你的實際資料夾
VAULT_DIR = Path("Vault/棒球大聯盟2")
OUT_FILE = Path("index.json")

def die(msg):
    print(f"[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def parse_md_file(file_path):
    """
    解析 Markdown 檔案，提取 YAML 屬性與內文
    """
    content = file_path.read_text(encoding="utf-8").strip()
    
    # 建立基礎資料結構
    item = {
        "id": file_path.stem,
        "title": file_path.stem,
        "properties": {},
        "body": ""
    }

    # 使用正規表達式抓取 Obsidian 的屬性區塊 (--- 之間的內容)
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    
    if frontmatter_match:
        yaml_block = frontmatter_match.group(1)
        body_content = frontmatter_match.group(2)
        
        # 簡易解析 YAML 屬性 (處理 "屬性: 值" 格式)
        for line in yaml_block.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                item["properties"][key.strip()] = val.strip()
        
        item["body"] = body_content.strip()
    else:
        # 如果沒有屬性區塊，則整篇都是內文
        item["body"] = content

    return item

def load_from_folder(folder_name):
    folder_path = VAULT_DIR / folder_name
    if not folder_path.exists():
        print(f"[警告] 找不到資料夾: {folder_name}")
        return []
    
    items = []
    for p in folder_path.glob("*.md"):
        # 排除模板檔案本身（如果名稱包含「模板」）
        if "模板" in p.stem:
            continue
        items.append(parse_md_file(p))
    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到路徑 {VAULT_DIR}，請確認執行檔與 Vault 資料夾放在一起")

    print("正在處理資料...")

    # 根據你的資料夾結構進行抓取
    data = {
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "source": "棒球大聯盟2"
        },
        "characters": load_from_folder("人物"),          # 對應「人物」資料夾
        "reading_notes": load_from_folder("閱讀筆記"),    # 對應「閱讀筆記」資料夾
        "environment": load_from_folder("環境"),          # 對應「環境」資料夾
        "book_info": load_from_folder("書籍資訊")         # 對應「書籍資訊」資料夾
    }

    # 輸出成 JSON
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✔ 成功產生 {OUT_FILE}")
    print(f"共抓取: {len(data['characters'])} 個角色, {len(data['reading_notes'])} 篇筆記")
    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()