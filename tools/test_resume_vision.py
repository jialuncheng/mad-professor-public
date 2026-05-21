"""Phase 4.7e v2 人工驗證 CLI：對 /tmp/phase_4_7e_samples/resume_samples/
6 份履歷各跑一次 ResumeProcessor、輸出寫 .claude-logs/_phase_4_7e_outputs/{paper}/。

用法：
    venv/bin/python tools/test_resume_vision.py

⚠ 實際打 LLM API（settings.LLM_VISION_MODEL）、需 GEMINI_API_KEY、會花錢。

v2 vs 舊 7e-1：
- structure_check 移除「強制 Candidate Summary / Working Experience / Technical Skills」
  warnings（履歷各種變體都合法）
- 新增主標題黑名單檢查（對齊既有設計手冊 §3.1 / §4.5）
- table 容忍度放寬到 5（履歷常用 table 列學歷）
- print 加 section 統計（# / ## / ### counts）

baron 審視重點（見 .claude-logs/_phase_4_7e_outputs/{paper}/{paper}.md）：
  - 主標題必須是人名（不是「Resume」/「CV」/「CTO Resume - X」重組格式）
  - 中文 section 名（個人資料 / 學歷 / 工作經驗）原樣保留
  - table 結構保留不拆
  - DeHunt FOCALTECH / NOVATEK plain text 公司是否被補抽成 ###
  - 江元杰 plain text 公司（河洛 / 大昌瑞台）是否被補抽
"""
import sys
import time
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.resume_processor import ResumeProcessor  # noqa: E402

SAMPLES_DIR = Path("/tmp/phase_4_7e_samples/resume_samples")
OUTPUTS_DIR = ROOT / ".claude-logs" / "_phase_4_7e_outputs"

SAMPLES = [
    "CV_Chinyu_Lin_2308",
    "DeHunt_CTO_Tzung-Yuan_Lee",
    "YuLun_Wu_CV",
    "Priyal_Shah_CV",
    "江元杰",
    "黃忠偉",
]

# 主標題黑名單（對齊 processor/resume_processor.py 與既有設計手冊 §3.1 / §4.5）
RESUME_TITLE_BLACKLIST = frozenset({
    'resume', 'cv', 'curriculum vitae',
    '履歷', '個人簡歷', '履歷表',
})

RESUME_TITLE_SUSPICIOUS_PATTERNS = (
    ' resume -', ' resume:', ' cv -', ' cv:',
    '履歷 -', '履歷:', 'curriculum vitae',
)


def structure_check(md_content: str) -> Tuple[List[str], int, int, int]:
    """v2 鬆綁 + 黑名單檢查。回傳 (warnings, h1_count, h2_count, h3_count)。

    舊版「缺 ## Candidate Summary / Working Experience / Technical Skills」warnings
    全部移除——履歷可能用中文 section / freelance 結構 / 學生履歷各種變體都合法。

    新加：
    - 主標題黑名單檢查（對齊既有設計手冊 §3.1 / §4.5）
    - 主標題 suspicious pattern 檢查（如 'CTO Resume - X' 重組格式）
    - table 容忍度 → 5（履歷常用 table 列學歷）
    """
    warnings: List[str] = []

    h1_count = sum(1 for ln in md_content.split("\n") if ln.startswith("# ") and not ln.startswith("## "))
    h2_count = sum(1 for ln in md_content.split("\n") if ln.startswith("## ") and not ln.startswith("### "))
    h3_count = sum(1 for ln in md_content.split("\n") if ln.startswith("### ") and not ln.startswith("#### "))

    if not md_content.startswith("#"):
        warnings.append("❌ 缺主標題（# 開頭）")
        return warnings, h1_count, h2_count, h3_count

    # 主標題黑名單檢查
    first_line = md_content.split("\n", 1)[0]
    title_text = first_line.lstrip("#").strip().casefold()

    if title_text in RESUME_TITLE_BLACKLIST:
        warnings.append(
            f"❌ 主標題是黑名單通用詞 {title_text!r}、應為人名: {first_line}"
        )

    for pattern in RESUME_TITLE_SUSPICIOUS_PATTERNS:
        if pattern in title_text:
            warnings.append(
                f"⚠ 主標題含重組 pattern {pattern!r}、可能違反「忠實轉錄」: {first_line}"
            )
            break

    # ### 數量檢查
    if h3_count == 0:
        warnings.append(
            "⚠ ### 數量 = 0（履歷無公司平行條目、可能是學生 CV / freelance / 結構奇特）"
        )

    # 防 hallucination：偵測過多 markdown table（履歷常用 table 列學歷、放寬到 5）
    table_count = md_content.count("| --- |") + md_content.count("|---|")
    if table_count > 5:
        warnings.append(
            f"⚠ markdown table 數量 {table_count} 超過 5、請人工確認是否合理"
        )

    return warnings, h1_count, h2_count, h3_count


def main() -> int:
    if not SAMPLES_DIR.exists():
        print(f"❌ 樣本目錄不存在：{SAMPLES_DIR}")
        print("   請先解壓：")
        print("   mkdir -p /tmp/phase_4_7e_samples && cd /tmp/phase_4_7e_samples && \\")
        print(f"     tar -xzf {ROOT}/.claude-logs/resume_samples.tgz")
        return 1

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    proc = ResumeProcessor()

    print(f"處理 {len(SAMPLES)} 份履歷、輸出到 {OUTPUTS_DIR}/\n")

    ok, fail = 0, 0
    times: List[float] = []
    for name in SAMPLES:
        pdf = SAMPLES_DIR / name / f"{name}.pdf"
        if not pdf.exists():
            print(f"❌ {name}: 找不到 {pdf}\n")
            fail += 1
            continue

        out_dir = OUTPUTS_DIR / name
        try:
            print(f"🔵 {name} 處理中...", flush=True)
            t0 = time.time()
            md_path = proc.process(str(pdf), str(out_dir))
            elapsed = time.time() - t0
            times.append(elapsed)

            md_content = md_path.read_text(encoding="utf-8")
            print(f"✅ {name}: {len(md_content)} chars、耗時 {elapsed:.1f}s")

            warnings, h1, h2, h3 = structure_check(md_content)
            print(f"   ✓ 結構：# ({h1}) + ## ({h2}) + ### ({h3})")
            if warnings:
                for w in warnings:
                    print(f"   {w}")
            else:
                print("   ✓ 無 warnings")

            print("   📝 前 200 字:")
            for line in md_content[:200].splitlines():
                print(f"     {line}")
            print()
            ok += 1
        except Exception as e:
            print(f"❌ {name}: {type(e).__name__}: {e}\n")
            fail += 1

    print(f"=== 完成 ok={ok} fail={fail} ===")
    if times:
        avg = sum(times) / len(times)
        print(f"平均耗時 {avg:.1f}s（min {min(times):.1f}s / max {max(times):.1f}s）")
        print(f"估算 cost ≈ $0.5 - $1（6 份 vision call、模型依 LLM_VISION_MODEL）")
    print(f"輸出位於 {OUTPUTS_DIR}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
