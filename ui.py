import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"

st.title("Chef Assistant")

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

    response = requests.post(
        API_URL,
        json={"message": user_input, "session_id": st.session_state.session_id},  
        timeout=90,
    )
    data = response.json()

    st.session_state.session_id = data["session_id"]             

    reply = data["reply"]
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)