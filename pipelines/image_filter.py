# === [IMG-FILTER C1] ===
"""確定性垃圾圖過濾器（IMG-FILTER）。

文字攝入家族之站台 chrome（logo／masthead／社群鈕／互動列）幾何過濾——三規則任一命中
即 DROP、互為保險（plan v2 §2.1）：
  ① 面積：`w*h < IMG_FILTER_MIN_AREA`（實測校正 100k、廢 spec 長邊軸）
  ② 長寬比：`max(w/h, h/w) > IMG_FILTER_MAX_ASPECT`（實測 4.0）
  ③ 報頭區位置：`src ∈ header_srcs`（呼叫端依前段結構判型行界預掃注入）

設計紀律：
- **零 LLM／零 Vision**（design spec F7 實證：Vision 描述判垃圾必漏）；**零第三方影像依賴**
  （尺寸讀取＝stdlib 二進位 header 解析、PNG＋JPEG 覆蓋 MinerU 實產）。
- **零文體字面量**、route-specific（`header_srcs`／`images_root`）由呼叫端注入；
  IO 全封裝於本模組閉包內（ingestion_engine 保持零 IO）。
- **fail-open**：圖檔缺失／格式無法解析／尺寸異常 → KEEP（寧留勿誤刪）。
- **審計不靜默**：每張 DROP `logger.info`（src＋實測尺寸＋命中規則）。
"""

from __future__ import annotations

import logging
import struct
from pathlib import Path
from typing import Callable, Iterable, Optional, Tuple

import settings

logger = logging.getLogger(__name__)

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
# JPEG SOF markers（含尺寸之 frame header）；跳過 C4（DHT）/C8（JPG 保留）/CC（DAC）。
_JPEG_SOF_MARKERS = frozenset(
    {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
)


def _read_image_size(path: Path) -> Optional[Tuple[int, int]]:
    """stdlib 二進位 header 解析 PNG／JPEG 尺寸，回 (w, h)；不支援格式回 None。

    - PNG：簽名 8 bytes＋IHDR 前段——僅讀前 24 bytes 即得寬高。
    - JPEG：自 SOI 起掃 marker 段、命中 SOF 段讀寬高；遇 SOS（0xDA、壓縮資料起點）或
      EOI（0xD9）即終止——防止對大檔做無效全檔遍歷。
    檔案缺失／IO 異常由呼叫端捕捉（fail-open）。
    """
    with path.open("rb") as f:
        head = f.read(24)
        if head[:8] == _PNG_SIGNATURE and len(head) >= 24:
            w, h = struct.unpack(">II", head[16:24])
            return int(w), int(h)
        if head[:2] != b"\xff\xd8":
            return None  # 非 PNG 非 JPEG
        # JPEG marker 掃描（從 SOI 之後、以 seek 跳段、不整檔載入）
        f.seek(2)
        while True:
            byte = f.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            # 吃掉 padding 0xFF
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if not marker:
                return None
            m = marker[0]
            if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7:
                continue  # 無長度段（SOI/TEM/RSTn）
            if m in (0xD9, 0xDA):
                return None  # EOI / SOS：終止、未見 SOF
            seg_len_bytes = f.read(2)
            if len(seg_len_bytes) < 2:
                return None
            seg_len = struct.unpack(">H", seg_len_bytes)[0]
            if m in _JPEG_SOF_MARKERS:
                body = f.read(5)
                if len(body) < 5:
                    return None
                h, w = struct.unpack(">HH", body[1:5])
                return int(w), int(h)
            f.seek(seg_len - 2, 1)  # 跳過本段其餘 payload


def make_figure_filter(
    images_root,
    header_srcs: Optional[Iterable[str]] = None,
    *,
    min_area: Optional[int] = None,
    max_aspect: Optional[float] = None,
    enabled: Optional[bool] = None,
) -> Optional[Callable[[str, str], bool]]:
    """三規則過濾器工廠，回 `filter(src, alt) -> bool`（True＝KEEP／False＝DROP）。

    - `enabled` 缺省讀 `settings.IMG_FILTER_ENABLED`；False → 回 **None**（呼叫端不注入、
      行為零變＝圖片全保留）。
    - `header_srcs`：報頭區圖片 src 集合（規則③；呼叫端依判型行界預掃、src 與 markdown
      原文字串同基準零轉換——plan v2 §4 接縫契約）。
    - 實檔定位＝`images_root / Path(src).name`（basename 解析、相容 `images/<hash>.jpg`
      相對路徑；2026-07-20 review 硬要求）。
    """
    if enabled is None:
        enabled = settings.IMG_FILTER_ENABLED
    if not enabled:
        return None
    area_floor = min_area if min_area is not None else settings.IMG_FILTER_MIN_AREA
    aspect_cap = max_aspect if max_aspect is not None else settings.IMG_FILTER_MAX_ASPECT
    header_set = set(header_srcs or ())
    root = Path(images_root)

    def _filter(src: str, alt: str = "") -> bool:
        # 規則③：報頭區位置（判型行界內預掃命中）
        if src in header_set:
            logger.info("[img-filter] DROP 規則③報頭區 src=%s", src)
            return False
        path = root / Path(src).name
        try:
            size = _read_image_size(path)
        except Exception as exc:  # noqa: BLE001 — 缺檔/IO 異常一律 fail-open KEEP
            logger.warning(
                "[img-filter] 尺寸讀取異常（fail-open KEEP）src=%s: %s",
                src, exc, exc_info=True,
            )
            return True
        if size is None:
            logger.warning(
                "[img-filter] 格式無法解析（fail-open KEEP）src=%s path=%s", src, path
            )
            return True
        w, h = size
        if w <= 0 or h <= 0:
            logger.warning(
                "[img-filter] 尺寸非正（fail-open KEEP）src=%s size=%dx%d", src, w, h
            )
            return True
        area = w * h
        aspect = max(w / h, h / w)
        # 規則①：面積
        if area < area_floor:
            logger.info(
                "[img-filter] DROP 規則①面積 src=%s size=%dx%d area=%d < %d",
                src, w, h, area, area_floor,
            )
            return False
        # 規則②：長寬比
        if aspect > aspect_cap:
            logger.info(
                "[img-filter] DROP 規則②長寬比 src=%s size=%dx%d aspect=%.2f > %.1f",
                src, w, h, aspect, aspect_cap,
            )
            return False
        return True

    return _filter
# === [IMG-FILTER C1 END] ===
