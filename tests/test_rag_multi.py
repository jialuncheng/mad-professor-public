# === [RAG-MULTI-1 C4] ===
"""RAG-MULTI-1：跨文件多篇檢索「每篇保底覆蓋」演算法 + 引用禁 [N] pytest（11 個）。

對齊 plan v3 §8.1 / tasks §8 C4。以**真實演算法**驗證——僅 mock vector store 的
similarity_search_with_score（確定化、distinct 分數避免 tie 不確定）與 load_rag_tree（回 title）；
不 mock retrieve_multi_with_context 本體。

covered（plan v3 §2 U1-U6）：
- U1 每篇保底覆蓋 + 不足全拿（1/2）
- U2 effective_floor=min(floor_k,max(1,cap//N))：小 N 不暴漲（3）/ cap 不超（4）/ N>cap 最高分截斷（5）/ 補位排除已保底（6）/ cap override（8）
- 0 候選跳過（7）/ U4 混型 book 不壓 resume（9）/ U6 單篇路徑不變（10）/ U5 提示詞禁 [N]（11）
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rag_retriever as rr_mod  # noqa: E402
from rag_retriever import RagRetriever  # noqa: E402


# ─────────────────── mock 範式（自包含；鏡像 test_phase2_p2_2 的 _make_retriever）───────────────────
def _make_retriever(paper_score_chunks):
    """建 RagRetriever、注入 mock vector_stores + rag_trees。

    paper_score_chunks: dict[pid, list[(score, chunk_text)]]（score 須 distinct、降序最清晰）
    """
    r = RagRetriever(base_path='/tmp/test_rag_multi')
    for pid, score_chunks in paper_score_chunks.items():
        mock_vs = MagicMock()

        def _make_search(_sc):
            def _search(query, k=5):
                out = []
                for s, c in _sc[:k]:
                    out.append((SimpleNamespace(page_content=c, metadata={}), s))
                return out
            return _search

        mock_vs.similarity_search_with_score = _make_search(score_chunks)
        r.vector_stores[(1, pid)] = mock_vs
        r.paper_vector_paths[(1, pid)] = f'/fake/{pid}'  # is_ready() = True
        r.rag_trees[(1, pid)] = {'translated_title': f'{pid}_title'}
    return r


def _headers(ctx):
    return [ln for ln in ctx.split('\n') if ln.startswith('## 摘自文件')]


def _pid_count(ctx, pid):
    """ctx 中屬於 pid 的 chunk 數（chunk 內文以 pid_ 開頭）。"""
    return sum(1 for ln in ctx.split('\n') if ln.startswith(f'{pid}_'))


@pytest.fixture(autouse=True)
def _no_threshold(monkeypatch):
    """預設門檻 0.0（除非測試自行覆寫）——多數測試只驗保底分配、不驗門檻。"""
    monkeypatch.setattr(rr_mod, 'RAG_SCORE_THRESHOLD', 0.0)


# ─────────────────── 1. 每篇保底覆蓋（U1）───────────────────
def test_multi_per_paper_floor(monkeypatch):
    """3 篇 A>B>C、cap=6 binding、floor=2 → 每篇各 2（C 低分仍被代表，全域 top-6 會給 C=0）。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {
        'A': [(0.90, 'A_0'), (0.88, 'A_1'), (0.86, 'A_2')],
        'B': [(0.70, 'B_0'), (0.68, 'B_1'), (0.66, 'B_2')],
        'C': [(0.40, 'C_0'), (0.38, 'C_1'), (0.36, 'C_2')],  # 全域最低、舊 top-k 會被擠掉
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'B', 'C'], top_k=6)
    assert len(_headers(ctx)) == 6
    assert _pid_count(ctx, 'A') == 2
    assert _pid_count(ctx, 'B') == 2
    assert _pid_count(ctx, 'C') == 2   # ← 核心：低分 paper 不再 0 代表（吳焴倫場景）


# ─────────────────── 2. 不足全拿（U1 邊界 Q1）───────────────────
def test_multi_floor_underfilled_takes_all(monkeypatch):
    """B 僅 1 候選 → 取 1（不因 floor=2 排除）。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_MAX_CHUNKS', 15)
    papers = {
        'A': [(0.9, 'A_0'), (0.8, 'A_1'), (0.7, 'A_2')],
        'B': [(0.5, 'B_0')],  # 僅 1 候選
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'B'], top_k=None)
    assert _pid_count(ctx, 'B') == 1   # 不足 floor 全拿、不排除


# ─────────────────── 3. 小 N 不暴漲（U2·Q2 修正）───────────────────
def test_multi_small_n_no_floor_balloon(monkeypatch):
    """N=3、cap=10 → effective_floor=min(2, max(1,10//3=3))=2（非 3）。
    驗：C（低分）只取 floor=2，而非被暴漲的 floor=3 拉進第 3 個低分 chunk。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {
        'A': [(0.90, 'A_0'), (0.88, 'A_1'), (0.86, 'A_2'), (0.84, 'A_3'), (0.82, 'A_4')],
        'B': [(0.70, 'B_0'), (0.68, 'B_1'), (0.66, 'B_2'), (0.64, 'B_3'), (0.62, 'B_4')],
        'C': [(0.30, 'C_0'), (0.28, 'C_1'), (0.26, 'C_2'), (0.24, 'C_3'), (0.22, 'C_4')],
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'B', 'C'], top_k=10)
    assert len(_headers(ctx)) == 10
    # floor=2：C 保底 2；補位 4 個全給高分 A/B（非暴漲 floor=3 致 C=3）
    assert _pid_count(ctx, 'C') == 2   # ← 若公式漏 min(floor_k,…)、C 會是 3


# ─────────────────── 4. cap 不超（U2）───────────────────
def test_multi_cap_not_exceeded(monkeypatch):
    """floor×N > cap → 總 chunk ≤ cap、effective_floor 自適應降。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {p: [(0.9 - 0.01 * i, f'{p}_{i}') for i in range(4)] for p in ['A', 'B', 'C', 'D', 'E']}
    r = _make_retriever(papers)  # 5 篇 ×4 = 20 候選
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=list(papers), top_k=8)
    assert len(_headers(ctx)) <= 8
    assert len(_headers(ctx)) == 8   # cap=8、候選 20 → 恰填滿


# ─────────────────── 5. N>cap 按最高分截斷（U2·Q2 截斷序）───────────────────
def test_multi_n_gt_cap_truncate_by_best(monkeypatch):
    """N=4 篇、cap=3 → effective_floor=1、floored=4>cap → 按各篇最高分取前 3 篇各 1（最低 best 那篇 0）。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {
        'A': [(0.90, 'A_0'), (0.5, 'A_1')],
        'B': [(0.80, 'B_0'), (0.5, 'B_1')],
        'C': [(0.70, 'C_0'), (0.5, 'C_1')],
        'D': [(0.20, 'D_0'), (0.1, 'D_1')],  # best 最低 → 被截掉
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'B', 'C', 'D'], top_k=3)
    assert len(_headers(ctx)) == 3
    for p in ['A', 'B', 'C']:
        assert _pid_count(ctx, p) == 1
    assert _pid_count(ctx, 'D') == 0   # ← best 最低之篇被截斷


# ─────────────────── 6. 補位排除已保底（U2 補位池）───────────────────
def test_multi_global_fill_excludes_floored(monkeypatch):
    """補位池排除已保底 chunk → 無重複；headers 數 == 不重複 chunk 數。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {
        'A': [(0.9, 'A_0'), (0.85, 'A_1'), (0.8, 'A_2')],
        'B': [(0.7, 'B_0'), (0.65, 'B_1'), (0.6, 'B_2')],
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'B'], top_k=10)
    chunk_lines = [ln for ln in ctx.split('\n') if ln and ln[0] in ('A', 'B') and '_' in ln[:3]]
    assert len(chunk_lines) == len(set(chunk_lines))   # 無重複（補位未重計保底）
    assert len(_headers(ctx)) == 6   # 6 候選全入、各 1 次


# ─────────────────── 7. 0 候選跳過（門檻交互）───────────────────
def test_multi_zero_candidate_paper_skipped(monkeypatch):
    """C 全部 < threshold → 0 貢獻（不硬塞雜訊）。"""
    monkeypatch.setattr(rr_mod, 'RAG_SCORE_THRESHOLD', 0.5)
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    papers = {
        'A': [(0.9, 'A_0'), (0.8, 'A_1')],
        'C': [(0.3, 'C_0'), (0.2, 'C_1')],  # 全 < 0.5
    }
    r = _make_retriever(papers)
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A', 'C'], top_k=15)
    assert _pid_count(ctx, 'C') == 0
    assert _pid_count(ctx, 'A') == 2


# ─────────────────── 8. cap override（U2）───────────────────
def test_multi_cap_override_param(monkeypatch):
    """top_k=None → RAG_MULTI_MAX_CHUNKS；傳值 → 當 cap。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_MAX_CHUNKS', 4)
    papers = {'A': [(0.9 - 0.05 * i, f'A_{i}') for i in range(10)]}
    r = _make_retriever(papers)
    # None → cap = MAX_CHUNKS(4)
    ctx_none = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A'], top_k=None)
    assert len(_headers(ctx_none)) == 4
    # 傳 3 → cap=3
    ctx_3 = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['A'], top_k=3)
    assert len(_headers(ctx_3)) == 3


# ─────────────────── 9. 混型：book 不壓 resume（U4 五路通用 Q5）───────────────────
def test_multi_mixed_doctype_small_not_starved(monkeypatch):
    """book（100 chunk、分數均勻偏高）+ resume（5 chunk 低分）、cap=15、floor=2 →
    resume 仍被保底代表（不被大文件全域壓制）。"""
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_FLOOR_K', 2)
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_MAX_CHUNKS', 15)
    book = [(0.80 - 0.001 * i, f'book_{i}') for i in range(100)]      # 100 chunk、皆 > resume
    resume = [(0.50, 'resume_0'), (0.49, 'resume_1'), (0.48, 'resume_2'),
              (0.47, 'resume_3'), (0.46, 'resume_4')]
    r = _make_retriever({'book': book, 'resume': resume})
    ctx = r.retrieve_multi_with_context(owner_id=1, query='q', paper_ids=['book', 'resume'], top_k=None)
    assert _pid_count(ctx, 'resume') >= 2   # ← 保底使小文件不被 book 全域壓制（全域 top-15 會給 resume=0）
    assert len(_headers(ctx)) == 15


# ─────────────────── 10. 單篇路徑不變（U6）───────────────────
def test_single_path_unchanged(monkeypatch):
    """單篇 retrieve_with_context（top_k=5、Header→key_map→node 導航）行為等價、不受 C2 多篇改動影響。

    單篇路徑與多篇分離、C2 一行未改；此測以單篇所需之完整 mock（Header metadata + key_map + sections）
    驗證端到端仍正確產出 context。
    """
    monkeypatch.setattr(rr_mod, 'RAG_SCORE_THRESHOLD', 0.0)
    r = RagRetriever(base_path='/tmp/test_rag_multi_single')
    mock_vs = MagicMock()
    mock_vs.similarity_search_with_score = lambda query, k=5: [
        (SimpleNamespace(page_content='A_chunk', metadata={'Header': 'H0'}), 0.9)
    ]
    r.vector_stores[(1, 'A')] = mock_vs
    r.paper_vector_paths[(1, 'A')] = '/fake/A'
    r.rag_trees[(1, 'A')] = {
        'translated_title': 'A_title',
        'key_map': {'H0': '/sections/0/content/0'},
        'sections': [{'translated_title': '章節一', 'content': [
            {'type': 'text', 'content': 'A_chunk', 'translated_content': 'A_chunk'}
        ], 'children': []}],
    }
    ctx = r.retrieve_with_context(owner_id=1, query='q', paper_id='A', top_k=5)
    assert isinstance(ctx, str) and ctx.strip() != ''
    assert 'A_chunk' in ctx and 'A_title' in ctx   # 單篇導航正確、含 paper title 前綴


# ─────────────────── 11. 提示詞禁 [N]（U5、驗 C3 落地）───────────────────
def test_prompt_forbids_bracket_citation():
    """ai_character_prompt.txt 引用段含「禁 [數字] 引用」指示（C3）。"""
    txt = (ROOT / 'prompt' / 'ai' / 'ai_character_prompt.txt').read_text(encoding='utf-8')
    assert '嚴禁輸出' in txt and '純數字引用標記' in txt
    assert '[1]' in txt   # 明示禁止之範例
