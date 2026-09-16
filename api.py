from fastapi import FastAPI , HTTPException , Depends
from pydantic import BaseModel
from DayOne import NoteManager , get_connection , init_db
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import sqlite3

@asynccontextmanager
async def lifespan(app):
    """应用程序生命周期管理器"""
    conn = get_connection()
    try:
        init_db(conn)
    finally:
        conn.close()
    yield
app = FastAPI(lifespan=lifespan)

def connect_db():
    """连接到 SQLite 数据库"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_note_manager(conn: sqlite3.Connection = Depends(connect_db)):
    """获取 NoteManager 实例"""
    return NoteManager(conn)
        
class NoteIn(BaseModel):
    title: str
    content: str

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.post("/notes" , status_code=201)
def create_note(note_in : NoteIn, note_manager: NoteManager = Depends(get_note_manager)):
    """创建一条新的笔记"""
    note = note_manager.add(note_in.title , note_in.content)
    return note

@app.get("/notes")
def list_notes(note_manager: NoteManager = Depends(get_note_manager)):
    """返回所有笔记"""
    return note_manager.list_all()

@app.get("/notes/search")
def search_notes(keyword: str, note_manager: NoteManager = Depends(get_note_manager)):
    """搜索笔记"""
    return note_manager.search(keyword)

@app.get("/notes/{note_id}")
def get_note(note_id: int, note_manager: NoteManager = Depends(get_note_manager)):
    """获取一条笔记"""
    note = note_manager.get(note_id)
    if note is None:
        raise HTTPException(status_code=404 , detail=f"未找到 ID 为 {note_id} 的笔记。")
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, note_manager: NoteManager = Depends(get_note_manager)):
    """删除一条笔记"""
    ok = note_manager.delete(note_id)
    if not ok:
        raise HTTPException(status_code=404 , detail=f"未找到 ID 为 {note_id} 的笔记。")
    return {"message": f"笔记 ID {note_id} 已删除。"}