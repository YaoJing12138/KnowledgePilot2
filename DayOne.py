import sqlite3
import os

def get_connection():
    """连接到 SQLite 数据库"""
    os.makedirs("data" , exist_ok=True)
    conn = sqlite3.connect("data/notes.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    """初始化数据库"""
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)

class NoteManager:
    def __init__(self , conn):
        """初始化 NoteManager 类"""
        self.conn = conn
        #让查询结果以列名返回

    @staticmethod
    def _row_to_dict(row):
        """将数据库行转换为字典"""
        return {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"]
        }

    def add(self , title , content):
        """添加一条笔记"""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO notes (title , content) VALUES (? , ?)" , 
                (title , content)
            )
            note_id = cur.lastrowid
            return {"id": note_id , "title": title , "content": content}

    def list_all(self):
        """返回所有笔记"""
        with self.conn:
            cur = self.conn.execute("SELECT id , title , content FROM notes")
            return [self._row_to_dict(row) for row in cur.fetchall()]

    def search(self , keyword):
        """返回匹配的笔记"""
        with self.conn:
            cur = self.conn.execute("SELECT id , title , content FROM notes WHERE title LIKE ? OR content LIKE ?", (f'%{keyword}%', f'%{keyword}%'))
            return [self._row_to_dict(row) for row in cur.fetchall()]

    def delete(self , note_id):
        """删除一条笔记"""
        with self.conn:
            cur = self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cur.rowcount > 0

    def get(self , note_id):
        """获取一条笔记"""
        cur = self.conn.execute("SELECT id , title , content FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()
        return self._row_to_dict(row) if row else None


if __name__ == "__main__":
    conn = get_connection()
    init_db(conn)
    manager = NoteManager(conn)
    while True:
        try:
            print("=============================================")
            print("输入'add'来执行添加笔记操作")
            print("输入'list'来查看所有笔记")
            print("输入'search'来搜索笔记")
            print("输入'delete'来删除笔记")
            user_input = input("请输入你想要执行的命令，或者输入 'quit' 退出程序。 ")
            if user_input.lower() == 'quit':
                print("退出程序。")
                break
            elif user_input.lower() == 'add':
                title = input("请输入笔记标题: ")
                content = input("请输入笔记内容: ")
                print(manager.add(title, content))

            elif user_input.lower() == 'list':
                print(manager.list_all())

            elif user_input.lower() == 'search':
                keyword = input("请输入搜索关键词: ").strip()
                if not keyword:
                    print("搜索关键词不能为空。")
                else:
                    print(manager.search(keyword))

            elif user_input.lower() == 'delete':
                try:
                    note_id = int(input("请输入要删除的笔记 ID: "))
                    print(manager.delete(note_id))
                except ValueError:
                    print("请输入有效的数字 ID。")

            else:
                print("无效的命令，请输入 'add'  'list' 'search' 或 'delete'，或者输入 'quit' 退出程序。")
        except Exception as e:
            print(f"An error occurred: {e}")

