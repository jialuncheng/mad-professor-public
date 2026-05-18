import sys
sys.path.insert(0, '/workspaces/Python/mad-professor-public')

from processor.md_restore_processor import RestoreProcessor
import json
from pathlib import Path

# 模擬 translated.json 的資料結構
test_data = {
    "title": "Test Paper",
    "translated_title": "測試論文",
    "authors_info": "Author: Test Author",
    "sections": [
        {
            "title": "Introduction",
            "translated_title": "緒論",
            "level": 1,
            "heading_level": 2,
            "content": [
                {
                    "type": "text",
                    "index": 0,
                    "content": "Line 1.\nLine 2.\nLine 3.",
                    "translated_content": "第一行。\n第二行。\n第三行。"
                }
            ],
            "children": []
        },
        {
            "title": "Results",
            "translated_title": "結果",
            "level": 1,
            "heading_level": 2,
            "content": [
                {
                    "type": "figure",
                    "index": 0,
                    "src": "images/test.jpg",
                    "alt": "",
                    "caption": "Fig. 1 Test figure with caption.",
                    "translated_caption": "圖 1 測試圖片說明。"
                },
                {
                    "type": "figure",
                    "index": 1,
                    "src": "images/test2.jpg",
                    "alt": "",
                    "caption": "",
                    "translated_caption": ""
                },
                {
                    "type": "table",
                    "index": 2,
                    "content": "| Col1 | Col2 |\n|------|------|\n| A    | B    |",
                    "caption": "Table 1 Test table.",
                    "translated_caption": "表 1 測試表格。"
                },
                {
                    "type": "table",
                    "index": 3,
                    "content": "",
                    "caption": "",
                    "translated_caption": ""
                },
                {
                    "type": "formula",
                    "index": 4,
                    "content": "$$E = mc^2$$"
                },
                {
                    "type": "formula",
                    "index": 5,
                    "content": ""
                }
            ],
            "children": []
        },
        {
            "title": "Supporting Information",
            "translated_title": "附錄資訊",
            "level": 1,
            "heading_level": 2,
            "content": [
                {
                    "type": "text",
                    "index": 0,
                    "content": "Fig. S1 Sample quality control.\nFig. S2 DEG analysis.\nFig. S3 RNA-seq datasets.",
                    "translated_content": "圖 S1 樣本品質控制。\n圖 S2 差異表達分析。\n圖 S3 RNA-seq 數據集。"
                }
            ],
            "children": []
        }
    ]
}

# 寫入測試 JSON
test_json = Path("/tmp/test_restore.json")
test_json.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

# 執行
processor = RestoreProcessor()
processor.process(
    str(test_json),
    "/tmp/test_restore_en.md",
    "/tmp/test_restore_zh.md"
)

# 檢查輸出
print("=== 英文版 ===")
print(Path("/tmp/test_restore_en.md").read_text())
print("\n=== 中文版 ===")
print(Path("/tmp/test_restore_zh.md").read_text())