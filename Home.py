import streamlit as st
import os
from dotenv import load_dotenv
from Narelle import Narelle
import pprint

# Load environment variables from the .env file
load_dotenv()

# Initialise chatbot
chatbot = Narelle()

# Set up page
st.set_page_config(
    page_title="AskNarelle - Your friendly course assistant", page_icon="🙋‍♀️"
)
st.title(":woman-raising-hand: Ask Narelle")
st.write(f"For queries related to {os.environ.get('COURSE_NAME')}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_avatars = {
    "ai": "imgs/ai_avatar.jpg",
    "user": {
        "Male": "imgs/male_user_avatar.jpg",
        "Female": "imgs/female_user_avatar.jpg",
    },
}

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Accept user input
if prompt := st.chat_input("Ask Narelle a question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # update backend's chat history
    chatbot.set_chat_history(chat_history=st.session_state.messages)

    # Display user message in chat message container
    with st.chat_message("user"):
        st.write(prompt)

    # Display chatbot message
    with st.chat_message("assistant"):
        response = chatbot.answer_this(query=prompt)["chatbot_response"]

        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # update backend's chat history
    chatbot.set_chat_history(chat_history=st.session_state.messages)

