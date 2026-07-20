"""連字壞字修復純函式（PDF 字型層 ToUnicode 映射共病）。

PIPE-INGEST-FITZ C2：部分 PDF 字型的 ToUnicode 表把連字字形（ﬁ/ﬂ/ﬀ/ﬃ/ﬄ）
映到錯誤碼位（常見為 `1` / `;`），任何抽取法（本地直抽或外部解析服務）
產出的文字都會出現 `Pro1les` / `;rst` / `de1ning` 類壞字——與工具無關、
須在文字層獨立正規化。

設計（保守·誤殺比漏修貴）：
- **窗口**：僅處理「小寫字母 × 異常字元 × 小寫字母」與「詞首異常字元 ×
  小寫字母」兩形態；候選連字 `fi/fl/ff/ffi/ffl`。
- **第一閘（替換前排查）**：詞為數字縮寫（`1st`/`2nd`/`3s` 等）或版本號
  （`v1`/`v1.2`）者一律不碰。
- **第二閘（替換後詞形檢查）**：替換結果必須是有效英文單字——優先用系統
  字典 `/usr/share/dict/words`（存在才用、lazy 一次快取）、並以內建常見
  連字字彙集兜底（零第三方依賴）；不確定即保留原樣（fail-open）。
- **行數不變式**：純行內替換、嚴禁增刪行——下游行索引基準（判型 sidecar）
  不受汙染。
"""
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# 候選連字（壞映射的原字形；逐一嘗試、以第二閘裁決）
_CANDIDATES = ("fi", "fl", "ff", "ffi", "ffl")

# 窗口：小寫×異常字元×小寫、或詞首異常字元×小寫（如 `;rst`）
_WINDOW_RE = re.compile(r"(?:(?<=[a-z])[1;](?=[a-z])|^[1;](?=[a-z]))")

# 第一閘：數字縮寫 / 版本號一律不碰
_SKIP_RE = re.compile(r"^\d+(?:st|nd|rd|th|s)?$|^[vV]\d+(?:\.\d+)*$")

# 詞頭/詞尾包覆符（僅為 skip 檢查與詞形驗證剝殼；輸出原樣保留）
_LEAD_RE = re.compile(r"^[\(\[\{\"'`]*")
_TRAIL_RE = re.compile(r"[\)\]\}\"'`\.,:!\?]+$")

# 第二閘兜底：常見連字字彙集（系統字典缺席時仍可正修高頻壞字）
_FALLBACK_WORDS = frozenset({
    "affect", "afford", "artificial", "benefit", "benefits", "certificate",
    "classification", "coefficient", "configuration", "confirm", "conflict",
    "defined", "defining", "definition", "difference", "differences",
    "different", "difficult", "effect", "effects", "efficiency", "efficient",
    "effort", "efforts", "field", "fields", "figure", "figures", "file",
    "files", "final", "finally", "financial", "find", "finding", "findings",
    "fine", "finish", "firm", "firms", "first", "fit", "five", "fix",
    "flexible", "floor", "flow", "flows", "fly", "identified", "identify",
    "influence", "notification", "off", "offer", "offers", "office",
    "officer", "official", "profile", "profiles", "profit", "profits",
    "qualified", "significant", "significantly", "specific", "specifically",
    "specified", "verified", "workflow", "workflows",
})

_SYSTEM_DICT_PATH = Path("/usr/share/dict/words")
_word_cache: Optional[frozenset] = None


def _word_set() -> frozenset:
    """詞形檢查字集：系統字典優先（存在才讀、lazy 一次快取）＋內建兜底。"""
    global _word_cache
    if _word_cache is None:
        words = set(_FALLBACK_WORDS)
        try:
            if _SYSTEM_DICT_PATH.exists():
                words.update(
                    w.strip().lower()
                    for w in _SYSTEM_DICT_PATH.read_text(
                        encoding="utf-8", errors="ignore"
                    ).splitlines()
                    if w.strip()
                )
        except Exception as exc:  # noqa: BLE001 — 字典讀取失敗降級走兜底集
            logger.warning(
                "[ligature_repair] 系統字典讀取失敗（降級內建兜底集）: %s",
                exc, exc_info=True,
            )
        _word_cache = frozenset(words)
    return _word_cache


def _is_valid_word(word: str) -> bool:
    if not word or not word.isalpha():
        return False
    lowered = word.lower()
    words = _word_set()
    if lowered in words:
        return True
    # 輕量詞形放寬：複數 s 退單數再查（字典多收原形）
    return lowered.endswith("s") and lowered[:-1] in words


def _try_repair(core: str, depth: int = 0) -> Optional[str]:
    """遞迴逐窗口嘗試候選連字；全部窗口修畢且為有效詞才採信。"""
    if depth > 3:
        return None
    m = _WINDOW_RE.search(core)
    if m is None:
        return core if _is_valid_word(core) else None
    for lig in _CANDIDATES:
        candidate = core[: m.start()] + lig + core[m.end():]
        repaired = _try_repair(candidate, depth + 1)
        if repaired is not None:
            return repaired
    return None


def _repair_token(token: str) -> str:
    if _WINDOW_RE.search(token) is None:
        return token
    lead = _LEAD_RE.match(token).group(0)
    rest = token[len(lead):]
    trail_m = _TRAIL_RE.search(rest)
    trail = trail_m.group(0) if trail_m else ""
    core = rest[: len(rest) - len(trail)] if trail else rest
    if not core or _SKIP_RE.match(core):  # 第一閘：數字縮寫/版本號不碰
        return token
    if _WINDOW_RE.search(core) is None:
        return token
    repaired = _try_repair(core)  # 候選替換 + 第二閘詞形檢查
    if repaired is None:
        return token  # 不確定保留原樣（fail-open）
    return f"{lead}{repaired}{trail}"


def _repair_line(line: str) -> str:
    return re.sub(r"\S+", lambda m: _repair_token(m.group(0)), line)


def repair_ligatures(text: str) -> str:
    """修復連字壞字（純函式、行內替換、**行數不變式**）。

    僅在雙閘皆過時替換；非 ASCII（如中文）行天然無窗口、原樣通過。
    """
    return "\n".join(_repair_line(line) for line in text.split("\n"))
