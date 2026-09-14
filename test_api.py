"""
api.py 的自动化测试。

运行方式：
    pip install pytest httpx        # TestClient 依赖 httpx
    pytest -v                       # 在项目目录（DayOne.py / api.py 所在处）执行

关键点：下面的 client 夹具给每个测试都换上一个“临时空笔记文件”，
所以测试不会污染你真实的 notes.json。
"""

import pytest
from fastapi.testclient import TestClient

import api
from DayOne import NoteManager


@pytest.fixture
def client(tmp_path, monkeypatch):
    """每个测试用独立的临时文件，保证互不影响、也不碰真实数据。"""
    tmp_file = tmp_path / "test_notes.json"
    # 把 api 模块里的全局 note_manager 换成指向临时文件的新实例
    monkeypatch.setattr(api, "note_manager", NoteManager(str(tmp_file)))
    return TestClient(api.app)


# ---------- 创建 ----------

def test_create_note_returns_201(client):
    """创建成功应返回 201，并且带回 id。"""
    resp = client.post("/notes", json={"title": "标题", "content": "内容"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "标题"
    assert data["content"] == "内容"
    assert data["id"] == 1


def test_create_rejects_missing_field(client):
    """缺字段应被 Pydantic 拦下，返回 422。"""
    resp = client.post("/notes", json={"title": "只有标题"})
    assert resp.status_code == 422


# ---------- 列表 ----------

def test_list_notes_empty_at_start(client):
    """新库应为空列表。"""
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_notes_after_create(client):
    """建两条后，列表长度应为 2。"""
    client.post("/notes", json={"title": "A", "content": "a"})
    client.post("/notes", json={"title": "B", "content": "b"})
    resp = client.get("/notes")
    assert len(resp.json()) == 2


# ---------- 搜索（重点：验证路由顺序没被吃掉） ----------

def test_search_returns_matches(client):
    """/notes/search 应走搜索接口，而不是被当成 note_id 报 422。"""
    client.post("/notes", json={"title": "Python", "content": "学习记录"})
    client.post("/notes", json={"title": "日记", "content": "今天很好"})
    resp = client.get("/notes/search", params={"keyword": "python"})
    assert resp.status_code == 200          # 若是 422，说明 /notes/{id} 排在了前面
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Python"


def test_search_is_case_insensitive(client):
    """搜索应忽略大小写。"""
    client.post("/notes", json={"title": "FastAPI", "content": "x"})
    resp = client.get("/notes/search", params={"keyword": "fastapi"})
    assert len(resp.json()) == 1


# ---------- 删除 ----------

def test_delete_missing_returns_404(client):
    """删除不存在的 ID 应返回 404（验收清单里点名的一条）。"""
    resp = client.delete("/notes/999")
    assert resp.status_code == 404


def test_delete_then_list(client):
    """删除后列表里不应再有它。"""
    note_id = client.post("/notes", json={"title": "待删", "content": "x"}).json()["id"]
    assert client.delete(f"/notes/{note_id}").status_code == 200
    ids = [n["id"] for n in client.get("/notes").json()]
    assert note_id not in ids


# ---------- 端到端往返 ----------

def test_create_then_search_roundtrip(client):
    """建一条能立刻搜到，删掉后搜不到——串起一整条链路。"""
    client.post("/notes", json={"title": "唯一关键词Z", "content": "内容"})
    assert len(client.get("/notes/search", params={"keyword": "关键词Z"}).json()) == 1

    note_id = client.get("/notes").json()[0]["id"]
    client.delete(f"/notes/{note_id}")
    assert client.get("/notes/search", params={"keyword": "关键词Z"}).json() == []
