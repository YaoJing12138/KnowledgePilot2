import pytest
import sqlite3
from fastapi.testclient import TestClient

import api
from DayOne import NoteManager
@pytest.fixture
def client(tmp_path):
    tmp_db = tmp_path / "test_notes.db"

    # 一个"替身"连接函数：和 api.connect_db 长得一样，但指向临时库
    def override_connect_db():
        conn = sqlite3.connect(tmp_db)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # 挂上"换车源"的牌子：凡是要 connect_db 的，都改用上面的替身
    api.app.dependency_overrides[api.connect_db] = override_connect_db
    yield TestClient(api.app)
    # 测完摘牌子，别污染别的测试
    api.app.dependency_overrides.clear()