"""Phase 4.7e-1 人工驗證 CLI：對 /tmp/phase_4_7e_samples/resume_samples/
6 份履歷各跑一次 ResumeProcessor、輸出寫 .claude-logs/_phase_4_7e_outputs/{paper}/。

用法：
    venv/bin/python tools/test_resume_vision.py

⚠ 實際打 LLM API（settings.LLM_VISION_MODEL）、需 GEMINI_API_KEY、會花錢。

每份印：
  - 處理耗時（評估 Vision call latency）
  - 結構強度檢核 warnings（缺主標題 / ### 數量 / 缺區段 / 過多 table）
  - 輸出前 200 字快速 sanity check

baron 審視重點（見 .claude-logs/_phase_4_7e_outputs/{paper}/{paper}.md）：
  - 主標題格式（# {職稱} Resume - {人名}）
  - Working Experience 內每家公司 ### 平行
  - FOCALTECH / NOVATEK 等 plain text 公司是否被補抽 ###（DeHunt）
  - Technical Skills 區段是否合理彙整
  - 多語履歷處理（黃忠偉 / Priyal_Shah）
  - 邊界 case（Priyal 雙語、黃忠偉自傳重複）
"""
import sys
import time
from pathlib import Path
from typing import List

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


def structure_check(md_content: str) -> List[str]:
    """簡單結構強度檢核、回傳 warnings list。"""
    warnings: List[str] = []

    if not md_content.startswith("#"):
        warnings.append("❌ 缺主標題（# 開頭）")

    h3_count = sum(
        1 for line in md_content.split("\n")
        if line.startswith("### ") and not line.startswith("#### ")
    )
    if h3_count == 0:
        warnings.append("⚠ 結構強度可能不足: ### 數量 = 0")
    elif h3_count < 2:
        warnings.append(f"⚠ ### 僅 {h3_count} 個、平行公司可能未被識別")

    if "## Working Experience" not in md_content:
        warnings.append("⚠ 缺 '## Working Experience' 區段")
    if "## Candidate Summary" not in md_content:
        warnings.append("⚠ 缺 '## Candidate Summary' 區段")
    if "## Technical Skills" not in md_content:
        warnings.append("⚠ 缺 '## Technical Skills' 區段")

    # 防 hallucination：偵測過多 markdown table（履歷不應有太多表格）
    table_count = md_content.count("| --- |") + md_content.count("|---|")
    if table_count > 2:
        warnings.append(
            f"⚠ Vision Hallucination 風險: 偵測 {table_count} 個 table、"
            f"可能將非表格內容誤呈現為 table"
        )

    return warnings


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

            warnings = structure_check(md_content)
            if warnings:
                for w in warnings:
                    print(f"   {w}")
            else:
                print("   ✓ 結構完整")

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
        # gemini-2.0-flash 估價 ~$0.001/call、Pro ~$0.005-0.01/call
        # 6 份 * 1 call ≈ $0.01-0.06；含多頁圖 token、保守估 $0.5-1
        print(f"估算 cost ≈ $0.5 - $1（6 份 vision call、模型依 LLM_VISION_MODEL）")
    print(f"輸出位於 {OUTPUTS_DIR}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
