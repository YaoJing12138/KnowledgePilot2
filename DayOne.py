import json

class NoteManager:
    def __init__(self , filepath = "notes.json"):
        """初始化 NoteManager 类"""
        self.filepath = filepath
        self.notes = self._loaded()
        self.next_id = max([note['id'] for note in self.notes], default=0) + 1 if self.notes else 1

    def _loaded(self):
        try:
            with open(self.filepath , "r" , encoding="utf-8") as f:
                notes = json.load(f)
                return notes
        except FileNotFoundError: #空笔记
            return []
        except json.JSONDecodeError:#JSON解码错误
            return []

    def _save(self):
        with open(self.filepath , "w" , encoding="utf-8") as f:
            json.dump(self.notes , f , ensure_ascii=False , indent=4)

    def add(self , title , content):
        """添加一条笔记"""
        note = {
            "id": self.next_id,
            "title": title,
            "content": content
        }
        self.notes.append(note)
        self._save()
        self.next_id += 1
        print(f"笔记 '{title}' 已添加。")

    def list_all(self):
        """列出所有笔记"""
        if self.notes:
            print("所有笔记:")
            self.print_notes()
        else:
            print("没有笔记可显示。")

    def search(self , keyword):
        """搜索笔记"""
        found_notes = [note for note in self.notes if keyword.lower() in note['title'].lower() or keyword.lower() in note['content'].lower()]
        if found_notes:
            print("搜索结果:")
            self.print_notes(found_notes)
        else:
            print("没有找到匹配的笔记。")

    def delete(self , note_id):
        """删除一条笔记"""
        if not any(note['id'] == note_id for note in self.notes):
            print(f"未找到 ID 为 {note_id} 的笔记。")
            return False

        self.notes = [note for note in self.notes if note['id'] != note_id]
        self._save()
        print(f"笔记 ID {note_id} 已删除。")
        return True

    def print_notes(self , notes = None):
        """打印笔记列表"""
        if notes is None:
            notes = self.notes
        for note in notes:
            print(f"ID: {note['id']}, 标题: {note['title']}, 内容: {note['content']}")

if __name__ == "__main__":
    manager = NoteManager()
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
                manager.add(title, content)

            elif user_input.lower() == 'list':
                manager.list_all()

            elif user_input.lower() == 'search':
                keyword = input("请输入搜索关键词: ").strip()
                if not keyword:
                    print("搜索关键词不能为空。")
                else:
                    manager.search(keyword)

            elif user_input.lower() == 'delete':
                try:
                    note_id = int(input("请输入要删除的笔记 ID: "))
                    manager.delete(note_id)
                except ValueError:
                    print("请输入有效的数字 ID。")

            else:
                print("无效的命令，请输入 'add'  'list' 'search' 或 'delete'，或者输入 'quit' 退出程序。")
        except Exception as e:
            print(f"An error occurred: {e}")

