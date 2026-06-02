"""PIPE-SCAFFOLD 雙軌派發 scaffolding 測試（plan v3 §6 / tasks_v3 §6.2）。

覆蓋：
- 影子 B 軌派發單元 run_pipeline_shadow 的四重隔離（_shadow task_key + (測試) 標題、
  與 A 軌鍵不碰撞）。
- 旗標閘門：SHADOW_LAUNCH_ENABLED false → 單軌（僅 A 軌派發）；true → 雙軌（額外 B 軌）。
  以 confirm_type（派發點二）直接呼叫驗證 gating 決策。
- 派發點一（upload_paper）閘門結構存在；A 軌 run_pipeline 本體未被改寫（原始碼自檢）。

策略：直接呼叫 async endpoint / 影子單元（繞過 HTTP/auth/DB），以 Fake BackgroundTasks
記錄派發決策；不實跑 pipeline（add_task 僅記錄）。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import settings  # noqa: E402
import web_server  # noqa: E402

_SRC = (ROOT / "web_server.py").read_text(encoding="utf-8")
_OWNER = 777001  # 測試專用 owner 哨兵（避免污染真實 processing_tasks）


class _FakeBG:
    """記錄 add_task 派發決策（不實跑）。"""

    def __init__(self):
        self.calls = []

    def add_task(self, fn, *args, **kwargs):
        self.calls.append((getattr(fn, "__name__", str(fn)), args))


class _Req:
    def __init__(self, doc_type="academic"):
        self.doc_type = doc_type


class _User:
    def __init__(self, uid=_OWNER):
        self.id = uid


def _cleanup_keys(*keys):
    with web_server.tasks_lock:
        for k in keys:
            web_server.processing_tasks.pop(k, None)


# ── 影子 B 軌派發單元：四重隔離（U3）──

def test_run_pipeline_shadow_isolation(monkeypatch):
    paper_id = "pX"
    a_key = (_OWNER, paper_id)
    shadow_key = (_OWNER, f"{paper_id}_shadow")
    _cleanup_keys(a_key, shadow_key)

    # 讓 Orchestrator 不實跑（避免 NullStrategy 噪聲）；本測試只驗派發單元的隔離行為
    import pipelines

    class _NoopOrch:
        def run(self, ctx):
            return ctx

    monkeypatch.setattr(pipelines, "Orchestrator", _NoopOrch)

    asyncio.run(web_server.run_pipeline_shadow(_OWNER, paper_id, "/tmp/x.pdf", "academic", "x.pdf"))

    with web_server.tasks_lock:
        assert shadow_key in web_server.processing_tasks          # ① 獨立 task_key
        assert a_key not in web_server.processing_tasks            # 不碰撞 A 軌鍵
        title = web_server.processing_tasks[shadow_key]["_original_filename"]
        assert title.endswith(" (測試)")                          # ④ (測試) 標題後綴
    _cleanup_keys(a_key, shadow_key)


# ── 旗標閘門：派發點二（confirm_type）gating 決策（U1/U4）──

def _run_confirm(doc_type="academic"):
    bg = _FakeBG()
    task_key = (_OWNER, "pY")
    with web_server.tasks_lock:
        web_server.processing_tasks[task_key] = {
            "status": "waiting_confirm", "_pdf_path": "/tmp/x.pdf",
            "_original_filename": "x.pdf",
        }
    try:
        asyncio.run(web_server.confirm_type("pY", _Req(doc_type), bg, _User()))
    finally:
        _cleanup_keys(task_key, (_OWNER, "pY_shadow"))
    return bg


def test_dispatch_flag_false_single_track(monkeypatch):
    monkeypatch.setattr(settings, "SHADOW_LAUNCH_ENABLED", False)
    bg = _run_confirm()
    names = [c[0] for c in bg.calls]
    assert names == ["run_pipeline"]                  # 單軌：僅 A 軌


def test_dispatch_flag_true_dual_track(monkeypatch):
    monkeypatch.setattr(settings, "SHADOW_LAUNCH_ENABLED", True)
    bg = _run_confirm()
    names = [c[0] for c in bg.calls]
    assert names == ["run_pipeline", "run_pipeline_shadow"]   # 雙軌：A + B
    # 影子派發引數 paper_id 與 A 軌相同（由 run_pipeline_shadow 內部衍生 _shadow，不在此碰撞）
    assert bg.calls[1][1][1] == "pY"


# ── 原始碼自檢：派發點一閘門存在 + A 軌本體未改寫 ──

def test_dispatch_point_one_gate_present():
    assert "[PIPE-SCAFFOLD OP-1 START] 派發點一閘門" in _SRC
    assert "[PIPE-SCAFFOLD OP-2 START] 派發點二閘門" in _SRC


def test_a_track_run_pipeline_untouched():
    # A 軌 run_pipeline 本體與 PipelineCore 調用仍在
    assert "async def run_pipeline(" in _SRC
    assert "pipeline = PipelineCore(on_progress=on_progress)" in _SRC
    # 影子單元為獨立函式（附加式、非改 A 軌）
    assert "async def run_pipeline_shadow(" in _SRC
    assert "[PIPE-SCAFFOLD OP-1 START] 影子 B 軌派發單元" in _SRC
