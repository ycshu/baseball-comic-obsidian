import json
import re
from pathlib import Path
from datetime import datetime
import sys

# 設定您的 Vault 路徑 (請根據實際情況修改，例如 "try" 或 "vault")
VAULT_DIR = Path("try")  
OUT_FILE = Path("index.json")

def die(msg):
    print(f"[ERROR] {msg}")
    input("按 Enter 鍵結束...")
    sys.exit(1)

def parse_yaml_value(value):
    """清理 YAML 的值，移除引號或括號"""
    value = value.strip()
    # 移除雙引號 (例如 "80" -> 80)
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    # 嘗試轉換數字
    if value.isdigit():
        return int(value)
    return value

def extract_wikilinks(text):
    """提取內文中的 [[連結]]，用於建立關聯圖譜"""
    return re.findall(r'\[\[(.*?)\]\]', text)

def parse_markdown(text):
    """
    解析 Markdown，分離 YAML Frontmatter 與 內文
    """
    # 1. 透過正則表達式分離 Frontmatter
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.search(pattern, text, re.DOTALL)
    
    meta = {}
    content = text.strip()
    
    if match:
        yaml_text = match.group(1)
        content = text[match.end():].strip() # 剩下的就是純內文
        
        # 2. 簡易解析 YAML (針對您的格式優化)
        current_key = None
        for line in yaml_text.split('\n'):
            line = line.rstrip()
            if not line: continue
            
            # 處理清單項目 (例如 tags 下面的 - 棒球漫畫)
            if line.strip().startswith("- ") and current_key:
                val = parse_yaml_value(line.strip()[2:])
                if not isinstance(meta[current_key], list):
                    meta[current_key] = []
                meta[current_key].append(val)
                
            # 處理鍵值對 (例如 作者: "[[滿田拓也]]")
            elif ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                
                if val: # 如果有值直接存
                    meta[key] = parse_yaml_value(val)
                    current_key = key # 記住這個 key，以防下一行是 list
                else: # 如果值是空的，可能是 list 的開始 (例如 tags:)
                    meta[key] = []
                    current_key = key

    # 3. 額外處理：從內文中提取所有的 [[連結]] 放到 metadata 方便查詢
    meta["related_links"] = extract_wikilinks(content)
    
    # 4. 額外處理：移除內文中的 WikiLink 括號，讓全文檢索更自然
    # 例如將 "[[張哲維]]" 轉為 "張哲維" (可選，視需求而定)
    clean_content = re.sub(r'\[\[(.*?)\]\]', r'\1', content)

    return meta, clean_content

def load_md_files(folder):
    """遞迴讀取資料夾下的所有 .md 檔案"""
    if not folder.exists():
        print(f"[WARN] 找不到路徑: {folder}，跳過")
        return []
        
    items = []
    # 使用 rglob 支援子目錄搜尋
    for p in folder.rglob("*.md"):
        try:
            raw_text = p.read_text(encoding="utf-8")
            meta, body = parse_markdown(raw_text)
            
            # 建立標準化的資料結構
            item = {
                "id": p.stem,                  # 檔案名稱當 ID
                "filename": p.name,
                "filepath": str(p),            # 原始路徑
                "modified_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
                "metadata": meta,              # 結構化資料 (作者, 定價, tags...)
                "content": body,               # 純文字內容
                "length": len(body)
            }
            items.append(item)
        except Exception as e:
            print(f"[ERROR] 讀取 {p.name} 失敗: {e}")

    return items

def main():
    if not VAULT_DIR.exists():
        die(f"找不到 {VAULT_DIR} 資料夾")

    print(f"正在掃描 {VAULT_DIR} ...")

    # 這裡將所有資料彙整成一個大的 List，適合丟入搜尋引擎或資料庫
    # 如果您希望保留資料夾分類，可以根據 filepath 欄位來篩選
    all_docs = load_md_files(VAULT_DIR)

    data = {
        "info": {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(all_docs),
            "description": "Obsidian Vault Export for Querying"
        },
        "documents": all_docs
    }

    print(f"正在寫入 {OUT_FILE} ...")
    OUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"✔ 成功匯出 {len(all_docs)} 筆資料至 {OUT_FILE}")
    # 顯示前幾筆資料的標題做為確認
    if len(all_docs) > 0:
        print("範例資料:", [d['id'] for d in all_docs[:3]])
    
    input("按 Enter 鍵結束...")

if __name__ == "__main__":
    main()