import streamlit as st
import requests

st.title("🤖 AI Q&A Chatbot")


if "messages" not in st.session_state:
    st.session_state.messages = []


# Show previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# User input
user_message = st.chat_input("Ask me anything...")


if user_message:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.write(user_message)


    # Send the new question to FastAPI
    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={
            "question": user_message
        }
    )


    data = response.json()

    answer = data["answer"]


    # Save AI response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)

