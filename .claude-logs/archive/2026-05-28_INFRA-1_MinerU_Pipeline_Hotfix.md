# INFRA-1 Hotfix — MinerU `hybrid_auto` 卡死 + `pipeline` backend 確認

> **任務類別**：`hotfix`
> **日期**：2026-05-28
> **影響範圍**：GCP mineru Docker container + mad-professor `pdf_processor.py`

---

## 阻斷性問題

| # | 現象 | 根本原因 |
|---|------|---------|
| 1 | `hybrid_auto` backend 卡在 `Predict: 0%`，永不回傳 | CPU 環境下 VLM 推理無法啟動，已知問題 |
| 2 | `MINERU_VIRTUAL_VRAM_SIZE=8` 造成 OOM 卡死 | batch_size=4 在 CPU 下吃爆記憶體 |
| 3 | `MINERU_VIRTUAL_VRAM_SIZE=4` 無加速效果 | `pipeline` backend 完全不看此變數，反而多跑無用邏輯 |

**診斷證據**：
```
# hybrid_auto 卡死 log
Predict:   0%|          | 0/18 [00:00<?, ?it/s]
# 之後完全靜止，無任何輸出

# pipeline 正常 log
Pipeline processing-window multi-file run. doc_count=1, total_pages=18
2,  3.51s/it
```

---

## 測試數據

| 測試條件 | 結果 |
|---------|------|
| `hybrid_auto`（預設） | ❌ 卡死，永不完成 |
| `pipeline` + `MINERU_VIRTUAL_VRAM_SIZE=4` | ✅ 1分39秒 |
| `pipeline`（移除環境變數） | ✅ **1分6秒**（最快）|

測試文件：NVIDIA 白皮書，18頁，1.2MB，純文字為主。

---

## 修復內容

### 1. GCP mineru Docker container

**`/home/baroncheng/mineru-cpu-deploy/docker-compose.yml`**

```diff
- environment:
-   - MINERU_DEVICE_MODE=cpu
-   - MINERU_VIRTUAL_VRAM_SIZE=8   # ← 移除，造成 OOM
+ environment:
+   - MINERU_DEVICE_MODE=cpu
```

已執行：
```bash
docker compose down && docker compose up -d
```

### 2. mad-professor `pdf_processor.py`（待執行）

呼叫 MinerU `/file_parse` 時加上 `backend=pipeline`：

```diff
- data = {"return_md": "true"}
+ data = {"return_md": "true", "backend": "pipeline"}
```

---

## 不可動清單

- `docker-compose.yml` 的 `cpus: "3.0"` 和 `memory: 10G` 限制 — 不動
- MinerU container 的 volume 掛載路徑 — 不動
- `mineru-net` 網路名稱 — 不動（mad-professor 之後要接同一個網路）

---

## E2E 驗證

```bash
# 驗證 pipeline backend 正常
time curl -s -o /tmp/verify.json \
  -X POST http://127.0.0.1:8000/file_parse \
  -F "files=@/tmp/test.pdf" \
  -F "return_md=true" \
  -F "backend=pipeline"

# 確認有內容
cat /tmp/verify.json | python3 -c \
  "import json,sys; d=json.load(sys.stdin); \
   [print(k, ':', len(str(v)), 'chars') for k,v in d.get('results',{}).items()]"

# 預期：test : 40000+ chars，time real < 2m
```

---

## Commit 格式

```
fix(infra): 移除 MINERU_VIRTUAL_VRAM_SIZE，改用 pipeline backend

- 移除 MINERU_VIRTUAL_VRAM_SIZE 環境變數（CPU 下無效，反而增加耗時 33 秒）
- hybrid_auto backend 在 CPU 環境下已知卡死（Predict 0% 永不進展）
- pipeline backend 為 CPU 環境正確選擇，18頁文件約 1分6秒
- pdf_processor.py 呼叫 MinerU 時加上 backend=pipeline 參數
```

---

## 背景說明

### hybrid_auto vs pipeline

| | hybrid_auto | pipeline |
|--|-------------|----------|
| 架構 | 新（3.x），單一 VLM 模型 | 舊，多專門模型（PaddleOCR + RapidTable） |
| GPU 需求 | 需要 | 不需要 |
| CPU 環境 | ❌ 已知卡死 | ✅ 穩定 |
| 速度（CPU） | N/A（卡死） | 18頁約 1分6秒 |

### batch_size 在 CPU 下無效

MinerU 的 `set_default_batch_size()` 邏輯設計給 GPU，CPU 環境下 `total_memory` 預設為 1GB → `batch_size=1`。即使透過 `MINERU_VIRTUAL_VRAM_SIZE` 強制提高，CPU 的 batch 機制仍是序列處理，記憶體反而增加，無實質加速。
