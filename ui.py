import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"
FAV_URL = "http://127.0.0.1:8000/favorites"  

st.title("Chef Assistant")

with st.sidebar:
    st.header("Favorites")
    st.button("Refresh")    # clicking any button reruns the script, which reloads the list
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
                r = requests.delete(f"{FAV_URL}/{f["id"]}", timeout=10)   # blank
                r.raise_for_status()
            except requests.RequestException:
                st.error("Couldn't delete that one.")
            else:
                st.rerun()

# Things that must survive reruns
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

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
        # turns 4xx/5xx replies into exceptions
        response.raise_for_status()      
        data = response.json()
    except requests.RequestException:
        st.error("Server is currently experiencing some issues.")   
        # end this run so nothing below executes              
        st.stop()                        

    st.session_state.session_id = data["session_id"]

    reply = data["reply"]
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.rerun()                     