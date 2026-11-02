import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"
FAV_URL = "http://127.0.0.1:8000/favorites"
HIST_URL = "http://127.0.0.1:8000/history"
CONV_URL = "http://127.0.0.1:8000/conversations"

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
        label = ("> " if sid == st.session_state.session_id else "") + c["title"]
        if st.button(label, key=f"chat_{sid}"):
            st.session_state.session_id = sid
            st.session_state.messages = load_history(sid)
            st.query_params["session"] = sid
            st.rerun()

    st.header("Favorites")
    st.button("Refresh")
    try:
        favs = requests.get(FAV_URL, timeout=10).json()
    except requests.RequestException:
        favs = []
        st.caption("Can't reach the server.")

    for f in favs:
        col_title, col_btn = st.columns([4, 1])
        col_title.write(f"{f['id']}. {f['title']}")
        if col_btn.button("x", key=f"dSel_{f['id']}"):
            try:
                r = requests.delete(f"{FAV_URL}/{f['id']}", timeout=10)
                r.raise_for_status()
            except requests.RequestException:
                st.error("Couldn't delete that one.")
            else:
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
            API_URL,
            json={"message": user_input, "session_id": st.session_state.session_id},
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        st.error("Server is currently experiencing some issues.")
        st.stop()

    st.session_state.session_id = data["session_id"]
    st.query_params["session"] = st.session_state.session_id

    reply = data["reply"]
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()