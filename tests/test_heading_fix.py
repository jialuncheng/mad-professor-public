from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path('/workspaces/Python/mad-professor-public/.env'))

# test_heading_fix.py
import os
import sys
sys.path.insert(0, '/workspaces/Python/mad-professor-public')

from processor.pdf_processor import PDFProcessor
from pathlib import Path

# 模擬 MinerU 輸出的 Markdown（所有標題都是 ##）
test_md_content = """# Context matters: coordinated transcriptional regulation and root plasticity under multinutrient conditions

Author for correspondence: Chia-Yi Cheng

## Summary

Key words: Arabidopsis thaliana, nutrient stress.

## I. Introduction

As sessile organisms, plants must adapt.

## II. Materials and Methods

We curated 318 RNA-seq datasets.

## 1. RNA-seq data collection and processing

Reads were trimmed by BBDUK.

## 2. DEG analysis

A total of 307 samples were included.

## 3. Co-expression network construction

WGCNA was applied.

## III. Results

We identified a core set of 2050 genes.

## 1. Molecular version of Mulder's chart

Results part 1.

## 2. Co-expression analysis

Results part 2.

## IV. Discussion

Our findings highlight the modular system.

## Acknowledgements

We thank the NTU.

## References

Barberon et al., 2016.
"""

# 寫入暫存檔案
test_path = Path("/tmp/test_heading.md")
test_path.write_text(test_md_content, encoding="utf-8")

print("=== 修正前的標題 ===")
for i, line in enumerate(test_md_content.split("\n")):
    if line.startswith("#"):
        print(f"  行{i}: {line}")

# 執行修正
processor = PDFProcessor()
processor._fix_heading_levels(test_path)

# 讀取修正後結果
fixed_content = test_path.read_text(encoding="utf-8")
print("\n=== 修正後的標題 ===")
for i, line in enumerate(fixed_content.split("\n")):
    if line.startswith("#"):
        print(f"  行{i}: {line}")