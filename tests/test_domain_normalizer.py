"""DOMAIN-NORM C4: DomainNormalizer 對齊器單元測試。

依據:
- plan v2 §6.1（四測試）+ tasks §8 C4
- 對齊 tests/test_paper_chunks_schema.py 的 file-based SQLite + FK ON fixture pattern

四測試：
1. test_domain_normalization_content_based — 內容判定（投放/社群→HF、Python/LLM→QA）
2. test_domain_dynamic_registration       — 冷門領域動態註冊 Domains，且**不塞單字**
3. test_domain_mapping_cache_hit          — 第二次查詢命中 DomainMapping、0 次 LLM API
4. test_feature_flag_off_preserves_raw    — 旗標 off 走舊行為（原樣回傳、不查 DB/不呼 LLM）

LLM 一律以 mock 注入（不實打 API）；DB 用 file-based 臨時 SQLite（FK ON）隔離、不污染正式庫。
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import Base, Domains, DomainMapping  # noqa: E402
import processor.domain_normalizer as dn  # noqa: E402
from processor.domain_normalizer import DomainNormalizer, DEFAULT_LCC  # noqa: E402


# ─────────────────── fixtures ───────────────────


@pytest.fixture
def session_factory():
    """每測試一個獨立 file-based SQLite + FK ON、回 sessionmaker。

    file-based（非 in-memory）：對齊 test_paper_chunks_schema.py，支援跨 connection
    共享同一 DB（normalize 內多次開 session 需可見彼此寫入）。
    """
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON")
        finally:
            cur.close()

    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, class_=Session
    )
    yield TestSession
    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


class _MockLLM:
    """可程式化回傳的 mock LLM；記錄 chat 呼叫次數以驗證快取命中。"""

    def __init__(self, response: str):
        self.response = response
        self.calls = 0
        self.last_temperature = None

    def chat(self, messages, temperature=0.5, stream=True, model=None):
        self.calls += 1
        self.last_temperature = temperature
        return self.response


# ─────────────────── 測試 ───────────────────


def test_domain_normalization_content_based(session_factory):
    """① 內容判定：依實質技能領域收斂 LCC（投放/社群→HF、Python/LLM→QA）。"""
    # 行銷/社群履歷 → HF（Commerce）；raw 短句相異以避免快取鍵碰撞
    llm_hf = _MockLLM("HF|Commerce")
    norm_hf = DomainNormalizer(llm=llm_hf, session_factory=session_factory)
    lcc_hf = norm_hf.normalize("行銷企劃履歷", context_text="廣告投放、社群經營、品牌行銷")
    assert lcc_hf == "HF"
    # 確認分類任務以 temperature=0.0 呼叫（確定性）
    assert llm_hf.last_temperature == 0.0

    # 軟體工程/AI 履歷 → QA（Mathematics/CS）
    llm_qa = _MockLLM("QA|Mathematics & Computer Science")
    norm_qa = DomainNormalizer(llm=llm_qa, session_factory=session_factory)
    lcc_qa = norm_qa.normalize("軟體工程師履歷", context_text="Python、LLM、機器學習")
    assert lcc_qa == "QA"


def test_domain_dynamic_registration(session_factory):
    """② 冷門領域動態註冊 Domains，且僅存領域空間（lcc+name）、**不塞單字**。"""
    llm = _MockLLM("QE|Geology & Paleontology")
    norm = DomainNormalizer(llm=llm, session_factory=session_factory)
    lcc = norm.normalize("古生物學 - 侏羅紀化石與恐龍演化", context_text="化石 地層 演化")
    assert lcc == "QE"

    with session_factory() as s:
        domains = s.query(Domains).all()
        mappings = s.query(DomainMapping).all()

    # Domains 僅新增一筆領域空間（lcc_code + name），無任何單字 row
    assert len(domains) == 1
    assert domains[0].lcc_code == "QE"
    assert domains[0].name == "Geology & Paleontology"
    # Domains 模型只有 lcc_code/name/created_at 三欄，物理上不可能塞單字（與 GLOSSARY-CORE 隔離）
    assert {c.name for c in Domains.__table__.columns} == {"lcc_code", "name", "created_at"}
    # DomainMapping 快取一筆 raw→lcc
    assert len(mappings) == 1
    assert mappings[0].lcc_code == "QE"


def test_domain_mapping_cache_hit(session_factory):
    """③ 第二次相同 raw 查詢命中 DomainMapping 快取、0 次額外 LLM API。"""
    llm = _MockLLM("QA|Mathematics")
    norm = DomainNormalizer(llm=llm, session_factory=session_factory)

    raw = "應用數學 - 拓樸學"
    first = norm.normalize(raw)
    assert first == "QA"
    assert llm.calls == 1  # 首查走 LLM

    second = norm.normalize(raw)
    assert second == "QA"
    assert llm.calls == 1  # 再查命中快取、LLM 呼叫次數不增（0 API）


def test_feature_flag_off_preserves_raw(session_factory, monkeypatch):
    """④ 旗標 off：normalize_to_lcc 走舊行為（原樣回傳 raw、不查 DB/不呼 LLM）。"""
    import settings
    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", False)
    # 確保單例未被先前測試污染
    monkeypatch.setattr(dn, "_normalizer_singleton", None)

    raw = "電力電子技術 - 高壓直流系統"
    result = dn.normalize_to_lcc(raw, context_text="HVDC 換流站")

    # 舊行為：原樣回傳 raw
    assert result == raw
    # 旗標 off 不應實例化對齊器（不建 LLMClient / DB 連線）
    assert dn._normalizer_singleton is None

    # 反向確認：旗標 on 時委派對齊器（以假對齊器驗證分派路徑）
    class _FakeNorm:
        def normalize(self, raw_domain, context_text=None):
            return "ZZ"

    monkeypatch.setattr(settings, "LLM_USE_GLOSSARY_ALIGN", True)
    monkeypatch.setattr(dn, "_normalizer_singleton", _FakeNorm())
    assert dn.normalize_to_lcc(raw) == "ZZ"
