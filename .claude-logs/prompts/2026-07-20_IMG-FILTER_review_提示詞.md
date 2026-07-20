# IMG-FILTER plan review 提示詞

- 日期：2026-07-20
- 來源：baron（轉發外部 review：代碼掃描核查 + 兩實作提醒 + 五 OQ 拍板）
- 階段：plan review（v1 → v2 定稿）

## 原文摘要

> review下面建議 / 如果沒問題 / update plan

review 內容：
1. **無結構性缺失**；門檻與邊界校正（廢長邊軸→面積 100k、規則③收窄判型行界）成功避開 481×369 chart 與 hero 圖誤殺。
2. **實作提醒 ×2**：DROP 路徑 caption 須 `used[cap_idx]=True` 標記（防孤兒圖說退化為 text block）；路徑解析用 `images_root / Path(src).name`（basename、相容相對路徑）。
3. **五 OQ 拍板**：Q1 stdlib header 解析〔PNG 前 24 bytes/JPEG SOF marker·SOS/EOI 終止〕/ Q2 設總開關預設 true / Q3 100k+4.0 廢長邊 / Q4 caption 一併不入 / Q5 獨立 `pipelines/image_filter.py`——全數採納推薦。

## 處置

兩實作提醒與現行代碼結構相符（split_blocks 既有 caption used[] 機制、MinerU src 相對路徑）→ 採納。plan 更新至 v2（§2.1 路徑解析 / §2.2 caption used 標記硬要求 / §9 五 OQ 拍板留痕 / §99.2 v2）。
