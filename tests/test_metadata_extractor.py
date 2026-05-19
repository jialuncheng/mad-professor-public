"""Phase 4.2 單元測試：processor/metadata_extractor.py

本環境 output/ 無真實 PDF（未跑 migration/上傳），故：
- 邏輯以 fitz 產生的「合成 PDF」做確定性驗證（已設定 metadata/首頁文字）。
- 真實專案 PDF（800-vdc-... / kahneman2009）若不存在則 skip（不讓套件失敗）。
"""
import sys
from pathlib import Path

import pytest
import fitz

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from processor.metadata_extractor import (  # noqa: E402
    SCHEMA_VERSION,
    create_empty_metadata,
    extract_pdf_metadata,
    fill_from_pdf_metadata,
    date_to_iso,
    parse_authors,
    get_first_page_text,
    get_first_page_render,
)


# ── 合成 PDF fixture（確定性）──

@pytest.fixture(scope="module")
def synthetic_pdf(tmp_path_factory):
    p = tmp_path_factory.mktemp("md") / "synthetic.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), "800 VDC Architecture for Next-Generation")
    page.insert_text((72, 120), "AI Infrastructure")
    page.insert_text((72, 160), "Jared Huntington and Mike Tu")
    doc.set_metadata({
        "title": "",  # 模擬 Word 匯出常見：title 空
        "author": "Jared Huntington and Mike Tu",
        "subject": "Power distribution",
        "keywords": "GPU, Data Center, Power Distribution",
        "creator": "Microsoft Word",
        "producer": "test",
        "creationDate": "D:20251009144037-07'00'",
    })
    doc.save(str(p))
    doc.close()
    return str(p)


@pytest.fixture(scope="module")
def noisy_title_pdf(tmp_path_factory):
    p = tmp_path_factory.mktemp("md2") / "noisy.pdf"
    doc = fitz.open()
    doc.new_page().insert_text((72, 100), "hello")
    doc.set_metadata({"title": "Microsoft Word - draft.docx",
                       "author": "Alice"})
    doc.save(str(p))
    doc.close()
    return str(p)


# ── 純解析函式 ──

def test_date_parsing():
    assert date_to_iso("D:20251009144037-07'00'") == "2025-10-09"
    assert date_to_iso("D:20240102") == "2024-01-02"
    assert date_to_iso("2023-7-5") == "2023-07-05"
    assert date_to_iso("20221130") == "2022-11-30"
    assert date_to_iso(None) is None
    assert date_to_iso("") is None
    assert date_to_iso("not-a-date") is None
    assert date_to_iso("D:20259999") is None  # 月份非法


def test_authors_parsing():
    assert parse_authors("Jared Huntington and Mike Tu") == \
        ["Jared Huntington", "Mike Tu"]
    assert parse_authors("A, B; C & D") == ["A", "B", "C", "D"]
    assert parse_authors("Solo Author") == ["Solo Author"]
    assert parse_authors("Dup, Dup") == ["Dup"]      # 去重
    assert parse_authors(None) == []
    assert parse_authors("") == []


def test_empty_metadata_structure():
    m = create_empty_metadata()
    assert m["_schema_version"] == SCHEMA_VERSION == 2
    assert m["_stage_b_ran"] is False
    for f in ["title", "translated_title", "authors", "publication_date",
              "abstract", "journal_or_conference", "doi", "keywords",
              "publisher", "organization", "version"]:
        assert f in m, f"缺欄位 {f}"
        assert set(m[f]) == {"value", "source", "confidence", "alternates"}
        assert m[f]["source"] is None
        assert m[f]["confidence"] is None
        assert m[f]["alternates"] == {}
    assert m["authors"]["value"] == []
    assert m["keywords"]["value"] == []
    assert m["title"]["value"] is None


# ── 合成 PDF 抽取 ──

def test_extract_from_synthetic(synthetic_pdf):
    pm = extract_pdf_metadata(synthetic_pdf)
    assert pm["authors"] == ["Jared Huntington", "Mike Tu"]
    assert pm["title"] is None              # 空 title
    assert pm["creation_date"] == "2025-10-09"
    assert pm["publication_date"] == "2025-10-09"
    assert pm["keywords"] == ["GPU", "Data Center", "Power Distribution"]
    assert pm["creator"] == "Microsoft Word"


def test_noisy_title_filtered(noisy_title_pdf):
    pm = extract_pdf_metadata(noisy_title_pdf)
    assert pm["title"] is None              # 'Microsoft Word - draft.docx' 視為雜訊
    assert pm["authors"] == ["Alice"]


def test_fill_from_pdf_metadata(synthetic_pdf):
    pm = extract_pdf_metadata(synthetic_pdf)
    meta = create_empty_metadata()
    meta = fill_from_pdf_metadata(meta, pm)
    assert meta["authors"]["value"] == ["Jared Huntington", "Mike Tu"]
    assert meta["authors"]["source"] == "pdf_metadata"
    assert meta["authors"]["confidence"] == "high"
    assert meta["publication_date"]["value"] == "2025-10-09"
    assert meta["publication_date"]["confidence"] == "medium"
    # alternates 一律記錄
    assert meta["authors"]["alternates"]["pdf_metadata"] == \
        ["Jared Huntington", "Mike Tu"]
    # 先到先得：title 空，未被覆寫
    assert meta["title"]["value"] is None


def test_first_page_text(synthetic_pdf):
    txt = get_first_page_text(synthetic_pdf)
    assert txt is not None
    assert "800 VDC Architecture" in txt


def test_first_page_render(synthetic_pdf):
    png = get_first_page_render(synthetic_pdf)
    assert png is not None
    assert png[:8] == b"\x89PNG\r\n\x1a\n"   # PNG 魔數


def test_invalid_pdf_soft_fail(tmp_path):
    bad = tmp_path / "broken.pdf"
    bad.write_bytes(b"not a pdf at all")
    # 絕不 raise
    pm = extract_pdf_metadata(str(bad))
    assert pm["title"] is None and pm["authors"] == []
    assert get_first_page_text(str(bad)) is None
    assert get_first_page_render(str(bad)) is None
    pm2 = extract_pdf_metadata("/no/such/file.pdf")
    assert pm2["authors"] == []
    # fill 也不 raise
    fill_from_pdf_metadata(create_empty_metadata(), pm2)


# ── 真實專案 PDF（不存在則 skip，不讓套件失敗）──

@pytest.mark.parametrize("rel", [
    "output/1/800-vdc-architecture-for-ai-infrastructure/original.pdf",
    "output/1/kahneman2009/original.pdf",
])
def test_real_project_pdf_if_present(rel):
    pdf = ROOT / rel
    if not pdf.exists():
        pytest.skip(f"真實 PDF 不存在（此環境 output/ 為空）：{rel}")
    pm = extract_pdf_metadata(str(pdf))
    assert isinstance(pm["authors"], list)
    assert pm["creation_date"] is None or len(pm["creation_date"]) == 10
    meta = fill_from_pdf_metadata(create_empty_metadata(), pm)
    assert meta["_schema_version"] == 2
