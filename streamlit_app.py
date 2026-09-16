"""KnowledgePilot 的网页界面。

运行前必须先启动后端 API：
    uvicorn api:app --reload
然后另开一个终端跑本文件：
    streamlit run streamlit_app.py
浏览器会自动打开 http://localhost:8501
"""

import streamlit as st
import requests

# 后端 API 的地址（配置项：后端换地方，只改这一行）
API = "http://127.0.0.1:8000"

st.set_page_config(page_title="KnowledgePilot", layout="centered")
st.title("KnowledgePilot 知识库")

# 三个标签页：浏览 / 新增 / 搜索
tab_list, tab_add, tab_search = st.tabs(["浏览", "新增", "搜索"])


# ---------- 浏览 ----------
with tab_list:
    st.subheader("全部笔记")

    try:
        resp = requests.get(f"{API}/notes", timeout=5)
        resp.raise_for_status()
        notes = resp.json()
    except requests.RequestException as e:
        st.error(f"连接后端失败，确认后端已启动：{e}")
        notes = []

    if not notes:
        st.info("还没有笔记。")
    else:
        for note in notes:
            # 用 expander 折叠，点开才看到内容
            with st.expander(f"#{note['id']}  {note['title']}"):
                st.write(note["content"])
                # key 必须唯一，否则多个删除按钮会互相干扰
                if st.button("删除", key=f"del_{note['id']}"):
                    r = requests.delete(f"{API}/notes/{note['id']}", timeout=5)
                    if r.status_code == 200:
                        st.success("已删除")
                        st.rerun()          # 重跑脚本，让列表刷新
                    else:
                        st.error(f"删除失败：{r.status_code}")


# ---------- 新增 ----------
with tab_add:
    st.subheader("新增笔记")
    title = st.text_input("标题")
    content = st.text_area("内容")

    if st.button("保存"):
        if not title.strip():
            st.warning("标题不能为空。")
        else:
            r = requests.post(
                f"{API}/notes",
                json={"title": title, "content": content},
                timeout=5,
            )
            if r.status_code == 201:
                st.success(f"已保存，ID = {r.json()['id']}")
            else:
                st.error(f"保存失败：{r.status_code}  {r.text}")


# ---------- 搜索 ----------
with tab_search:
    st.subheader("搜索笔记")
    keyword = st.text_input("关键词")

    if keyword:
        r = requests.get(
            f"{API}/notes/search", params={"keyword": keyword}, timeout=5
        )
        results = r.json()
        if not results:
            st.info("没有匹配的笔记。")
        for note in results:
            st.markdown(f"**#{note['id']}  {note['title']}**")
            st.write(note["content"])
            st.divider()
