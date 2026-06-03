"""RAG-1 Phase 2 P2-2：後端 hashtag RAG 路由 pytest（12 個、≥ 8）。

涵蓋：
- paper_manager.list_paper_uuids_by_tag（含 case-insensitive / skip not done / Q3 跨 owner 隔離）
- paper_manager.parse_query_hashtag（含長標籤優先、無匹配、純 tag 無問題、空 owner）
- rag_retriever.retrieve_multi_with_context（多 paper Merge-Sort + empty / top_k env）
- AI_professor_chat.process_query_stream 入口分流（0 篇 warning / 多篇 multi / 無 hashtag fallback）
"""
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import db as db_mod  # noqa: E402
from models import Base, Paper, User  # noqa: E402
import paper_manager  # noqa: E402


# ─────────────────── fixture（沿用 R1/R2/R3 pattern）───────────────────


@pytest.fixture
def temp_db(monkeypatch):
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
    monkeypatch.setattr(db_mod, 'engine', engine)
    monkeypatch.setattr(db_mod, 'SessionLocal', TestSession)
    monkeypatch.setattr(paper_manager, '_ensure_db', lambda: None)
    yield db_mod, sys.modules['models'], paper_manager
    engine.dispose()
    try:
        os.unlink(path)
    except OSError:
        pass


def _make_user(db_mod_p, models_mod, owner_id):
    with db_mod_p.SessionLocal() as s:
        if not s.query(models_mod.User).filter_by(id=owner_id).first():
            s.add(models_mod.User(
                id=owner_id, username=f'u{owner_id}', password_hash='x'
            ))
            s.commit()


def _make_paper(db_mod_p, models_mod, owner_id, paper_uuid, user_tags,
                status='done'):
    _make_user(db_mod_p, models_mod, owner_id)
    with db_mod_p.SessionLocal() as s:
        p = models_mod.Paper(
            owner_id=owner_id,
            paper_uuid=paper_uuid,
            status=status,
            original_filename=f'{paper_uuid}.pdf',
            metadata_json=json.dumps({"user_tags": user_tags}),
        )
        s.add(p)
        s.commit()


# ─────────────────── list_paper_uuids_by_tag（4 個）───────────────────


def test_list_paper_uuids_by_tag_finds_matches(temp_db):
    """3 paper 中 2 個含 #hr → 回 2 個 uuid。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr', 'plant'])
    _make_paper(db_mod_p, models_mod, 1, 'p2', ['hr'])
    _make_paper(db_mod_p, models_mod, 1, 'p3', ['plant'])

    with db_mod_p.SessionLocal() as s:
        uuids = pm.list_paper_uuids_by_tag(s, 1, 'hr')
    assert set(uuids) == {'p1', 'p2'}


def test_list_paper_uuids_by_tag_case_insensitive(temp_db):
    """tag='#HR' 查詢、metadata 存 'hr'、仍能匹配（_normalize_tag）。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr'])

    with db_mod_p.SessionLocal() as s:
        uuids = pm.list_paper_uuids_by_tag(s, 1, 'HR')
    assert uuids == ['p1']


def test_list_paper_uuids_by_tag_skips_not_done(temp_db):
    """status='processing' 的 paper 被過濾。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr'], status='done')
    _make_paper(db_mod_p, models_mod, 1, 'p2', ['hr'], status='processing')

    with db_mod_p.SessionLocal() as s:
        uuids = pm.list_paper_uuids_by_tag(s, 1, 'hr')
    assert uuids == ['p1']


def test_list_paper_uuids_by_tag_owner_isolation(temp_db):
    """Q3：跨 owner 隔離、owner=2 的 paper 即使含 #hr 也不洩漏給 owner=1。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'own_p1', ['hr'])
    _make_paper(db_mod_p, models_mod, 2, 'own_p2', ['hr'])

    with db_mod_p.SessionLocal() as s:
        uuids_1 = pm.list_paper_uuids_by_tag(s, 1, 'hr')
        uuids_2 = pm.list_paper_uuids_by_tag(s, 2, 'hr')
    assert uuids_1 == ['own_p1']
    assert uuids_2 == ['own_p2']


# ─────────────────── parse_query_hashtag（4 個）───────────────────


def test_parse_query_hashtag_long_tag_priority(temp_db):
    """#complex_system 問題 不被 #complex 誤攔（長度排序生效）。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['complex', 'complex_system'])

    with db_mod_p.SessionLocal() as s:
        tag, cleaned = pm.parse_query_hashtag(
            s, 1, '#complex_system 這篇有甚麼重點?'
        )
    assert tag == 'complex_system'
    assert cleaned == '這篇有甚麼重點?'


def test_parse_query_hashtag_no_match_returns_none(temp_db):
    """#unknown 問題 → (None, 原 query)。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr'])

    with db_mod_p.SessionLocal() as s:
        tag, cleaned = pm.parse_query_hashtag(s, 1, '#unknown question?')
    assert tag is None
    assert cleaned == '#unknown question?'


def test_parse_query_hashtag_tag_only_no_question(temp_db):
    """`#hr` 純 tag 無後續問題 → ('hr', '')。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr'])

    with db_mod_p.SessionLocal() as s:
        tag, cleaned = pm.parse_query_hashtag(s, 1, '#hr')
    assert tag == 'hr'
    assert cleaned == ''


def test_parse_query_hashtag_no_hash_prefix(temp_db):
    """query 不以 # 開頭 → 直接回 (None, 原 query)、不查 DB。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['hr'])

    with db_mod_p.SessionLocal() as s:
        tag, cleaned = pm.parse_query_hashtag(s, 1, '一般問題不含 hashtag')
    assert tag is None
    assert cleaned == '一般問題不含 hashtag'


# ─────────────────── retrieve_multi_with_context（3 個）───────────────────


def _make_retriever_with_mock_papers(paper_score_chunks):
    """建 RagRetriever、注入 mock vector_stores + rag_trees。

    paper_score_chunks: dict[paper_id, list[(score, chunk_text)]]
    """
    from rag_retriever import RagRetriever
    r = RagRetriever(base_path='/tmp/test_multi')
    for pid, score_chunks in paper_score_chunks.items():
        # mock FAISS：similarity_search_with_score 回固定 (Document, score)
        mock_vs = MagicMock()

        def _make_search(_sc):
            def _search(query, k=5):
                results = []
                for s, c in _sc[:k]:
                    doc = SimpleNamespace(page_content=c, metadata={})
                    results.append((doc, s))
                return results
            return _search

        mock_vs.similarity_search_with_score = _make_search(score_chunks)
        r.vector_stores[(1, pid)] = mock_vs
        r.paper_vector_paths[(1, pid)] = f'/fake/{pid}'  # 讓 is_ready() = True
        r.rag_trees[(1, pid)] = {'translated_title': f'paper_{pid}_title'}
    return r


def test_retrieve_multi_with_context_merges_top_k():
    """2 paper 各 5 chunks（score 從 0.9 遞減）、top_k=7 → 全域取最高 7 個 + 含 paper title。"""
    paper_chunks = {
        'A': [(0.9 - 0.1 * i, f'A_chunk_{i}') for i in range(5)],
        'B': [(0.85 - 0.1 * i, f'B_chunk_{i}') for i in range(5)],
    }
    r = _make_retriever_with_mock_papers(paper_chunks)
    ctx = r.retrieve_multi_with_context(
        owner_id=1, query='dummy', paper_ids=['A', 'B'], top_k=7,
    )
    # 應含至少 7 段「## 摘自文件《...》」標頭
    headers = [line for line in ctx.split('\n') if line.startswith('## 摘自文件')]
    assert len(headers) == 7
    # title 正確
    assert '《paper_A_title》' in ctx
    assert '《paper_B_title》' in ctx


def test_retrieve_multi_with_context_empty_paper_ids():
    """paper_ids=[] → 回空字串、不 raise。"""
    r = _make_retriever_with_mock_papers({})
    ctx = r.retrieve_multi_with_context(
        owner_id=1, query='dummy', paper_ids=[], top_k=7,
    )
    assert ctx == ''


def test_retrieve_multi_with_context_top_k_from_settings(monkeypatch):
    """Q5：top_k=None 時走 settings.RAG_MULTI_TOP_K（mock = 3）。"""
    import rag_retriever as rr_mod
    monkeypatch.setattr(rr_mod, 'RAG_MULTI_TOP_K', 3)
    monkeypatch.setattr(rr_mod, 'RAG_SCORE_THRESHOLD', 0.0)
    paper_chunks = {
        'A': [(0.9 - 0.1 * i, f'A_chunk_{i}') for i in range(5)],
    }
    r = _make_retriever_with_mock_papers(paper_chunks)
    ctx = r.retrieve_multi_with_context(
        owner_id=1, query='dummy', paper_ids=['A'], top_k=None,
    )
    headers = [line for line in ctx.split('\n') if line.startswith('## 摘自文件')]
    assert len(headers) == 3


# ─────────────────── AI_professor_chat 入口分流（3 個）───────────────────


@pytest.fixture
def mocked_chat(temp_db, monkeypatch):
    """建 AIProfessorChat、注入 mock LLMClient + mock retriever。"""
    from AI_professor_chat import AIProfessorChat
    chat = AIProfessorChat()
    chat.llm_client = MagicMock()
    chat.llm_client.chat_stream_by_sentence = MagicMock(
        return_value=iter(['回答 ', '已生成。'])
    )
    chat.llm_client._last_grounding_sources = []
    chat.retriever = MagicMock()
    chat.retriever.is_ready = MagicMock(return_value=True)
    chat.retriever.retrieve_multi_with_context = MagicMock(
        return_value='## 摘自文件《T》\nMULTI_CONTEXT'
    )
    # mock _prepare_final_messages（內讀 prompt 檔、純 IO）
    chat._prepare_final_messages = MagicMock(
        return_value=[{'role': 'user', 'content': 'final'}]
    )
    return chat


def test_process_query_stream_zero_papers_for_known_tag(
    temp_db, monkeypatch, mocked_chat
):
    """Q6：tag 在 distinct set、但 list_paper_uuids_by_tag 找到 0（皆非 done）→ warning。"""
    db_mod_p, models_mod, pm = temp_db
    # 故意製造：distinct 集合有 'ghost'、但所有 paper status='processing'
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['ghost'], status='processing')

    # parse_query_hashtag 也只看 status='done' → 對 'ghost' 也回 None
    # 所以單純這條件不會觸發 0 匹配 warning。
    # 真實 0 篇情境：先寫一個 done paper 含 hashtag、執行 parse 成功、
    # 然後在 list 前刪掉/降級 → 太繞。
    # 改用 monkeypatch：直接 mock paper_manager.parse_query_hashtags 回 (['ghost'], '問題?')
    # + mock list_paper_uuids_by_tag 回 []
    import paper_manager as pm_mod
    monkeypatch.setattr(
        pm_mod, 'parse_query_hashtags',
        lambda s, oid, q: (['ghost'], '問題?')
    )
    monkeypatch.setattr(
        pm_mod, 'list_paper_uuids_by_tag',
        lambda s, oid, t: []
    )

    events = list(mocked_chat.process_query_stream(
        query='#ghost 問題?', owner_id=1, paper_id=None,
        paper_data=None, conversation_history=[],
    ))
    # 應 yield 1 sentence warning + 1 done、不呼叫 LLM
    sentences = [e for e in events if e['type'] == 'sentence']
    dones = [e for e in events if e['type'] == 'done']
    assert len(sentences) == 1
    assert '#ghost' in sentences[0]['text']
    assert len(dones) == 1
    assert mocked_chat.llm_client.chat_stream_by_sentence.call_count == 0


def test_process_query_stream_multi_papers_routes_to_multi(
    temp_db, monkeypatch, mocked_chat
):
    """多篇符合 hashtag → 走 retrieve_multi_with_context + 繞 router。"""
    import paper_manager as pm_mod
    monkeypatch.setattr(
        pm_mod, 'parse_query_hashtags',
        lambda s, oid, q: (['hr'], '比較這幾篇')
    )
    monkeypatch.setattr(
        pm_mod, 'list_paper_uuids_by_tag',
        lambda s, oid, t: ['pA', 'pB', 'pC']
    )

    events = list(mocked_chat.process_query_stream(
        query='#hr 比較這幾篇', owner_id=1, paper_id=None,
        paper_data=None, conversation_history=[],
    ))
    # retriever.retrieve_multi_with_context 被呼叫一次、用 cleaned query
    mocked_chat.retriever.retrieve_multi_with_context.assert_called_once()
    kwargs = mocked_chat.retriever.retrieve_multi_with_context.call_args.kwargs
    assert kwargs['query'] == '比較這幾篇'
    assert kwargs['paper_ids'] == ['pA', 'pB', 'pC']
    assert kwargs['owner_id'] == 1
    # 應 yield 串流 sentences + done
    sentences = [e for e in events if e['type'] == 'sentence']
    dones = [e for e in events if e['type'] == 'done']
    assert len(sentences) >= 1
    assert len(dones) == 1
    # 繞過 router：_make_decision 應未被呼叫（hashtag_routed_multi=True 提前 return）
    # _prepare_final_messages 應收到 'rag_retrieval' function_name
    pf_kwargs = mocked_chat._prepare_final_messages.call_args.kwargs
    assert pf_kwargs['function_name'] == 'rag_retrieval'
    assert pf_kwargs['context_info'] == '## 摘自文件《T》\nMULTI_CONTEXT'


def test_process_query_stream_no_hashtag_falls_back_to_single(
    temp_db, monkeypatch, mocked_chat
):
    """無 hashtag 的 query → 完全不觸發 hashtag 分流、走既有 router 路徑。"""
    # parse_query_hashtags 不應該被呼叫（query 不以 # 開頭、入口先短路）
    parse_called = {'n': 0}

    def _parse(s, oid, q):
        parse_called['n'] += 1
        return ([], q)

    import paper_manager as pm_mod
    monkeypatch.setattr(pm_mod, 'parse_query_hashtags', _parse)

    # mock _make_decision 回 direct_answer
    mocked_chat._make_decision = MagicMock(return_value={
        'function': 'direct_answer', 'query': 'q?'
    })

    events = list(mocked_chat.process_query_stream(
        query='普通問題',  # 不以 # 開頭
        owner_id=1, paper_id=None, paper_data=None,
        conversation_history=[],
    ))
    # 入口分流的條件 `query.startswith("#")` 已 False、parse 不會被呼叫
    assert parse_called['n'] == 0
    # 既有 router + LLM 仍走
    assert mocked_chat._make_decision.call_count == 1
    # multi context 沒被呼叫
    mocked_chat.retriever.retrieve_multi_with_context.assert_not_called()


def test_parse_query_hashtags_combinations(temp_db):
    """測試全新 parse_query_hashtags 在多標籤、容錯關閉字元及多種分隔符號下的解析規格。"""
    db_mod_p, models_mod, pm = temp_db
    _make_paper(db_mod_p, models_mod, 1, 'p1', ['sst', 'cv', 'latex'])

    with db_mod_p.SessionLocal() as s:
        # 1. 測試多標籤 + 關閉符號 × + 逗號空格
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#sst×, #cv× 這份簡報的摘要')
        assert tags == ['sst', 'cv']
        assert cleaned == '這份簡報的摘要'

        # 2. 測試多標籤 + 關閉符號 x + 空格
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#sstx #cvx 這份簡報')
        assert tags == ['sst', 'cv']
        assert cleaned == '這份簡報'

        # 3. 測試多標籤 + 換行
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#sst\n#cv\n這份簡報')
        assert tags == ['sst', 'cv']
        assert cleaned == '這份簡報'

        # 4. 測試手打不帶 x 且結尾為 x 的標籤（防範誤切 late + x）
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#latex 這篇有什麼重點？')
        assert tags == ['latex']
        assert cleaned == '這篇有什麼重點？'

        # 5. 測試純標籤無提問
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#sst× #cv×')
        assert tags == ['sst', 'cv']
        assert cleaned == ''

        # 6. 測試包含無效（不存在）標籤時，自動忽略無效標籤
        tags, cleaned = pm.parse_query_hashtags(s, 1, '#sst×, #unknown× 這份簡報')
        # 遇到未知標籤 '#unknown×' 應停止解析標籤，將其視為提問本文一部分
        assert tags == ['sst']
        assert cleaned == '#unknown× 這份簡報'

