import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"
FAV_URL = "http://127.0.0.1:8000/favorites"
HIST_URL = "http://127.0.0.1:8000/history"
CONV_URL = "http://127.0.0.1:8000/conversations"
STREAM_URL = "http://127.0.0.1:8000/chat/stream"

def load_history(session_id):
    try:
        r = requests.get(f"{HIST_URL}/{session_id}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return []

st.title("Chef Assistant")

# Things that must survive reruns (must come BEFORE the sidebar)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = st.query_params.get("session")
    if st.session_state.session_id:
        st.session_state.messages = load_history(st.session_state.session_id)
if "pending_delete" not in st.session_state:
    st.session_state.pending_delete = None

with st.sidebar:
    if st.button("New chat"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.query_params.clear()
        st.rerun()

    st.header("Chats")
    try:
        convs = requests.get(CONV_URL, timeout=10).json()
    except requests.RequestException:
        convs = []

    for c in convs:
        sid = c["session_id"]
        col_chat, col_del = st.columns([5, 1])
        label = ("> " if sid == st.session_state.session_id else "") + c["title"]
        if col_chat.button(label, key=f"chat_{sid}"):
            st.session_state.session_id = sid
            st.session_state.messages = load_history(sid)
            st.query_params["session"] = sid
            st.rerun()
        if col_del.button("x", key=f"delchat_{sid}"):
            try:
                r = requests.delete(f"{CONV_URL}/{sid}", timeout=10)
                r.raise_for_status()
            except requests.RequestException:
                st.error("Couldn't delete that chat.")
            else:
                if sid == st.session_state.session_id:
                    st.session_state.messages = []
                    st.session_state.session_id = None
                    st.query_params.clear()
                st.rerun()

    st.header("Favorites")
    st.button("Refresh")
    try:
        favs = requests.get(FAV_URL, timeout=10).json()
    except requests.RequestException:
        favs = []
        st.caption("Can't reach the server.")

    for f in favs:
        marker = ("fav", f["id"])
        if st.session_state.pending_delete == marker:               
            st.write(f"Delete \"{f['title']}\"?")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Yes", key=f"yes_fav_{f['id']}"):
                try:
                    r = requests.delete(f"{FAV_URL}/{f['id']}", timeout=10)
                    r.raise_for_status()
                except requests.RequestException:
                    st.error("Couldn't delete that one.")
                else:
                    st.session_state.pending_delete = None         
                    st.rerun()
            if col_no.button("Cancel", key=f"no_fav_{f['id']}"):
                st.session_state.pending_delete = None            
                st.rerun()
        else:
            col_title, col_btn = st.columns([4, 1])
            col_title.write(f["title"])
            if col_btn.button("x", key=f"dSel_{f['id']}"):
                st.session_state.pending_delete = marker
                st.rerun()

# Redraw the conversation so far
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("What are we cooking?")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post(
            STREAM_URL,
            json={"message": user_input, "session_id": st.session_state.session_id},
            stream=True,
            timeout=90,
        )
        response.raise_for_status()
    except requests.RequestException:
        st.error("Server is currently experiencing some issues.")
        st.stop()

    response.encoding = "utf-8"
    st.session_state.session_id = response.headers["X-Session-Id"]  
    st.query_params["session"] = st.session_state.session_id

    with st.chat_message("assistant"):
        reply = st.write_stream(response.iter_content(chunk_size=None, decode_unicode=True))                        

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()