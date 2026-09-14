from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
from DayOne import NoteManager
from fastapi.responses import RedirectResponse

note_manager = NoteManager()
app = FastAPI()

class NoteIn(BaseModel):
    title: str
    content: str

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.post("/notes" , status_code=201)
def create_note(note_in : NoteIn):
    """创建一条新的笔记"""
    note = note_manager.add(note_in.title , note_in.content)
    return note

@app.get("/notes")
def list_notes():
    """返回所有笔记"""
    return note_manager.list_all()

@app.get("/notes/search")
def search_notes(keyword: str):
    """搜索笔记"""
    return note_manager.search(keyword)

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    """删除一条笔记"""
    ok = note_manager.delete(note_id)
    if not ok:
        raise HTTPException(status_code=404 , detail=f"未找到 ID 为 {note_id} 的笔记。")
    return {"message": f"笔记 ID {note_id} 已删除。"}