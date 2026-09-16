from fastapi import FastAPI , HTTPException , Depends
from pydantic import BaseModel
from DayOne import NoteManager
from fastapi.responses import RedirectResponse
import sqlite3
import os

app = FastAPI()

def connect_db():
    """连接到 SQLite 数据库"""
    os.makedirs("data" , exist_ok=True)
    conn = sqlite3.connect("data/notes.db")
    conn.row_factory = sqlite3.Row
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

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, note_manager: NoteManager = Depends(get_note_manager)):
    """删除一条笔记"""
    ok = note_manager.delete(note_id)
    if not ok:
        raise HTTPException(status_code=404 , detail=f"未找到 ID 为 {note_id} 的笔记。")
    return {"message": f"笔记 ID {note_id} 已删除。"}