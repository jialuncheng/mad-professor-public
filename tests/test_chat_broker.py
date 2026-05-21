"""Phase 4.7d Commit 17-2：stream broker 單元測試。

不依賴 pytest-asyncio（venv 未裝）；用 asyncio.run() 跑 async helper。
不啟動 FastAPI app；只 import broker dataclass + helpers。
"""
import sys
import asyncio
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# 注意：import web_server 會 register routes + 建 FastAPI app（無副作用、
# lifespan 不會跑除非 server start）。我們只用 dataclass + helpers。
import web_server  # noqa: E402


@pytest.fixture(autouse=True)
def clean_active_streams():
    """每測試前清 active_streams（避免污染）。"""
    web_server.active_streams.clear()
    yield
    web_server.active_streams.clear()


def _new_session(buffer=None) -> 'web_server.StreamSession':
    return web_server.StreamSession(
        owner_id=1, paper_db_id=1, paper_uuid='test', query='q',
        chunks_buffer=list(buffer or []),
    )


# ── StreamSession 初始化 ──

def test_stream_session_init():
    """StreamSession 初始化空 buffer / subscribers / 未 done。"""
    session = web_server.StreamSession(
        owner_id=1, paper_db_id=1, paper_uuid='test', query='hello',
    )
    assert session.chunks_buffer == []
    assert session.subscribers == []
    assert session.done is False
    assert session.error is None
    assert session.grounding_sources == []
    assert session.started_at > 0


# ── _broadcast ──

def test_broadcast_to_single_subscriber():
    async def run():
        session = _new_session()
        q: asyncio.Queue = asyncio.Queue(maxsize=10)
        session.subscribers.append(q)
        await web_server._broadcast(session, {'sentence': 'hello', 'done': False})
        chunk = await q.get()
        assert chunk['sentence'] == 'hello'
        assert chunk['done'] is False
    asyncio.run(run())


def test_broadcast_to_multiple_subscribers():
    """多 subscriber 同時收到同樣 chunk（內建多瀏覽器支援）。"""
    async def run():
        session = _new_session()
        qs = [asyncio.Queue(maxsize=10) for _ in range(3)]
        session.subscribers.extend(qs)
        await web_server._broadcast(session, {'sentence': 'broadcast', 'done': False})
        for q in qs:
            chunk = await q.get()
            assert chunk['sentence'] == 'broadcast'
    asyncio.run(run())


def test_broadcast_queue_full_drops_safely():
    """queue full 時不炸、partial 在 chunks_buffer 仍完整。"""
    async def run():
        session = _new_session()
        q: asyncio.Queue = asyncio.Queue(maxsize=1)
        q.put_nowait({'pre': 'filled'})  # 填滿
        session.subscribers.append(q)
        # 應該不 raise（log warning + drop）
        await web_server._broadcast(session, {'sentence': 'dropped', 'done': False})
        # 原 chunk 還在、queue 仍只有 1 個
        assert q.qsize() == 1
    asyncio.run(run())


# ── _pump_to_client ──

def test_pump_replays_buffer_then_streams():
    """新 subscriber attach 時、已產生的 partial 一次回放、再接 queue read 新 chunks。"""
    async def run():
        session = _new_session(buffer=['part1 ', 'part2 ', 'part3'])
        sub_q: asyncio.Queue = asyncio.Queue(maxsize=10)
        session.subscribers.append(sub_q)

        # 在 pump 開始前先 put 一筆新 chunk（done）
        sub_q.put_nowait({'sentence': ' final', 'done': True})

        # 收集 yield 出的 SSE 行
        lines = []
        async for line in web_server._pump_to_client(session, sub_q):
            lines.append(line)

        # 預期：3 個 replay（含 'replay': True）+ 1 個 done
        assert len(lines) == 4
        for i, expected_text in enumerate(['part1', 'part2', 'part3']):
            assert expected_text in lines[i]
            assert '"replay": true' in lines[i]
        # 第 4 個是真新 chunk、無 replay 標記
        assert '"done": true' in lines[3]
        assert 'final' in lines[3]
        assert '"replay"' not in lines[3]

        # pump 結束後 subscriber 應被移除
        assert sub_q not in session.subscribers
    asyncio.run(run())


def test_pump_no_buffer_no_replay():
    """sender 第一次 attach 時 chunks_buffer 為空、不回放重複。"""
    async def run():
        session = _new_session(buffer=[])
        sub_q: asyncio.Queue = asyncio.Queue(maxsize=10)
        session.subscribers.append(sub_q)
        sub_q.put_nowait({'sentence': 'first', 'done': False})
        sub_q.put_nowait({'sentence': '', 'done': True})

        lines = []
        async for line in web_server._pump_to_client(session, sub_q):
            lines.append(line)

        assert len(lines) == 2
        assert 'first' in lines[0]
        assert '"replay"' not in lines[0]
        assert '"done": true' in lines[1]
    asyncio.run(run())


# ── 內部狀態管理 ──

def test_active_streams_key_format():
    """active_streams key = (owner_id, paper_db_id)、與廣播邏輯一致。"""
    async def run():
        session = _new_session()
        key = (session.owner_id, session.paper_db_id)
        async with web_server.streams_lock:
            web_server.active_streams[key] = session
            assert key in web_server.active_streams
            web_server.active_streams.pop(key)
            assert key not in web_server.active_streams
    asyncio.run(run())
