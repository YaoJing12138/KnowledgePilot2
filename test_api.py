"""api.py 的自动化测试。

运行：
    pytest -v

每个测试都会把 api 的连接函数替换成"指向临时文件"的替身，
所以不会污染真实的 data/notes.db。
"""

import pytest
import sqlite3
from fastapi.testclient import TestClient

import api
from DayOne import init_db


@pytest.fixture
def client(tmp_path):
    tmp_db = tmp_path / "test_notes.db"

    # 替身连接函数：和 api.connect_db 长得一样，但指向临时库
    def override_connect_db():
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        init_db(conn)                     # 临时库也要有表（lifespan 管不到它）
        try:
            yield conn
        finally:
            conn.close()

    # 挂上"换车源"的牌子：凡是要 connect_db 的，都用上面的替身
    api.app.dependency_overrides[api.connect_db] = override_connect_db
    yield TestClient(api.app)
    # 测完摘牌子，别污染别的测试
    api.app.dependency_overrides.clear()


# ---------- 创建 ----------

def test_create_note_returns_201(client):
    resp = client.post("/notes", json={"title": "title", "content": "content"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "title"
    assert data["content"] == "content"
    assert data["id"] == 1


def test_create_rejects_missing_field(client):
    resp = client.post("/notes", json={"title": "only title"})
    assert resp.status_code == 422


# ---------- 列表 ----------

def test_list_notes_empty_at_start(client):
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_notes_after_create(client):
    client.post("/notes", json={"title": "A", "content": "a"})
    client.post("/notes", json={"title": "B", "content": "b"})
    assert len(client.get("/notes").json()) == 2


# ---------- 单条（新增：验证 GET /notes/{id}） ----------

def test_get_note_by_id(client):
    note_id = client.post("/notes", json={"title": "X", "content": "x"}).json()["id"]
    resp = client.get(f"/notes/{note_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "X"


def test_get_missing_note_returns_404(client):
    assert client.get("/notes/999").status_code == 404


# ---------- 搜索（重点：验证路由顺序没被吃掉） ----------

def test_search_returns_matches(client):
    client.post("/notes", json={"title": "Python", "content": "study"})
    client.post("/notes", json={"title": "diary", "content": "today"})
    resp = client.get("/notes/search", params={"keyword": "python"})
    assert resp.status_code == 200          # 若是 422，说明 /notes/{id} 排在了前面
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Python"


def test_search_is_case_insensitive(client):
    client.post("/notes", json={"title": "FastAPI", "content": "x"})
    assert len(client.get("/notes/search", params={"keyword": "fastapi"}).json()) == 1


# ---------- 删除 ----------

def test_delete_missing_returns_404(client):
    assert client.delete("/notes/999").status_code == 404


def test_delete_then_list(client):
    note_id = client.post("/notes", json={"title": "tmp", "content": "x"}).json()["id"]
    assert client.delete(f"/notes/{note_id}").status_code == 200
    assert note_id not in [n["id"] for n in client.get("/notes").json()]


# ---------- 端到端 ----------

def test_create_search_delete_roundtrip(client):
    client.post("/notes", json={"title": "unique-keyword-Z", "content": "c"})
    assert len(client.get("/notes/search", params={"keyword": "keyword-Z"}).json()) == 1

    note_id = client.get("/notes").json()[0]["id"]
    client.delete(f"/notes/{note_id}")
    assert client.get("/notes/search", params={"keyword": "keyword-Z"}).json() == []
